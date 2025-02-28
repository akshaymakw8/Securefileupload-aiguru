import json
import base64
import boto3
import os

# Initialize the S3 client
s3 = boto3.client('s3')
BUCKET_NAME = os.getenv("BUCKET_NAME")  # Replace with your actual S3 bucket name

# Allowed file extensionsimport os
import json
import base64
import boto3

# Initialize the S3 client
s3 = boto3.client('s3')

# Environment variables provided via CloudFormation
BUCKET_NAME = os.environ.get('BUCKET_NAME')
UPLOAD_PASSWORD = os.environ.get('UPLOAD_PASSWORD')

def lambda_handler(event, context):
    """
    Expected JSON payload (from API Gateway):
    {
      "uploadPassword": "yourPassword",
      "fileName": "example.txt",
      "fileContent": "<base64-encoded file content>"
    }
    """
    # Retrieve the request body (API Gateway proxy integration)
    body_str = event.get("body")
    if not body_str:
        return _response(400, "Missing request body")
    
    try:
        body = json.loads(body_str)
    except json.JSONDecodeError:
        return _response(400, "Invalid JSON in request body")
    
    # Validate the upload password
    if body.get("uploadPassword") != UPLOAD_PASSWORD:
        return _response(403, "Invalid upload password")
    
    # Retrieve file details from the payload
    file_name = body.get("fileName")
    file_content_b64 = body.get("fileContent")
    if not file_name or not file_content_b64:
        return _response(400, "Missing fileName or fileContent")
    
    # Decode the base64 file content
    try:
        decoded_content = base64.b64decode(file_content_b64)
    except Exception as e:
        return _response(400, f"Error decoding fileContent: {str(e)}")
    
    # Upload the file to S3
    try:
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=decoded_content
        )
    except Exception as e:
        return _response(500, f"Error uploading file to S3: {str(e)}")
    
    return _response(200, f"File '{file_name}' uploaded successfully to bucket '{BUCKET_NAME}'.")

def _response(status_code, message):
    """Helper function to format API Gateway proxy responses."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"  # Enable CORS if needed
        },
        "body": json.dumps({"message": message})
    }

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
