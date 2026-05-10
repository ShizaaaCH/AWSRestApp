import boto3
import os
from dotenv import load_dotenv

load_dotenv()

sns_client = boto3.client(
    "sns",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
    region_name=os.getenv("REGION_NAME", "us-east-1")
)

def publish_message_to_sns(message, subject):
    topic_arn = os.getenv("SNS_TOPIC_ARN")

    try:
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject=subject
        )
        print(f"Mensaje publicado exitosamente en SNS: {response}")
        return response
    except Exception as e:
        print(f"Error al publicar mensaje en SNS: {e}")
        return None