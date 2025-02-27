import json
import base64
import boto3
import os

# Initialize the S3 client
s3 = boto3.client('s3')
BUCKET_NAME = os.getenv("BUCKET_NAME")  # Replace with your actual S3 bucket name

# Allowed file extensions
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "png", "jpg", "eml", "msg"}

def lambda_handler(event, context):
    try:
        correct_password = os.getenv("UPLOAD_PASSWORD")
        body = json.loads(event["body"]) if "body" in event else event
        
        if body.get("password") != correct_password:
            return {
                "statusCode": 401,
                "body": json.dumps("Unauthorized: Incorrect password")
            }

        files = body.get("files", [])
        if not files:
            return {
                "statusCode": 400,
                "body": json.dumps("No files found in the request")
            }

        if len(files) > 10:
            return {
                "statusCode": 400,
                "body": json.dumps("You can upload a maximum of 10 files")
            }

        for file in files:
            file_name = file["name"]
            file_extension = file_name.split('.')[-1].lower()

            if file_extension not in ALLOWED_EXTENSIONS:
                return {
                    "statusCode": 400,
                    "body": json.dumps(f"Invalid file type: {file_name}. Allowed types: PDF, Word, Excel, PNG, JPG, Email.")
                }

            file_content = base64.b64decode(file["content"])
            s3.put_object(Bucket=BUCKET_NAME, Key=file_name, Body=file_content)

        return {
            "statusCode": 200,
            "body": json.dumps("File(s) uploaded successfully!")
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error: {str(e)}")
        }
