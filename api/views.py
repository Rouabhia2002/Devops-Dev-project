import subprocess
from django.http import HttpResponse

from django.conf import settings
from django.shortcuts import render


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