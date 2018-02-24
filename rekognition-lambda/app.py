from chalice import Chalice
import boto3
from decimal import Decimal
import json
import urllib
app = Chalice(app_name='rekognition-lambda')


print('Loading function')
rekognition = boto3.client('rekognition')



@app.route('/')
def index():
    return {'hello': 'world'}

# --------------- Helper Functions to call Rekognition APIs ------------------


def detect_faces(bucket, key):
    response = rekognition.detect_faces(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    return response


def detect_labels(bucket, key):
    response = rekognition.detect_labels(Image={"S3Object": {"Bucket": bucket, "Name": key}})

    # Sample code to write response to DynamoDB table 'MyTable' with 'PK' as Primary Key.
    # Note: role used for executing this Lambda function should have write access to the table.
    table = boto3.resource('dynamodb').Table('MyTable')
    labels = [{'Confidence': Decimal(str(label_prediction['Confidence'])), 'Name': label_prediction['Name']} for label_prediction in response['Labels']]
    table.put_item(Item={'PK': key, 'Labels': labels})
    return response


def index_faces(bucket, key):
    # Note: Collection has to be created upfront. Use CreateCollection API to create a collecion.
    #rekognition.create_collection(CollectionId='BLUEPRINT_COLLECTION')
    response = rekognition.index_faces(Image={"S3Object": {"Bucket": bucket, "Name": key}}, CollectionId="BLUEPRINT_COLLECTION")
    return response


#Lambda request handler
def lambda_handler(event, context):
	#if (event["session"]["application"]["applicationId"] != ""):
		#raise ValueError("Invalid Application ID")
	#if event["request"]["type"] == "LaunchRequest":
	#	return on_launch(event["request"], event["session"])
	#elif event["request"]["type"] == "IntentRequest":
	#	return on_intent(event["request"], event["session"])
	#elif event["request"]["type"] == "SessionEndedRequest":
	#	return on_session_ended(event["request"], event["session"])
        bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    try:
        # Calls rekognition DetectFaces API to detect faces in S3 object
        #response = detect_faces(bucket, key)

        # Calls rekognition DetectLabels API to detect labels in S3 object
        response = detect_labels(bucket, key)

        # Calls rekognition IndexFaces API to detect faces in S3 object and index faces into specified collection
        #response = index_faces(bucket, key)

        # Print response to console.
        print(response)

        return response
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e


