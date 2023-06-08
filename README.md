# FBChatbot_KoboldAI

This is a Facebook Messenger Chatbot Callback Server powered by KoboldAI. For more detailed instructions on setting up the KoboldAI Client, please refer to this [guide](https://github.com/KoboldAI/KoboldAI-Client).
For non-GPU users, Colab Pro+ is strongly recommended for KoboldAI endpoint generation. 

# Python ChatBot Webhook Application

This is a Python Flask application that uses a webhook to process incoming messages. The application leverages Natural Language Processing to process and respond to user messages. It includes functionality to handle Korean input and conversation history.

## Features

1. Processing incoming messaging events.
2. Responding to messages using natural language processing.
3. Logging of conversation history.
4. Handling of Korean language inputs.

## Setup Instructions

1. Clone this repository.
2. Navigate to the project directory.
3. Install the necessary dependencies by running `pip install -r requirements.txt`.
4. Set up your environment variables for `VERIFY_TOKEN` and `PAGE_ACCESS_TOKEN`.
5. For more detailed instructions on setting up the Facebook Messenger Bot, please refer to this [guide](https://blog.hartleybrody.com/fb-messenger-bot/).
6. Run the application using `python app.py`.

## Contribution

Please feel free to fork this project, submit a pull request or report any issues.

## License

This project is licensed under the MIT License.
