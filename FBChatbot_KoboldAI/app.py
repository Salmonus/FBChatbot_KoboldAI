# Import necessary libraries
import os
import re
import json
import requests
from datetime import datetime
from flask import Flask, request
from nltk.tokenize import sent_tokenize

# Instantiate a Flask application
app = Flask(__name__)

# Define KoboldAI endpoint
endpoint = ""

# Define characters folder
characters_folder = 'Characters'

# Initialize an empty list to store character data
characters = []

# Iterate over all JSON files in the characters folder and append character data to list
for filename in os.listdir(characters_folder):
    if filename.endswith('.json'):
        with open(os.path.join(characters_folder, filename)) as read_file:
            character_data = json.load(read_file)
            characters.append(character_data)

# Extract data for the first character
data = characters[0]

# Get character attributes
char_name = data["char_name"]
char_greeting = data["char_greeting"]
char_persona = data["char_persona"]
world_scenario = data["world_scenario"]
dialogue = data["example_dialogue"]

# Define the number of lines to keep in the conversation history
num_lines_to_keep = 20

@app.route('/', methods=['GET'])
def verify():
    """
    When the endpoint is registered as a webhook, it must echo back
    the 'hub.challenge' value it receives in the query arguments.
    """
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200

@app.route('/', methods=['POST'])
def webhook():
    """
    Endpoint for processing incoming messaging events.
    """

    # Extract request data
    data = request.get_json()

    # Process page object data
    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                # Process messaging events
                if messaging_event.get("message"):

                    # Extract relevant message attributes
                    sender_id = messaging_event["sender"]["id"]  # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    user_input = message_text

                    # Check for Korean language in user input and adjust accordingly
                    if check_hangul(user_input) == True:
                        user_input = "(speaks in Korean but impossible to understand.)"

                    # Ensure user-specific chat logs directory exists
                    chatlogs_dir = os.path.join('chatlogs', sender_id)
                    if not os.path.exists(chatlogs_dir):
                        os.makedirs(chatlogs_dir)

                    # Ensure user-specific chat logs file exists
                    chatlog_file = os.path.join(chatlogs_dir, 'chatlog.txt')
                    if not os.path.isfile(chatlog_file):
                        with open(chatlog_file, 'w') as f:
                            f.write(f"{char_name}'s Persona: {char_persona}\n{dialogue}\n")

                    # Load conversation history
                    with open(chatlog_file, 'r') as f:
                        conversation_history = f.read()

                    # Add user input to conversation history
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    conversation_history += f'You: {user_input}\n'
                    temp_chat = f'You: {user_input}\n'

                    # Prepare the prompt
                    prompt = {
                        "prompt": '\n'.join(conversation_history.split('\n')[-num_lines_to_keep:]) + f'{char_name}:',
                        "use_story": False,
                        "use_memory": False,
                        "use_authors_note": False,
                        "use_world_info": False,
                        "max_context_length": 1000,
                        "max_length": 250, #recommend 250 for response speed. Else, FB sends multiple requests that result in errors. 
                        "rep_pen": 1.03,
                        "rep_pen_range": 1024,
                        "rep_pen_slope": 0.9,
                        "temperature": 1,
                        "tfs": 0.9,
                        "top_a": 0,
                        "top_k": 0,
                        "top_p": 1,
                        "typical": 1,
                        "sampler_order": [6, 0, 1, 2, 3, 4, 5]
                    }

                    # Send POST request to API endpoint and handle the response
                    response = requests.post(f"{endpoint}/api/v1/generate", json=prompt)

                    # Process the response
                    if response.status_code == 200:

                        # Extract result from response
                        results = response.json()['results']
                        text = results[0]['text']

                        # Format and clean up the response text
                        split_text = text.split("You:")
                        response_text = split_text[0].strip().replace(f"{char_name}:", "").strip()
                        sentences = sent_tokenize(response_text)
                        sentences = [s for s in sentences if s.endswith(('.', '!', '?'))]
                        response_text = ' '.join(sentences)

                        # Update conversation history with bot's response
                        conversation_history += f'{char_name}: {response_text}\n'
                        temp_chat += f'{char_name}: {response_text}\n'

                        # Save conversation history to file
                        with open(chatlog_file, 'a') as f:
                            f.write(temp_chat)
                    else:
                        response_text = ""
                        print("Oh no!")

                    # Send message to the user
                    send_message(sender_id, response_text)

                # Handle other types of messaging events
                if messaging_event.get("delivery"):  # delivery confirmation
                    pass
                if messaging_event.get("optin"):  # optin confirmation
                    pass
                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):
    """
    Send a message to the specified recipient.
    """

    # Prepare request parameters and headers
    params = {"access_token": os.environ["PAGE_ACCESS_TOKEN"]}
    headers = {"Content-Type": "application/json"}

    # Prepare the data payload
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })

    # Send the request
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)


def check_hangul(text):
    """
    Check if the text contains Hangul (Korean characters).
    """
    return bool(re.search('[가-힣]', text))


if __name__ == '__main__':
    # Run the application
    app.run(host='0.0.0.0', port=80, threaded=True, debug=True)