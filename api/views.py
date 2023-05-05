import subprocess
from django.http import HttpResponse

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse


def run_script(request):
    script_path = 'api/script.sh'
    result = subprocess.run(['sh', script_path], stdout=subprocess.PIPE)
    return HttpResponse(result.stdout)


def amira(request):
    return render(request, 'home.html')



def create_instance(request):
    if request.method == 'POST':
        instance_name = request.POST.get('instance_name', 'my-instance')
        script_path = 'api/output.sh'
        process = subprocess.Popen([script_path, instance_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        return render(request, 'output.html', {'output': output.decode('utf-8'), 'error': error.decode('utf-8')})
    else:
        return render(request, 'execute.html')
    





def delete_instance(request):
    if request.method == 'POST':
        instance_name = request.POST.get('instance_name', 'my-instance')
        script_path = 'api/delete_ec2_instance.sh'
        process = subprocess.Popen([script_path, instance_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        return render(request, 'output.html', {'output': output.decode('utf-8'), 'error': error.decode('utf-8')})
    else:
        return render(request, 'delete_ec2_instance.html')
    


import boto3



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
