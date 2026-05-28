import os
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

class S3Client:
    def __init__(self):
        self.bucket_name = os.environ["S3_BUCKET_NAME"]
        self.s3 = boto3.client('s3')

    def upload_bytes(self, file_content, s3_key):
        try:
            self.s3.put_object(Bucket=self.bucket_name, Key=s3_key, Body=file_content)
            return True
        except NoCredentialsError:
            print("[S3 ERROR] No AWS credentials available")
            return False
        except Exception as e:
            print(f"[S3 ERROR] Error while uploading {s3_key}: {e}")
            return False