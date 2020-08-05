import boto3
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig

def gfarms3_client():
    return boto3.client("s3",
        aws_access_key_id = "K4XcKzocrUhrnCAKrx2Z",
        aws_secret_access_key = "39e+URNfFv/CCgs4bYcBMusR7ngMLOxEf6cpXWpB",
        endpoint_url = "http://127.0.0.1:9001")

def create_bucket(bucket_name):
    try:
        s3_client.create_bucket(Bucket = bucket_name)
    except ClientError as e:
        sys.stderr.write("{}".format(e))
        return False
    return True

def list_buckets():
    response = s3_client.list_buckets()

    print("Existing buckets:")
    for bucket in response["Buckets"]:
        print("{}".format(bucket["Name"]))

def upload_file(file_name, bucket, object_name):
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        sys.stderr.write("{}".format(e))
        return False
    return True

def upload_fileobj(f, bucket, object_name):
    try:
        response = s3_client.upload_fileobj(f, bucket, object_name)
    except ClientError as e:
        sys.stderr.write("{}".format(e))
        return False
    return True

s3_client = gfarms3_client()

create_bucket("new")

list_buckets()

with open("test.jpg", "rb") as f:
    s3_client.upload_fileobj(f, "mybucket", "test.jpg")

#s3_client.download_file("mybucket", "test.jpg", "/tmp/test.jpg")

with open("/tmp/test-2.jpg", "wb") as f:
    s3_client.download_fileobj("mybucket", "test.jpg", f)


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
