import json
import boto3
import os
from decimal import Decimal

dyn = boto3.resource('dynamodb')
sns = boto3.client('sns')
# We are using in code values because this is a demo
# Use proper environment variables
TABLE = os.environ.get("TABLE", "fraud-detections")
SNS_ARN = os.environ.get("SNS_ARN", "arn:aws:sns:us-east-1:461840362463:fraud-alerts")

# For our fictional finance institution, we'll assume 500k transactions monthly
THRESHOLD = 500000

def lambda_handler(event, context):

    # We're getting the data from the sqs events
    for record in event["Records"]:
        body = json.loads(record["body"])
        txn_id = body["transaction_id"]
        amount = Decimal(str(body["amount"]))
        merchant = body["merchant"]

        flagged = amount > THRESHOLD

        dyn.Table(TABLE).put_item(
            Item={
                "transaction_id": txn_id,
                "amount": amount,
                "merchant": merchant,
                "flagged": flagged
            }
        )

        if flagged:
            sns.publish(
                TopicArn=SNS_ARN,
                Message=f"Suspicious transfer Flagged: {txn_id} — NGN {amount} — {merchant}",
                Subject="Fraud Alert"
            )
    return {
        'statusCode': 200,
    }
