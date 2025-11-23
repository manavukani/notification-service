import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.getenv('DYNAMODB_TABLE'))
table = dynamodb.Table(table_name)

def is_already_processed(message_id: str) -> bool:
    try:
        response = table.get_item(Key={'message_id': message_id})
        return 'Item' in response
    except ClientError as e:
        print(f"Error checking idempotency: {e}")
        return False

def update_notification_status(message_id: str, status: str, retry_count: int, recipient: str, error: str = None):
    item = {
        'message_id': message_id,
        'status': status,
        'recipient': recipient,
        'retry_count': retry_count
    }
    if error:
        item['error_message'] = error
        
    try:
        table.put_item(Item=item)
    except ClientError as e:
        print(f"Error updating status: {e}")
