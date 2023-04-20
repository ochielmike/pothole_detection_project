import os
import boto3

class S3Uploader:
    def __init__(self, access_key, secret_key, bucket_name):
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key
        )

    def upload_folder(self, folder_path):
        print(f"Uploading folder: {folder_path}")
        for root, dirs, files in os.walk(folder_path):
            print(f"Found {len(files)} files in {root}")
            for filename in files:
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, folder_path)

                # Upload the file to the S3 bucket
                try:
                    self.s3.upload_file(file_path, self.bucket_name, relative_path)
                except Exception as e:
                    print(f"Error uploading {file_path}: {e}")
                    continue

                # Delete the file after it has been successfully uploaded to the S3 bucket
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
                

AWS_ACCESS_KEY = "*******"
AWS_SECRET_KEY = "*******"
BUCKET_NAME = "pothole-project-data"
FOLDER_PATH = "/home/pi/Desktop/project/object_detection_frames"
uploader = S3Uploader(AWS_ACCESS_KEY, AWS_SECRET_KEY, BUCKET_NAME)

# Upload the contents to the S3 bucket
uploader.upload_folder(FOLDER_PATH)
