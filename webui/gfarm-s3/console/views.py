from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
import json
import os
from subprocess import Popen, PIPE
import sys
import time

def debug_print(s):
    with open("/tmp/views.log", "a") as f:
        f.write(s)

def index(request):
    return render(request, "console/index.html", {})

def application(request):
    return render(request, "console/application.html", {})

def launch(request):
    debug_print("{}\n".format(request.POST))
    username = request.POST["username"]
    passwd = request.POST["passwd"]
    action = request.POST["action"]
    debug_print("username = {}\npasswd = {}\naction = {}\n".format(username, passwd, action))
    result = cmd(username, passwd, action)
    debug_print("result = {}\n".format(result))
    request.session["result"] = result 
    return HttpResponseRedirect(reverse("result"))

def result(request):
    #status = get_object_or_404(Status, pk = status_id)
    result = request.session["result"]
    return render(request, "console/result.html", result)

def cmd(username, passwd, action):
    GFARM_S3_BIN = "/home/user1/work/gfarm-s3-minio-web/bin"
    #action = "stop" | "start" | "restart" | "show" | "genkey"
    gfarm_s3_login = os.path.join(GFARM_S3_BIN, "gfarm-s3-login")
    cmd = [gfarm_s3_login, action, username, passwd]
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
        debug_print("ERROR 1\nSTDERR = {}\n".format(stderr.decode()))
        return {"status": "ERROR 1"}
    if ret == 0:
        debug_print("SUCCESS\nSTDERR = {}\n".format(stderr.decode()))
        result = json.loads(stdout.decode().strip())
        if "expiration_date" in result.keys():
            result["expiration_date"] = time.ctime(result["expiration_date"])
        return result
    else:
        debug_print("ERROR 2\nSTDERR = {}\n".format(stderr.decode()))
        return {"status": "ERROR 2"}
