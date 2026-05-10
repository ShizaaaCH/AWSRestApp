import boto3
import os
import uuid
import time
import secrets
from dotenv import load_dotenv

load_dotenv()

dynamodb = boto3.resource(
    "dynamodb",
    region_name=os.getenv("REGION_NAME", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN")
)

table = dynamodb.Table("sesiones-alumnos")

def create_session(alumno_id):
    #crear session string de 128 caracteres
    session_string = secrets.token_hex(64)
    
    session_item = {
        "id": str(uuid.uuid4()),
        'fecha': int(time.time()),
        'alumnoID': int(alumno_id),
        'sessionString': session_string,
        'active': True
    }
    table.put_item(Item=session_item)
    return session_string

def get_session(session_string):
    response = table.get_item(Key={'sessionString': session_string})
    return response.get('Item')

def deactivate_session(session_string):
    table.update_item(
        Key={'sessionString': session_string},
        UpdateExpression="set active = :a",
        ExpressionAttributeValues={':a': False}
    )