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

def gfarm_s3_login(action, username, passwd, stdin = None, authenticated = None, bucket = None):
### XXX debug
    GFARM_S3_BIN = "/usr/local/bin"
    args = [action, username, passwd]
    if authenticated is not None:
        args = ["--authenticated", authenticated] + args
    if bucket is not None:
        args = ["--bucket", bucket] + args
    gfarm_s3_login_bin = os.path.join(GFARM_S3_BIN, "gfarm-s3-login")
    #logger.debug("BIN = {}".format(gfarm_s3_login_bin))
    #logger.debug("ARGS = {}".format(args))
    return Popen([gfarm_s3_login_bin] + args, stdin = stdin, stdout = PIPE, stderr = PIPE, env = {})

def cmd(action, username, passwd, authenticated = None):
    #GFARM_S3_BIN = "/home/user1/work/gfarm-s3-minio-web/bin"
    #action = "stop" | "start" | "restart" | "show" | "genkey"
    #if authenticated is not None:
        #gfarm_s3_login_args = [action, username, ""]
    #elif passwd is not None:
        #gfarm_s3_login_args = [action, username, passwd]

    try:
        p = gfarm_s3_login(action, username, passwd, authenticated = authenticated)
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
    #logger.debug("SUCCESS --- STDERR = {}".format(stderr.decode()))
    #logger.debug("STDOUT = {}".format(stdout))
    result = json.loads(stdout.decode().strip())
    if "expiration_date" in result.keys():
        result["expiration_date_calendar_datetime"] = time.ctime(result["expiration_date"])
    return result

def get_bucket_list(username):
    ###s3rootdir = "/home/hp120273/hpci005858/tmp/gfarms3/hpci005858"
    ###cmd = ["sudo", "-u", username, "/usr/local/bin/gfls", s3rootdir]

    p = gfarm_s3_login("gfls", username, "", authenticated = "unspecified")

    stdout, stderr = p.communicate()

    p.wait()

### XXX debug
    #logger.debug("STDOUT = {}".format(stdout))

    return [e for e in stdout.decode().split('\n') if e != ""]

def get_bucket_acl(username, bucket):
    ##s3rootdir = "/home/hp120273/hpci005858/tmp/gfarms3/hpci005858"
    ##bucketpath = os.path.join(s3rootdir, bucket)
    ##cmd = ["sudo", "-u", username, "/usr/local/bin/gfgetfacl", bucketpath]

    p = gfarm_s3_login("gfgetfacl", username, "", authenticated = "unspecified", bucket = bucket)

    stdout, stderr = p.communicate()

    p.wait()

### XXX debug
    logger.debug("STDOUT = {}".format(stdout))

    return stdout.decode()

def set_bucket_acl(username, bucket, postdata):
#    logger.debug("SET BUCKET ACL: {} {}".format(username, bucket))
#    logger.debug("SET BUCKET ACL: postdata = {}".format(postdata))
#    for key, value in postdata.items():
#        logger.debug("SET BUCKET ACL: {} = {}".format(key, value))
    v = [postdata[e.replace("opt", "sel")] + ":" + postdata[e] for e in postdata if e.startswith("opt:")]

    acl_1_string = postdata["acl_1_string"]
    acl_2_edited = "\n".join(v)

    #logger.debug("acl_1_string: {}".format(acl_1_string))
    #logger.debug("acl_2_edited: {}".format(acl_2_edited))

    acl_new = acl_1_string + acl_2_edited 

    p = gfarm_s3_login("gfsetfacl", username, "", authenticated = "unspecified", bucket = bucket, stdin = PIPE)

### + "user:hpci001971:rwx\n"

    stdout, stderr = p.communicate(input = acl_new.encode())

    p.wait()

### XXX debug
#    logger.debug("STDOUT = {}".format(stdout))
#    logger.debug("STDERR = {}".format(stderr))

    return stdout.decode()

def get_group_list(username):
    ###cmd = ["sudo", "-u", username, "/usr/local/bin/gfgroup"]
    ###gfarm_s3_login_args = ["--authenticated", authenticated, "gfgroup", username, ""]

    p = gfarm_s3_login("gfgroup", username, "", authenticated = "unspecified")

    stdout, stderr = p.communicate()

    p.wait()

### XXX debug
    #logger.debug("STDOUT = {}".format(stdout))

    return [e for e in stdout.decode().split('\n') if e != ""]

def get_user_list(username):
    ###cmd = ["sudo", "-u", username, "/usr/local/bin/gfuser", "-l"]

    p = gfarm_s3_login("gfuser", username, "", authenticated = "unspecified")

    stdout, stderr = p.communicate()

    p.wait()

### XXX debug
    #logger.debug("STDOUT = {}".format(stdout))

    return [e for e in stdout.decode().split('\n') if e != ""]
    #return ["a", "b", "c"]

def get_groups_users_list(username):
    groups = get_group_list(username)
    groups.sort()
    groups = [{"id": "group:" + e, "text": "group:" + e} for e in groups]

    users = get_user_list(username)
    users.sort()
    users = [{"id": "user:" + user_id(e), "text": "user:" + pretty_name(e)} for e in users]

    return (groups, users)

def user_id(s):
    ss = s.split(':')
    return ss[0]

def pretty_name(s):
    ss = s.split(':')
    uu = ss[1].split('[')
    t = urllib.parse.unquote(uu[0]) + "(" + ss[0] + ")"
    return t
