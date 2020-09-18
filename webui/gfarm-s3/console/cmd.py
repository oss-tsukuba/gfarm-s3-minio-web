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
    GFARM_S3_BIN = "/usr/local/bin"
    args = [action, username, passwd]
    if authenticated is not None:
        args = ["--authenticated", authenticated] + args
    if bucket is not None:
        args = ["--bucket", bucket] + args
    gfarm_s3_login_bin = os.path.join(GFARM_S3_BIN, "gfarm-s3-login")
    return Popen([gfarm_s3_login_bin] + args, stdin = stdin, stdout = PIPE, stderr = PIPE, env = {})

def cmd(action, username, passwd, authenticated = None):
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
    result = json.loads(stdout.decode().strip())
    if "expiration_date" in result.keys():
        result["expiration_date_calendar_datetime"] = time.ctime(result["expiration_date"])
    return result

def get_bucket_list(username):
    p = gfarm_s3_login("gfls", username, "", authenticated = "unspecified")
    stdout, stderr = p.communicate()
    p.wait()
    return split_lines(stdout.decode())

def get_bucket_acl(username, bucket):
    p = gfarm_s3_login("gfgetfacl", username, "", authenticated = "unspecified", bucket = bucket)
    stdout, stderr = p.communicate()
    p.wait()
    #logger.debug("GET_BUCKET_ACL: [{}]".format(stdout.decode() + "\n"))
    return split_lines(stdout.decode())

def need_default(s):
    return (s.startswith("group:") or s.startswith("user:")) and ("::" not in s)

def rewrite_any(s):
    if s.startswith("group::"):
        return "group::---"
    if s.startswith("other::"):
        return "other::---"
    return s

def fix_acl(acl):
    acl = [rewrite_any(e) for e in acl]
    default = ["default:" + e for e in acl if need_default(e)]
    return acl + default

def set_bucket_acl(username, bucket, acl_1_string, acl_2):
    acl = "\n".join(fix_acl(split_lines(acl_1_string) + acl_2)) + "\n"
    logger.debug("ACL_FIXED: [{}]".format(acl))
    p = gfarm_s3_login("gfsetfacl", username, "", authenticated = "unspecified", bucket = bucket, stdin = PIPE)
    stdout, stderr = p.communicate(input = acl.encode())
    p.wait()
    return stdout.decode()

def get_group_list(username):
    p = gfarm_s3_login("gfgroup", username, "", authenticated = "unspecified")
    stdout, stderr = p.communicate()
    p.wait()
    return split_lines(stdout.decode())

def get_user_list(username):
    p = gfarm_s3_login("gfuser", username, "", authenticated = "unspecified")
    stdout, stderr = p.communicate()
    p.wait()
    return split_lines(stdout.decode())

def split_lines(s):
    return [e.strip() for e in s.split('\n') if e.strip() != ""]

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
