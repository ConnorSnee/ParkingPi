from chalice import Chalice

app = Chalice(app_name='alexa-lambda')


@app.route('/')
def index():
    return {'hello': 'world'}


def lambda_handler(event, context):
    #TODO enter the application ID
	if (event["session"]["application"]["applicationId"] != ""):
		raise ValueError("Invalid Application ID")
	if event["request"]["type"] == "LaunchRequest":
		return on_launch(event["request"], event["session"])
	elif event["request"]["type"] == "IntentRequest":
		return on_intent(event["request"], event["session"])
	elif event["request"]["type"] == "SessionEndedRequest":
		return on_session_ended(event["request"], event["session"])

#When a launch request is received
def on_launch(launch_request, session):
	return get_welcome_response()

#When an intent request is received
def on_intent(intent_request, session):
	intent = intent_request["intent"]
	intent_name = intent_request["intent"]["name"]

	if intent_name == "AMAZON.HelpIntent":
		return get_welcome_response()
	elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
		return handle_session_end_request()
	else:
        #TODO add intent names and functions
        if intent_name == "":
			return
        else:
			raise ValueError("Invalid intent")

#When a session ended request is received
def on_session_ended(session_ended_request, session):
	print("Ending session.")

def handle_session_ended_request():
	session_attributes = {}
	card_title = "Goodbye"
	speech_output = "Thank you for using the Parking Counter app, goodbye"
	should_end_session = True
	return build_response(session_attributes, build_speechlet_response(card_title, speech_output, should_end_session))

def get_welcome_response():
	session_attributes = {}
	card_title = "Welcome"
	speech_output = "Welcome to the Parking Counter skill."
	should_end_session = True
	return build_response(session_attributes, build_speechlet_response(card_title, speech_output, should_end_session))

def build_speechlet_response(title, output, should_end_session):
	return {
		"outputSpeech": {
			"type": "PlainText",
			"text": output
		},
		"card": {
			"type": "Simple",
			"title": title,
			"content": output
		},
		"shouldEndSession": should_end_session
	}

def build_response(session_attributes, speechlet_response):
	return {
		"version": "1.0",
		"sessionAttributes": session_attributes,
		"response": speechlet_response
	}
