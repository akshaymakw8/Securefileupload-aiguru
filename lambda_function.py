import json
import base64
import boto3
import os

s3 = boto3.client('s3')
BUCKET_NAME = os.getenv("BUCKET_NAME")  
UPLOAD_PASSWORD = os.getenv("UPLOAD_PASSWORD")

# Allowed file extensions
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "png", "jpg", "eml", "msg"}

def build_response(status_code, message):
    """
    Helper function to build a response that includes
    CORS headers for AWS_PROXY integration.
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "POST,OPTIONS"
            # Remove the commented line about credentials since it's not in your OPTIONS method
        },
        "body": json.dumps(message)
    }

def lambda_handler(event, context):
    try:
        # If using API Gateway proxy, 'body' is a JSON string
        body = json.loads(event["body"]) if "body" in event else event

        if body.get("password") != UPLOAD_PASSWORD:
            return build_response(401, "Unauthorized: Incorrect password")

        files = body.get("files", [])
        if not files:
            return build_response(400, "No files found in the request")

        if len(files) > 10:
            return build_response(400, "You can upload a maximum of 10 files")

        for file in files:
            file_name = file["name"]
            file_extension = file_name.split('.')[-1].lower()

            if file_extension not in ALLOWED_EXTENSIONS:
                return build_response(
                    400,
                    f"Invalid file type: {file_name}. Allowed types: PDF, Word, Excel, PNG, JPG, Email."
                )

            file_content = base64.b64decode(file["content"])
            s3.put_object(Bucket=BUCKET_NAME, Key=file_name, Body=file_content)

        return build_response(200, "File(s) uploaded successfully!")

    except Exception as e:
        return build_response(500, f"Error: {str(e)}")
