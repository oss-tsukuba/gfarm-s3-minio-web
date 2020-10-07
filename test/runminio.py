import getopt
import os
import pwd
from subprocess import Popen, PIPE, DEVNULL
import sys

def usage():
    sys.stderr.write(""
        "usage: {} \n"
        "        -r gfarm_shared_dir  | --gfarm_shared_dir=gfarm_shared_dir\n"
        "        -v shared_virtual_name      | --shared_virtual_name=shared_virtual_name\n"
        "        -a address         | --address=address\n"
        "        -k access_key      | --access_key=access_key\n"
        "        -K secret_key      | --secret_key=secret_key\n"
        .format(__file__))
    sys.exit(2)

def runminio():
    GfarmS3_Gfarm_Shared_Dir = "/home/hp120273/hpci005858/tmp/nas1"
    GfarmS3_Gfarm_Shared_Virtual_Name = "sss"
    minioAddress = "127.0.0.1:9001"
    access_key = "K4XcKzocrUhrnCAKrx2Z"
    secret_key = "39e+URNfFv/CCgs4bYcBMusR7ngMLOxEf6cpXWpB"
    GfarmS3_Cache_Basedir = "/mnt/data/tmp"
    GfarmS3_Cache_Size_MB = "128"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "r:s:a:k:K", 
            ["gfarm_shared_dir=", "shared_virtual_name=", "address=", "access_key=", "secret_key="])
    except getopt.GetoptError as err:
        sys.stderr.write("{}\n".format(err))
        usage()

    for opt, optarg in opts:
        if opt in ("-r", "--gfarm_shared_dir"):
            GfarmS3_Gfarm_Shared_Dir = optarg
        elif opt in ("-v", "--shared_virtual_name"):
            GfarmS3_Gfarm_Shared_Virtual_Name = optarg
        elif opt in ("-a", "--address"):
            minioAddress = optarg
        elif opt in ("-k", "--access_key"):
            access_key = optarg
        elif opt in ("-K", "--secret_key"):
            secret_key = optarg
        else:
            assert False, "unhandled option"

    if len(args) != 0:
        sys.stderr.write("argument number: {}\n".format(len(args)))
        usage()

    minio_path = "minio"

    env = {
        "MINIO_ACCESS_KEY": access_key,
        "MINIO_SECRET_KEY": secret_key,
        "GLOBUS_GSSAPI_NAME_COMPATIBILITY": "HYBRID",
        "HOME": os.environ["HOME"],
        "PATH": os.environ["PATH"],
        "TZ": os.environ["TZ"],
        "USER": os.environ["USER"],
        "MINIO_GFARMS3_CACHEDIR": GfarmS3_Cache_Basedir,
        "MINIO_GFARMS3_CACHEDIR_SIZE_MB": GfarmS3_Cache_Size_MB,
	"GFARMS3_PARTFILE_DIGEST": "yes",
    }

    gateway = "nas"
    gateway = "gfarm"
    if gateway == "nas":
        GfarmS3_Gfarm_Shared_Dir = "/home/user1/tmp/gfarms3"
        GfarmS3_Gfarm_Shared_Dir = "/gfarm/hp120273/user1/tmp/gfarms3"
        GfarmS3_Gfarm_Shared_Virtual_Name = ""
        cmd = [minio_path, "gateway", gateway, "--address", minioAddress, GfarmS3_Gfarm_Shared_Dir]
    else:
        cmd = [minio_path, "gateway", gateway, "--address", minioAddress, GfarmS3_Gfarm_Shared_Dir, GfarmS3_Gfarm_Shared_Virtual_Name]

    #print("env = {}".format(env))
    #print("cmd = {}".format(cmd))

    p = Popen(cmd, stdin = DEVNULL, stdout = PIPE, stderr = DEVNULL, env = env)
    #p = Popen(cmd, env = env)
    #p.wait()
    return p

def main():
    runminio()

if __name__ == "__main__":
    main()
