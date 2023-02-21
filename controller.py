import boto3
from flask import Flask, request, abort, make_response, jsonify
import os, json, concurrent.futures, time

app = Flask(__name__)

REGION = "us-east-1"
os.environ['AWS_ACCESS_KEY_ID'] = "AKIA3OBARTQ6E3JMDVRU"
os.environ['AWS_SECRET_ACCESS_KEY'] = "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"


INCOMING_RESPONSES_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/786047278140/Incoming_Request_Queue"
OUTGOING_RESPONSES_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/786047278140/Outgoing_Response_Queue"

sqsClient = boto3.client('sqs', REGION)

@app.route("/v1/classify_img", methods = ["POST"])
def save_image():
    # Get request body in form of JSON
    jsonData = request.json

    if "img" not in jsonData or len(jsonData["img"]) == 0:
        return abort(400, "Image not found!")
    
    img_encoding = jsonData["img"]

    # send message to request queue
    response = sqsClient.send_message(
        QueueUrl = INCOMING_RESPONSES_QUEUE_URL,
        MessageBody = img_encoding
    )

    print(response.get('MessageId'), " message sent to message queue")

    # receive message from response queue
    response = sqsClient.receive_message(
        QueueUrl = OUTGOING_RESPONSES_QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10,
    )

    print(f"Number of messages received: {len(response.get('Messages', []))}")

    for message in response.get("Messages", []):
        message_body = message["Body"]
        print(f"Message body:", message_body)
        print(f"Receipt Handle: {message['ReceiptHandle']}")

        sqsClient.delete_message(
            QueueUrl = OUTGOING_RESPONSES_QUEUE_URL,
            ReceiptHandle = message["ReceiptHandle"]
        )

        return make_response(message_body, 200)

    return abort(500, "Internal Server Error")

if __name__ == "__main__":
    app.run()