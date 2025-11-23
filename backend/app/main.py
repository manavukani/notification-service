from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from app.models import Notification, NotificationStatus
import boto3
import os
import uuid
import json

load_dotenv()

app = FastAPI(title="Resilient Notification Service")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS Clients
sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.getenv('DYNAMODB_TABLE'))
QUEUE_URL = os.getenv('QUEUE_URL')

class NotificationRequest(BaseModel):
    recipient: str
    subject: str
    body: str
    fail: bool = False # For testing failures

@app.post("/notifications", status_code=202)
async def create_notification(request: NotificationRequest):
    message_id = str(uuid.uuid4())
    
    message = {
        "message_id": message_id,
        "recipient": request.recipient,
        "subject": request.subject,
        "body": request.body,
        "fail": request.fail
    }
    
    try:
        # Send to SQS
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(message),
            MessageGroupId=request.recipient, # For FIFO ordering per user
            MessageDeduplicationId=message_id
        )
        
        # Initial write to DynamoDB
        table.put_item(Item={
            'message_id': message_id,
            'status': 'PENDING',
            'recipient': request.recipient,
            'retry_count': 0
        })
        
        return {"message_id": message_id, "status": "Accepted"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notifications/{message_id}")
async def get_notification_status(message_id: str):
    response = table.get_item(Key={'message_id': message_id})
    if 'Item' not in response:
        raise HTTPException(status_code=404, detail="Notification not found")
    return response['Item']

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
