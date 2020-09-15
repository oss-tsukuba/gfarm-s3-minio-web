import sys
import time
import filecmp
import os
import boto3
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig

class Mys3client(object):

    def __init__(self):
        self.s3_client = self.gfarms3_client()
    
    def gfarms3_client(self):
        return boto3.client("s3",
            aws_access_key_id = "K4XcKzocrUhrnCAKrx2Z",
            #aws_secret_access_key = "39e+URNfFv/CCgs4bYcBMusR7ngMLOxEf6cpXWpB",
            aws_secret_access_key = "TmXnYAhtjbtA3RHjK1Beu/6rvRJlmPVnOKThaZP0/+nT9XOo",
            endpoint_url = "http://127.0.0.1:9000")
    
    def create_bucket(self, bucket_name):
        try:
            self.s3_client.create_bucket(Bucket = bucket_name)
        except ClientError as e:
            sys.stderr.write("{}".format(e))
            return False
        return True
    
    def list_buckets(self):
        response = self.s3_client.list_buckets()
        return response["Buckets"]
    
    def upload_file(self, file_name, bucket, object_name):
        try:
            response = self.s3_client.upload_file(file_name, bucket, object_name)
        except ClientError as e:
            sys.stderr.write("{}".format(e))
            return False
        return True
    
    def upload_fileobj(self, f, bucket, object_name):
        try:
            response = self.s3_client.upload_fileobj(f, bucket, object_name)
        except ClientError as e:
            sys.stderr.write("{}".format(e))
            return False
        return True
    
    def download_fileobj(self, f, bucket, object_name):
        try:
            response = self.s3_client.download_fileobj(bucket, object_name, f)
        except ClientError as e:
            sys.stderr.write("{}".format(e))
            return False
        return True

def up_down_n_cmp(s3, basename, senddir, bucket, recvdir, flag):
    sendfile = os.path.join(senddir, basename)
    recvfile = os.path.join(recvdir, basename)

    if (flag & 4) != 0:
        now = time.time()
        start = now
        print("@@@ {} upload start {}".format(myformat(start), basename))
        with open(sendfile, "rb") as f:
            s3.upload_fileobj(f, bucket, basename)
        now = time.time()
        print("@@@ {} ({}) upload end {}".format(myformat(now), now - start, basename))

    if (flag & 2) != 0:
        now = time.time()
        start = now
        print("@@@ {} download start {}".format(myformat(start), basename))
        with open(recvfile, "wb") as f:
            s3.download_fileobj(f, bucket, basename)
        now = time.time()
        print("@@@ {} ({}) download end {}".format(myformat(now), now - start, basename))

    if (flag & 1) != 0:
        e = filecmp.cmp(sendfile, recvfile, shallow = False)
        print("compare files: {}".format(e))

def print_buckets(buckets):
    print("Existing buckets:")
    for bucket in buckets:
        print("{}".format(bucket["Name"]))

def createFileM(path, sz, force = False):
    if not force and os.path.isfile(path):
        return
    print("createFileM({}, {})".format(path, sz))
    with open(path, "wb") as f:
       for m in range(sz):
           f.write(os.urandom(1 * 1024 * 1024))

def main():
    s3 = Mys3client()

    source_dir = os.path.expanduser("~/work/tmp/s")
    download_dir = os.path.expanduser("~/work/tmp/r")
    bucket_name = "new"

    e = s3.create_bucket(bucket_name)
    print("create bucket: e = {}".format(e))

#    buckets = s3.list_buckets()
#    print_buckets(buckets)

#    with open("test.jpg", "wb") as f:
#        f.write(os.urandom(1024))
#    up_down_n_cmp(s3, "test.jpg", "new", "/tmp")

    flist = [("7M", 7), ("32M", 32), ("64M", 64)]

    for basename, sz in flist:
        source_file = os.path.join(source_dir, basename)
        createFileM(source_file, sz, True)

    for basename, sz in flist:
        source_file = os.path.join(source_dir, basename)
        up_down_n_cmp(s3, basename, source_dir, bucket_name, download_dir, 4)

    for basename, sz in flist:
        source_file = os.path.join(source_dir, basename)
        up_down_n_cmp(s3, basename, source_dir, bucket_name, download_dir, 2)

    for basename, sz in flist:
        source_file = os.path.join(source_dir, basename)
        up_down_n_cmp(s3, basename, source_dir, bucket_name, download_dir, 1)

    return


    GB = 1024 ** 3
    config = TransferConfig(multipart_threshold = 5)
    s3_client.upload_file("test.jpg", "mybucket", "test.jpg", Config = config)


    #config = TransferConfig(max_concurrency = 5)
    #s3_client.download_file("test.jpg", "mybucket", "test.jpg", Config = config)

    response = s3_client.list_objects(
        Bucket = "mybucket"
        #Prefix = "xx/"
    )

    for content in response["Contents"]:
        print("{}".format(content["Key"]))

def myformat(t):
    i = time.strftime('%Y%m%dT%H%M%S', time.gmtime(t))
    f = (int)((t % 1) * 1000000)
    return "{}.{:06d}Z".format(i, f)

if __name__ == "__main__":
    main()
