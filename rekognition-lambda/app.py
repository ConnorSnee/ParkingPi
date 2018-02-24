from chalice import Chalice

app = Chalice(app_name='rekognition-lambda')


@app.route('/')
def index():
    return {'hello': 'world'}



#Lambda request handler
def lambda_handler(event, context):
	if (event["session"]["application"]["applicationId"] != ""):
		raise ValueError("Invalid Application ID")
	#if event["request"]["type"] == "LaunchRequest":
	#	return on_launch(event["request"], event["session"])
	#elif event["request"]["type"] == "IntentRequest":
	#	return on_intent(event["request"], event["session"])
	#elif event["request"]["type"] == "SessionEndedRequest":
	#	return on_session_ended(event["request"], event["session"])
