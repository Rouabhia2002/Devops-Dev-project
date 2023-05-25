import subprocess
from django.http import HttpResponse

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
import boto3

def run_script(request):
    script_path = 'api/script.sh'
    result = subprocess.run(['sh', script_path], stdout=subprocess.PIPE)
    return HttpResponse(result.stdout)


def amira(request):
    return render(request, 'home.html')




def create_instance(request):
    if request.method == 'POST':
        instance_name = request.POST.get('instance_name', 'my-instance')
        
        # Check if instance_name is empty
        if not instance_name:
            error_message = 'Please provide a valid instance name.'
            return render(request, 'create_instance.html', {'error_message': error_message})
        
        script_path = 'api/create_ec2_instance.sh'
        process = subprocess.Popen([script_path, instance_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        
        return render(request, 'output.html', {'output': output.decode('utf-8'), 'error': error.decode('utf-8')})
    
    else:
        return render(request, 'create_instance.html')

    







def delete_ec2_instance(request):
    if request.method == 'POST':
        instance_id = request.POST.get('instance_id')
        if not instance_id:
            return JsonResponse({'error': 'Instance ID not provided.'}, status=400)
        return render(request, 'confirm_delete.html', {'instance_id': instance_id})
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)


def delete_ec2_instance_confirm(request):
    if request.method == 'POST':
        instance_id = request.POST.get('instance_id')
        try:
            ec2 = boto3.resource('ec2')
            response = ec2.instances.terminate(InstanceIds=[instance_id])
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        return JsonResponse({'message': 'Instance deleted successfully.'})
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)




def get_instance_metrics(request):
    if request.method == 'POST':
        instance_name = request.POST.get('instance_name')

        # First, use Boto3 to retrieve the instance ID from EC2 using the instance name
        ec2 = boto3.resource('ec2')
        instances = ec2.instances.filter(Filters=[{'Name': 'tag:Name', 'Values': [instance_name]}])
        instance_ids = [instance.id for instance in instances]
        if not instance_ids:
            return JsonResponse({'error': f'No instances found with name "{instance_name}"'})

        # If there are multiple instances with the same name, just use the first one
        instance_id = instance_ids[0]

        # Next, use Boto3 to fetch the CPU utilization metrics from CloudWatch
        cloudwatch = boto3.client('cloudwatch')
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime='2022-10-18T23:18:00Z',
            EndTime='2022-10-19T23:18:00Z',
            Period=3600,
            Statistics=['Maximum'],
        )

        # Return the metrics as a JSON response
        datapoints = response.get('Datapoints', [])
        return JsonResponse({'datapoints': datapoints})
    
    return render(request, 'instance_metrics.html')


def list_ec2_instances(request):
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    instance_list = [{'id': instance.id, 'name': instance.tags[0]['Value'] if instance.tags else ''} for instance in instances]

    return render(request, 'list_ec2_instances.html', {'instances': instance_list})




def update_instance_type(request):
    if request.method == 'POST':
        instance_id = request.POST.get('instance_id')
        if not instance_id:
            return JsonResponse({'error': 'Instance ID not provided.'}, status=400)
        ec2_client = boto3.client('ec2')
        instance_types = ec2_client.describe_instance_types()['InstanceTypes']
        return render(request, 'update_instance.html', {'instance_id': instance_id, 'instance_types': instance_types})
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)



def confirm_update_instance(request):
    if request.method == 'POST':
        instance_id = request.POST.get('instance_id')
        new_instance_type = request.POST.get('new_instance_type')

        if not instance_id or not new_instance_type:
            return JsonResponse({'error': 'Instance ID or new instance type not provided.'}, status=400)

        try:
            ec2_client = boto3.client('ec2')

            # Check the compatibility of the new instance type
            instance_info = ec2_client.describe_instances(InstanceIds=[instance_id])
            architecture = instance_info['Reservations'][0]['Instances'][0]['Architecture']
            valid_instance_types = ec2_client.describe_instance_types(
                Filters=[{'Name': 'instance-type', 'Values': [new_instance_type]}]
            )['InstanceTypes']

            if not valid_instance_types or valid_instance_types[0]['ProcessorInfo']['SupportedArchitectures'][0] != architecture:
                return JsonResponse({'error': 'Invalid instance type for the instance architecture.'}, status=400)

            instance_state = instance_info['Reservations'][0]['Instances'][0]['State']['Name']

            if instance_state != 'stopped':
                # Stop the instance
                ec2_client.stop_instances(InstanceIds=[instance_id])
                waiter = ec2_client.get_waiter('instance_stopped')
                waiter.wait(InstanceIds=[instance_id])

            # Modify the instance attribute
            ec2_client.modify_instance_attribute(
                InstanceId=instance_id,
                InstanceType={'Value': new_instance_type}
            )

            if instance_state != 'stopped':
                # Start the instance if it was previously running
                ec2_client.start_instances(InstanceIds=[instance_id])
                waiter = ec2_client.get_waiter('instance_running')
                waiter.wait(InstanceIds=[instance_id])

            return JsonResponse({'message': 'Instance updated successfully.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)



from django.http import JsonResponse
import boto3
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import boto3
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_instance_statistics(request):
    if request.method == 'POST':
        instance_name = request.POST.get('instance_name')

        if not instance_name:
            return JsonResponse({'error': 'Instance name not provided.'}, status=400)

        ec2_client = boto3.client('ec2')

        # Get the instance ID based on the instance name
        response = ec2_client.describe_instances(
            Filters=[{'Name': 'tag:Name', 'Values': [instance_name]}]
        )
        reservations = response['Reservations']

        if not reservations:
            return JsonResponse({'error': 'Instance not found.'}, status=404)

        instance_id = reservations[0]['Instances'][0]['InstanceId']

        cloudwatch_client = boto3.client('cloudwatch')

        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance_id
                },
            ],
            StartTime=datetime.utcnow() - timedelta(minutes=30),
            EndTime=datetime.utcnow(),
            Period=60,
            Statistics=['Average'],
            Unit='Percent'
        )

        statistics = response['Datapoints']
        if statistics:
            average_cpu = statistics[0]['Average']
        else:
            average_cpu = 0.0

        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='NetworkIn',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance_id
                },
            ],
            StartTime=datetime.utcnow() - timedelta(minutes=30),
            EndTime=datetime.utcnow(),
            Period=60,
            Statistics=['Average'],
            Unit='Bytes'
        )

        statistics = response['Datapoints']
        if statistics:
            average_network_in = statistics[0]['Average']
        else:
            average_network_in = 0.0

        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='NetworkOut',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance_id
                },
            ],
            StartTime=datetime.utcnow() - timedelta(minutes=30),
            EndTime=datetime.utcnow(),
            Period=60,
            Statistics=['Average'],
            Unit='Bytes'
        )

        statistics = response['Datapoints']
        if statistics:
            average_network_out = statistics[0]['Average']
        else:
            average_network_out = 0.0

        return JsonResponse({
            'instance_id': instance_id,
            'instance_name': instance_name,
            'average_cpu': average_cpu,
            'average_network_in': average_network_in,
            'average_network_out': average_network_out
        })

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def login(request):
    return render(request, 'api/login.html')


def register(request):
    return render(request, 'api/register.html')



