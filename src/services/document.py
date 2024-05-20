import boto3
from botocore.exceptions import ClientError
import os

AWS_S3_BUCKET_NAME = 'zizo123'
AWS_REGION = 'eu-north-1'
AWS_ACCESS_KEY = 'AKIAYS2NXG522LOCM56A'
AWS_SECRET_KEY = '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'

async def upload_document_to_aws(file_name, bucket = AWS_S3_BUCKET_NAME, object_name=None):
    """Upload document to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client(
        service_name='s3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    try:
        s3_client.upload_file(file_name, bucket, object_name)
        url = f"https://{bucket}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
        return url
    except ClientError as e:
        print(e)
