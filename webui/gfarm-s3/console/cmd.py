import json
import locale
import logging
import os
from subprocess import Popen, PIPE
import time
import threading
import urllib.parse

from contextlib import contextmanager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

def gfarm_s3_login(action, username, passwd, stdin = None, authenticated = None, bucket = None, remote_addr = None):
    GFARM_S3_BIN = "/usr/local/bin"
    args = [action, username, passwd]
    if authenticated is not None:
        args = ["--authenticated", authenticated] + args
    if bucket is not None:
        args = ["--bucket", bucket] + args
    if remote_addr is not None:
        args = ["--remote_addr", remote_addr] + args
    gfarm_s3_login_bin = os.path.join(GFARM_S3_BIN, "gfarm-s3-login")
    return Popen([gfarm_s3_login_bin] + args, stdin = stdin, stdout = PIPE, stderr = PIPE, env = {})

def cmd(action, username, passwd, authenticated = None, remote_addr = None, lang = None):
    try:
        p = gfarm_s3_login(action, username, passwd, authenticated = authenticated, remote_addr = remote_addr)
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
        result["expiration_date_calendar_datetime"] = myctime(result["expiration_date"], lang)
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
    logger.debug("GET_BUCKET_ACL: [{}]".format(stdout.decode() + "\n"))
    return split_lines(stdout.decode())

def need_default(s):
    return (s.startswith("group:") or s.startswith("user:")) and ("::" not in s)

def rewrite_any(s):
    if s.startswith("group::"):
        return "group::---"
    if s.startswith("other::"):
        return "other::---"
    return s

def is_fixed_entry(s):
    if s.startswith("#") or s.startswith("default:"):
        return False
    return "::" in s or s.startswith("mask:")

#def is_debug_entry(s):
#    return "77777" in s or "OTHER" in s

def fix_acl_1(acl):
    acl = [rewrite_any(e) for e in acl if is_fixed_entry(e)]
    return acl

def fix_acl_2(acl):
    #acl = [e for e in acl if not is_debug_entry(e)]
    logger.debug("acl: {}".format(acl))
    oth = [e for e in acl if e.startswith("gfarms3webui:OTHER:")][0]
    grp = [e for e in acl if e.startswith("gfarms3webui:GROUP:")][0]
    acl = [e for e in acl if not e.startswith("gfarms3webui:")]
    logger.debug("acl: {}".format(acl))
    logger.debug("oth: {}".format(oth))
    default = ["default:" + e for e in acl if need_default(e)]
    acl = acl + grp_to_aclentry(grp)
    acl = acl + oth_to_aclentry(oth)

    return acl + default

def grp_to_aclentry(grp):
    perm = grp.split(':')[2]
    return go_aclentry("group", perm)

def oth_to_aclentry(oth):
    perm = oth.split(':')[2]
    return go_aclentry("other", perm)

def go_aclentry(object, perm):
    if perm == "rwx":
        return [object + "::rwx", "default:" + object + "::rwx"]
    elif perm == "r-x":
        return [object + "::r-x", "default:" + object + "::r-x"]
    else:
        return [object + "::---", "default:" + object + "::---"]

def set_bucket_acl(username, bucket, acl_1, acl_2):
    logger.debug("bucket: {}".format(bucket))
    logger.debug("acl_1: {}".format(acl_1))
    logger.debug("acl_2: {}".format(acl_2))
    acl = "\n".join(fix_acl_1(acl_1) + fix_acl_2(acl_2)) + "\n"
    logger.debug("acl_fixed: {}".format(acl))
    p = gfarm_s3_login("gfsetfacl", username, "", authenticated = "unspecified", bucket = bucket, stdin = PIPE)
    stdout, stderr = p.communicate(input = acl.encode())
### ignore error for now
#    if p.wait() != 0:
#        return stderr.decode()
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

LOCALE_LOCK = threading.Lock()

@contextmanager
def setlocale(name):
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)

def myctime(sec, lang):
    lt = time.localtime(sec)
    if lang == "ja":
        with setlocale("ja_JP.UTF-8"):
            return time.strftime("%Y年 %b %-d日  (%a) %H:%M:%S +%Z", lt)
    else:
        with setlocale("en_US.UTF-8"):
            return time.strftime("%a, %d %b %Y %H:%M:%S +%Z", lt)
