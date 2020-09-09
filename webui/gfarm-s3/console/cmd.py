import json
import logging
import os
from subprocess import Popen, PIPE
import time

### XXX debug
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def cmd(username, passwd, action):
    #GFARM_S3_BIN = "/home/user1/work/gfarm-s3-minio-web/bin"
    GFARM_S3_BIN = "/usr/local/bin"
    #action = "stop" | "start" | "restart" | "show" | "genkey"
    gfarm_s3_login = os.path.join(GFARM_S3_BIN, "gfarm-s3-login")
    cmd = [gfarm_s3_login, action, username, passwd]

### XXX debug
    sys.stderr.write("CMD = {}\n".format(cmd))
    try:
        p = Popen(cmd, stdout = PIPE, stderr = PIPE, env = {})
    except:
        logger.debug("ERROR 1\n")
        return {"status": "ERROR 1", "reason": "Popen failed"}
    try:
        stdout, stderr = p.communicate()
        ret = p.wait()
    except:
        logger.debug("ERROR 2\nRETCODE = {} STDERR = None\n".format(p.returncode))
        return {"status": "ERROR 2", "reason": "retcode = {}".format(p.returncode)}
    if ret != 0:
        logger.debug("ERROR 3\nSTDERR = {}\n".format(stderr.decode()))
        return {"status": "ERROR 3", "reason": stderr.decode()}
    logger.debug("SUCCESS\nSTDERR = {}\n".format(stderr.decode()))
    result = json.loads(stdout.decode().strip())
    if "expiration_date" in result.keys():
        result["expiration_date_calendar_datetime"] = time.ctime(result["expiration_date"])
    return result

def get_group_list(username):
    cmd = ["sudo", "-u", username, "/usr/local/bin/gfgroup"]

### XXX debug
    sys.stderr.write("CMD = {}\n".format(cmd))

    p = Popen(cmd, stdout = PIPE, stderr = PIPE, env = {})

    stdout, stderr = p.communicate()

    p.wait()

    sys.stderr.write("*SYS*STDOUT = {}\n".format(stdout))
    logger.debug("+LOG+STDOUT = {}\n".format(stdout))

    return stdout.decode().split('\n')
    #return ["a", "b", "c"]

def get_user_list(username):
    cmd = ["sudo", "-u", username, "/usr/local/bin/gfuser"]

### XXX debug
    sys.stderr.write("CMD = {}\n".format(cmd))

    p = Popen(cmd, stdout = PIPE, stderr = PIPE, env = {})

    stdout, stderr = p.communicate()

    p.wait()

    sys.stderr.write("*SYS*STDOUT = {}\n".format(stdout))
    logger.debug("+LOG+STDOUT = {}\n".format(stdout))

    return stdout.decode().split('\n')
    #return ["a", "b", "c"]

def get_bucket_list(username):
    s3rootdir = "/home/hp120273/hpci005858/tmp/gfarms3/hpci005858"
    cmd = ["sudo", "-u", username, "/usr/local/bin/gfls", s3rootdir]

### XXX debug
    sys.stderr.write("CMD = {}\n".format(cmd))

    p = Popen(cmd, stdout = PIPE, stderr = PIPE, env = {})

    stdout, stderr = p.communicate()

    p.wait()

    sys.stderr.write("*SYS*STDOUT = {}\n".format(stdout))
    logger.debug("+LOG+STDOUT = {}\n".format(stdout))

    return stdout.decode().split('\n')
    #return ["a", "b", "c"]

def get_bucket_acl(username, bucket):
    s3rootdir = "/home/hp120273/hpci005858/tmp/gfarms3/hpci005858"
    bucketpath = os.path.join(s3rootdir, bucket)
    cmd = ["sudo", "-u", username, "/usr/local/bin/gfgetfacl", bucketpath]

### XXX debug
    sys.stderr.write("CMD = {}\n".format(cmd))

    p = Popen(cmd, stdout = PIPE, stderr = PIPE, env = {})

    stdout, stderr = p.communicate()

    p.wait()

    sys.stderr.write("*SYS*STDOUT = {}\n".format(stdout))
    logger.debug("+LOG+STDOUT = {}\n".format(stdout))

    return stdout.decode().split('\n')
    #return ["a", "b", "c"]
