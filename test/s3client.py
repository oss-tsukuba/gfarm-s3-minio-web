#import random
#import string
import sys
#import tempfile
#import time
#import filecmp
#import os
import boto3
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig

class Mys3client(object):

    def __init__(self):
        self.s3_client = self.gfarms3_client()

    def gfarms3_client(self):
        return boto3.client("s3",
            aws_access_key_id = "K4XcKzocrUhrnCAKrx2Z",
            aws_secret_access_key = "39e+URNfFv/CCgs4bYcBMusR7ngMLOxEf6cpXWpB",
            endpoint_url = "http://127.0.0.1:9001")

    def close_connection(self):
        pass

    def create_bucket(self, bucket_name):
        try:
            self.s3_client.create_bucket(Bucket = bucket_name)
        except ClientError as e:
            return "{}".format(e)
        return None

    def delete_bucket(self, bucket_name):
        try:
            self.s3_client.delete_bucket(Bucket = bucket_name)
        except ClientError as e:
            return "delete_bucket: {} {}".format(bucket_name)
        return None

    def delete_object(self, bucket_name, key):
        try:
            self.s3_client.delete_object(Bucket = bucket_name, Key = key)
        except ClientError as e:
            return "delete_object: {} {} {}".format(bucket_name, key, e)
        return None

    def list_buckets(self):
        response = self.s3_client.list_buckets()
        return response["Buckets"]

    def list_objects(self, bucket):
        response = self.s3_client.list_objects(Bucket = bucket)
        return response["Contents"]

    def upload_file(self, file_name, bucket, key):
        try:
            response = self.s3_client.upload_file(file_name, bucket, key)
        except ClientError as e:
            return "upload_file: {} {} {} {}".format(file_name, bucket, key, e)
        return None

    def upload_fileobj(self, f, bucket, key):
        try:
            response = self.s3_client.upload_fileobj(f, bucket, key)
        except ClientError as e:
            return "upload_fileobj: {} {} {}".format(bucket, key, e)
        return None

    def download_fileobj(self, f, bucket, key):
        try:
            response = self.s3_client.download_fileobj(bucket, key, f)
        except ClientError as e:
            return "download_fileobj: {} {} {}".format(bucket, key, e)
        return None

    def withBucket(self, bucket_name):
        return MyWithClass(self, bucket_name)

class MyWithClass():

    def __init__(self, s3, name):
        self.s3 = s3	# typeof Mys3client
        self.name = name

    def __enter__(self):
        print("enter bucket name = {}".format(self.name))
        self.s3.s3_client.create_bucket(Bucket = self.name)
        return self

    def __exit__(self, type, value, traceback):
        print("exit bucket name = {}".format(self.name))
        self.s3.delete_bucket(self.name)

#def random_s3_name():
#    return ''.join(random.choices(string.ascii_lowercase + string.digits, k = 24))
#
#def send_recv_cmp(s3, sendfile, bucket, key, recvfile):
#
#    with open(sendfile, "rb") as f:
#        if not s3.upload_fileobj(f, bucket, key):
#            return "upload {} => {}/{}".format(sendfile, bucket, key)
#
#    with open(recvfile, "wb") as f:
#        if not s3.download_fileobj(f, bucket, key):
#            return "download {} <= {}/{}".format(recvfile, bucket, key)
#
#    if not filecmp.cmp(sendfile, recvfile, shallow = False):
#        return "mismatch {} {}".format(sendfile, recvfile)
#
#    return None
#
#def up_down_n_cmp_sz(s3, size):
#
#    with tempfile.TemporaryDirectory(dir = ".") as tmpdirname:
#        print("temporary directory {}".format(tmpdirname))
#
#        bucket = random_s3_name()
#        with s3.withBucket(bucket) as b:
#            print("bucket name {}".format(b.name))
#    
#            with tempfile.NamedTemporaryFile(dir = tmpdirname) as sendfile:
#                print("created temporary file: {}".format(sendfile.name))
#        
#                with tempfile.NamedTemporaryFile(dir = tmpdirname) as recvfile:
#                    print("created temporary file: {}".format(recvfile.name))
#        
#                    e = createFileM(sendfile.name, size, force = True)
#                    if e:
#                        return e
#        
#                    key = random_s3_name()
#        
#                    e = send_recv_cmp(s3, sendfile.name, bucket, key, recvfile.name)
#        
#                    d = s3.delete_object(bucket, key)
#                    if d:
#                        e = d
#                    return e
#
#def createFileM(path, sz, force = False):
#    if not force and os.path.isfile(path):
#        return "file exists {}".format(path)
#    print("createFileM({}, {})".format(path, sz))
#    with open(path, "wb") as f:
#       for m in range(sz):
#           f.write(os.urandom(1 * 1024 * 1024))
#    return None

#def up_down_n_cmp(s3, basename, senddir, bucket, recvdir, flag):
#    sendfile = os.path.join(senddir, basename)
#    recvfile = os.path.join(recvdir, basename)
#
#    if (flag & 4) != 0:
#        now = time.time()
#        start = now
#        print("@@@ {} upload start {}".format(myformat(start), basename))
#        with open(sendfile, "rb") as f:
#            s3.upload_fileobj(f, bucket, basename)
#        now = time.time()
#        print("@@@ {} ({}) upload end {}".format(myformat(now), now - start, basename))
#
#    if (flag & 2) != 0:
#        now = time.time()
#        start = now
#        print("@@@ {} download start {}".format(myformat(start), basename))
#        with open(recvfile, "wb") as f:
#            s3.download_fileobj(f, bucket, basename)
#        now = time.time()
#        print("@@@ {} ({}) download end {}".format(myformat(now), now - start, basename))
#
#    if (flag & 1) != 0:
#        e = filecmp.cmp(sendfile, recvfile, shallow = False)
#        print("compare files: {}".format(e))

#def print_buckets(buckets):
#    print("Existing buckets:")
#    for bucket in buckets:
#        print("{}".format(bucket["Name"]))

def main():
    return None

#    s3 = Mys3client()
#
#    source_dir = os.path.expanduser("~/work/tmp/s")
#    download_dir = os.path.expanduser("~/work/tmp/r")
#    bucket_name = "new"
#
#    e = s3.create_bucket(bucket_name)
#    print("create bucket: e = {}".format(e))
#
#    buckets = s3.list_buckets()
#    print_buckets(buckets)
#
#    with open("test.jpg", "wb") as f:
#        f.write(os.urandom(1024))
#    up_down_n_cmp(s3, "test.jpg", "new", "/tmp")
#
#    flist = [("7M", 7), ("32M", 32), ("64M", 64)]
#
#    for basename, sz in flist:
#        source_file = os.path.join(source_dir, basename)
#        createFileM(source_file, sz, True)
#
#    for basename, sz in flist:
#        source_file = os.path.join(source_dir, basename)
#        up_down_n_cmp(s3, basename, source_dir, bucket_name, download_dir, 4)
#
#    for basename, sz in flist:
#        source_file = os.path.join(source_dir, basename)
#        up_down_n_cmp(s3, basename, source_dir, bucket_name, download_dir, 2)
#
#    for basename, sz in flist:
#        source_file = os.path.join(source_dir, basename)
#        up_down_n_cmp(s3, basename, source_dir, bucket_name, download_dir, 1)
#
#    return

#
#    GB = 1024 ** 3
#    config = TransferConfig(multipart_threshold = 5)
#    s3_client.upload_file("test.jpg", "mybucket", "test.jpg", Config = config)
#
#
#    #config = TransferConfig(max_concurrency = 5)
#    #s3_client.download_file("test.jpg", "mybucket", "test.jpg", Config = config)
#
#    response = s3_client.list_objects(
#        Bucket = "mybucket"
#        #Prefix = "xx/"
#    )
#
#    for content in response["Contents"]:
#        print("{}".format(content["Key"]))

#def myformat(t):
#    i = time.strftime('%Y%m%dT%H%M%S', time.gmtime(t))
#    f = (int)((t % 1) * 1000000)
#    return "{}.{:06d}Z".format(i, f)

if __name__ == "__main__":
    main()
