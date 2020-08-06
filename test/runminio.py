import getopt
import os
import pwd
from subprocess import Popen
import sys

def usage():
    sys.stderr.write(""
        "usage: {} \n"
        "        -r bucket_rootdir  | --bucket_rootdir=bucket_rootdir\n"
        "        -s shared_dir      | --shared_dir=shared_dir\n"
        "        -a address         | --address=address\n"
        "        -k access_key      | --access_key=access_key\n"
        "        -K secret_key      | --secret_key=secret_key\n"
        .format(__file__))
    sys.exit(2)

def runminio():
    GfarmS3_Gfarm_Bucket_Rootdir = "/home/hp120273/hpci005858/tmp/nas1"
    GfarmS3_Gfarm_Shared_Dir = "sss"
    minioAddress = "127.0.0.1:9001"
    access_key = "K4XcKzocrUhrnCAKrx2Z"
    secret_key = "39e+URNfFv/CCgs4bYcBMusR7ngMLOxEf6cpXWpB"
    GfarmS3_Cache_Basedir = ""
    GfarmS3_Cache_Size_MB = ""

    try:
        opts, args = getopt.getopt(sys.argv[1:], "r:s:a:k:K", 
            ["bucket_rootdir=", "shared_dir=", "address=", "access_key=", "secret_key="])
    except getopt.GetoptError as err:
        sys.stderr.write("{}\n".format(err))
        usage()

    for opt, optarg in opts:
        if opt in ("-r", "--bucket_rootdir"):
            GfarmS3_Gfarm_Bucket_Rootdir = optarg
        elif opt in ("-s", "--shared_dir"):
            GfarmS3_Gfarm_Shared_Dir = optarg
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
        #"MINIO_GFARMS3_CACHEDIR": GfarmS3_Cache_Basedir,
        #"MINIO_GFARMS3_CACHEDIR_SIZE_MB": GfarmS3_Cache_Size_MB,
    }

    cmd = [minio_path, "gateway", "gfarm", "--address", minioAddress, GfarmS3_Gfarm_Bucket_Rootdir, GfarmS3_Gfarm_Shared_Dir]

    print("env = {}".format(env))
    print("cmd = {}".format(cmd))

    p = Popen(cmd, env = env)
    #p.wait()

def main():
    runminio()

if __name__ == "__main__":
    main()
