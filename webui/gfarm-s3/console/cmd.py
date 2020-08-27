import json
import logging
import os
from subprocess import Popen, PIPE
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def cmd(username, passwd, action):
    GFARM_S3_BIN = "/home/user1/work/gfarm-s3-minio-web/bin"
    #action = "stop" | "start" | "restart" | "show" | "genkey"
    gfarm_s3_login = os.path.join(GFARM_S3_BIN, "gfarm-s3-login")
    cmd = [gfarm_s3_login, action, username, passwd]
    env = {
        #"GLOBUS_GSSAPI_NAME_COMPATIBILITY": "HYBRID",
        #"HOME": os.environ["HOME"],
	#"HOME": "/home/user2",
        #"PATH": os.environ["PATH"],
        #"TZ": os.environ["TZ"],
        #"USER": os.environ["USER"],
        #"USER": "user2",
    }
    try:
        p = Popen(cmd, stdout = PIPE, stderr = PIPE, env = env)
        stdout, stderr = p.communicate()
        ret = p.wait()
    except:
        logger.debug("ERROR 1\nSTDERR = {}\n".format(stderr.decode()))
        return {"status": "ERROR 1", "reason": stderr.decode()}
    if ret == 0:
        logger.debug("SUCCESS\nSTDERR = {}\n".format(stderr.decode()))
        result = json.loads(stdout.decode().strip())
        if "expiration_date" in result.keys():
            result["expiration_date"] = time.ctime(result["expiration_date"])
        return result
    else:
        logger.debug("ERROR 2\nSTDERR = {}\n".format(stderr.decode()))
        return {"status": "ERROR 2", "reason": stderr.decode()}
