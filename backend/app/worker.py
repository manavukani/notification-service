import json
import os
import boto3
from dotenv import load_dotenv
from app.utils import is_already_processed, update_notification_status

load_dotenv()

# Initialize clients
sqs = boto3.client('sqs')
sns = boto3.client('sns')

# Environment variables
QUEUE_URL = os.getenv('QUEUE_URL_PROD')
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN_PROD')

def lambda_handler(event, context):
    """
    Process SQS messages with idempotency and error handling
    """
    for record in event['Records']:
        try:
            body = json.loads(record['body'])
            message_id = body.get('message_id')
            recipient = body.get('recipient')
            
            if not message_id:
                print("Skipping message without ID")
                continue

            # Idempotency check
            if is_already_processed(message_id):
                print(f"Skipping duplicate: {message_id}")
                continue

            # Simulate processing (e.g. sending email)
            # In a real app, this would call SES or SendGrid
            if body.get('fail', False):
                raise Exception("Simulated failure for testing backoff")

            # Publish event to SNS (fan-out)
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=json.dumps({
                    'message_id': message_id,
                    'status': 'SENT',
                    'timestamp': record['attributes']['ApproximateFirstReceiveTimestamp']
                })
            )

            # Success path - update DynamoDB
            retry_count = int(record['attributes']['ApproximateReceiveCount'])
            update_notification_status(message_id, 'SENT', retry_count, recipient)
            print(f"Successfully processed: {message_id}")

        except Exception as e:
            print(f"Error processing message: {str(e)}")
            # Let Lambda fail so SQS retries according to backoff policy
            raise e
