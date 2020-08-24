from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
import json
import os
from subprocess import Popen, PIPE
import sys

def index(request):
    return render(request, "console/index.html", {})

def application(request):
    return render(request, "console/application.html", {})

def launch(request):
    result_s = cmd(request.POST["username"], request.POST["passwd"])
    result = json.loads(result_s)
    request.session["result"] = result 
    return HttpResponseRedirect(reverse("result"))

def result(request):
    #status = get_object_or_404(Status, pk = status_id)
    result = request.session["result"]
    return render(request, "console/result.html", result)

def cmd(username, passwd):
    GFARM_S3_BIN = "/home/user1/work/gfarm-s3-minio-web/bin"
    action = "stop"
    action = "start"
    gfarm_s3_login = os.path.join(GFARM_S3_BIN, "gfarm-s3-login")
    cmd = [gfarm_s3_login , action, username, passwd]
    env = {
        "GLOBUS_GSSAPI_NAME_COMPATIBILITY": "HYBRID",
        #"HOME": os.environ["HOME"],
	"HOME": "/home/user2",
        "PATH": os.environ["PATH"],
        "TZ": os.environ["TZ"],
        #"USER": os.environ["USER"],
        "USER": "user2",
    }
    try:
        p = Popen(cmd, stdout = PIPE, stderr = PIPE, env = env)
        stdout, stderr = p.communicate()
        ret = p.wait()
    except:
        d = {"status": "ERROR 1", "stderr": stderr.decode()}
        return json.dumps(d)
    if ret == 0:
        return stdout.decode().strip()
    else:
        d = {"status": "ERROR 2", "stderr": stderr.decode()}
        return json.dumps(d)
