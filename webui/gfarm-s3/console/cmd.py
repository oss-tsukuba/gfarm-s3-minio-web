import json
import logging
import os
from subprocess import Popen, PIPE
import time
import urllib.parse

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
    #logger.debug("CMD = {}".format(cmd))

    try:
        p = Popen(cmd, stdout = PIPE, stderr = PIPE, env = {})
    except:
        logger.debug("ERROR 1")
        return {"status": "ERROR 1", "reason": "Popen failed"}
    try:
        stdout, stderr = p.communicate()
        ret = p.wait()
    except:
        logger.debug("ERROR 2 --- RETCODE = {} STDERR = None".format(p.returncode))
        return {"status": "ERROR 2", "reason": "retcode = {}".format(p.returncode)}
    if ret != 0:
        logger.debug("ERROR 3 --- RETVAL = {} --- STDERR = {}".format(ret, stderr.decode()))
        return {"status": "ERROR 3", "reason": stderr.decode()}
    logger.debug("SUCCESS --- STDERR = {}".format(stderr.decode()))
    result = json.loads(stdout.decode().strip())
    if "expiration_date" in result.keys():
        result["expiration_date_calendar_datetime"] = time.ctime(result["expiration_date"])
    return result

def get_group_list(username):
    cmd = ["sudo", "-u", username, "/usr/local/bin/gfgroup"]

### XXX debug
    #logger.debug("CMD = {}".format(cmd))

    p = Popen(cmd, stdout = PIPE, stderr = PIPE, env = {})

    stdout, stderr = p.communicate()

    p.wait()

### XXX debug
    #logger.debug("STDOUT = {}".format(stdout))

    return stdout.decode().split('\n')

def get_user_list(username):
    cmd = ["sudo", "-u", username, "/usr/local/bin/gfuser", "-l"]

### XXX debug
    #logger.debug("CMD = {}".format(cmd))

    p = Popen(cmd, stdout = PIPE, stderr = PIPE, env = {})

    stdout, stderr = p.communicate()

    p.wait()

### XXX debug
    #logger.debug("STDOUT = {}".format(stdout))

    return stdout.decode().split('\n')
    #return ["a", "b", "c"]

def get_bucket_list(username):
    s3rootdir = "/home/hp120273/hpci005858/tmp/gfarms3/hpci005858"
    cmd = ["sudo", "-u", username, "/usr/local/bin/gfls", s3rootdir]

### XXX debug
    #logger.debug("CMD = {}".format(cmd))

    p = Popen(cmd, stdout = PIPE, stderr = PIPE, env = {})

    stdout, stderr = p.communicate()

    p.wait()

### XXX debug
    #logger.debug("STDOUT = {}".format(stdout))

    return stdout.decode().split('\n')

def get_bucket_acl(username, bucket):
    s3rootdir = "/home/hp120273/hpci005858/tmp/gfarms3/hpci005858"
    bucketpath = os.path.join(s3rootdir, bucket)
    cmd = ["sudo", "-u", username, "/usr/local/bin/gfgetfacl", bucketpath]

### XXX debug
    #logger.debug("CMD = {}".format(cmd))

    p = Popen(cmd, stdout = PIPE, stderr = PIPE, env = {})

    stdout, stderr = p.communicate()

    p.wait()

### XXX debug
    #logger.debug("STDOUT = {}".format(stdout))

    return stdout.decode().split('\n')

def pretty_name(s):
    ss = s.split(':')
    uu = ss[1].split('[')
    t = urllib.parse.unquote(uu[0]) + "(" + ss[0] + ")"
    return t

def user_id(s):
    ss = s.split(':')
    return ss[0]

def get_users_groups_list(username):
    users = [e for e in get_user_list(username) if e != ""]
    users.sort()
    users = [{"id": "user:" + user_id(e), "text": pretty_name(e)} for e in users]

    groups = [e for e in get_group_list(username) if e != ""]
    groups.sort()
    groups = [{"id": "group:" + e, "text": e} for e in groups]

    return (groups, users)
