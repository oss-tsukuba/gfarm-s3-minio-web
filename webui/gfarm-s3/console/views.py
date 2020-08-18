import os
import sys
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Status
from django.utils import timezone
from subprocess import Popen, PIPE

def index(request):
    return render(request, 'console/index.html', {})

def application(request):
    return render(request, 'console/application.html', {})

def launch(request):
    result = cmd(request.POST['id'], request.POST['passwd'])
    status = Status(username_text = result,
                    launch_date = timezone.now())
    status.save()
    return HttpResponseRedirect(reverse('result', args = (status.id,)))

def result(request, status_id):
    status = get_object_or_404(Status, pk = status_id)
    return render(request, 'console/result.html', {'result_string': status.username_text})

def cmd(id, passwd):
    GFARM_S3_BIN = "/home/user1/work/gfarm-s3-minio-web/bin"
    action = "stop"
    action = "start"
    gfarm_s3_login = os.path.join(GFARM_S3_BIN, "gfarm-s3-login")
    cmd = [gfarm_s3_login , action, id, passwd]
    env = {
        "GLOBUS_GSSAPI_NAME_COMPATIBILITY": "HYBRID",
        "HOME": os.environ["HOME"],
        "PATH": os.environ["PATH"],
        "TZ": os.environ["TZ"],
        "USER": os.environ["USER"],
    }
    try:
        sys.stderr.write("cmd = {}\n".format(cmd))
        p = Popen(cmd, stdout = PIPE, stderr = PIPE, env = env)
        stdout, stderr = p.communicate()
        ret = p.wait()
    except:
        return "ERROR 1 {}".format(stderr)
    if ret == 0:
        return stdout.decode().strip()
    else:
        return "ERROR 2 {}".format(stderr)
