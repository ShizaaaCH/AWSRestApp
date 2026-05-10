import boto3
import os
from dotenv import load_dotenv

load_dotenv()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
    region_name=os.getenv("REGION_NAME", "us-east-1")
)

def upload_file_to_s3(file, alumno_id):
    bucket_name = os.getenv("S3_BUCKET_NAME")

    if not bucket_name:
        print("Error: S3_BUCKET_NAME no está configurado")
        return None
    
    try:
        filename = f"foto_{alumno_id}_{file.filename}"
        s3_client.upload_fileobj(file,
                                 bucket_name,
                                 filename,
                          ExtraArgs={
                              'ACL': 'public-read',
                              'ContentType': file.content_type})
        print(f"Archivo {filename} subido exitosamente a {bucket_name}/{filename}")
        return f"https://{bucket_name}.s3.amazonaws.com/{filename}"

    except Exception as e:
        print(f"Error al subir archivo: {e}")
        return None