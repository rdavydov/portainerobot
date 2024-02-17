# pip install python-telegram-bot==13.7 python-dotenv

import os
import logging
import requests
# from datetime import datetime
from telegram.ext import Updater, MessageHandler, Filters
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

event_logger = logging.getLogger('event_logger')
event_handler = logging.FileHandler('events.log', mode='a', encoding='utf-8')
event_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
event_logger.addHandler(event_handler)

group_chat_logger = logging.getLogger('group_chat_logger')
group_chat_handler = logging.FileHandler('group_chat.log', mode='a', encoding='utf-8')
group_chat_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
group_chat_logger.addHandler(group_chat_handler)

private_chat_logger = logging.getLogger('private_chat_logger')
private_chat_handler = logging.FileHandler('private_chat.log', mode='a', encoding='utf-8')
private_chat_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
private_chat_logger.addHandler(private_chat_handler)

# Retrieve the Telegram Bot API token
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')

# Function to get stack information
def get_stack_info(stack_name):
    # Retrieve the API key and stack ID from the .env file
    X_API_KEY = os.getenv('X_API_KEY')
    stack_id = os.getenv(stack_name)
    
    # URL to make the GET request
    url = f"https://portainer.eis-online.ru/api/stacks/{stack_id}"
    
    # Headers for the GET request
    headers = {
        "X-API-Key": X_API_KEY
    }
    
    # Log the request
    event_logger.info(f"Request to {url} with stack ID {stack_id}")
    
    # Make the GET request
    response = requests.get(url, headers=headers)
    
    # Log the response
    event_logger.info(f"Response {response.status_code}: {response.text}")
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        
        # Extract the required information
        name = data.get("Name")
        env = data.get("Env", [])
        
        # Find the specific environment variable values
        release_frontend = next((item for item in env if item["name"] == "RELEASE_FRONTEND"), {}).get("value", "Not Found")
        release_backend = next((item for item in env if item["name"] == "RELEASE_BACKEND"), {}).get("value", "Not Found")
        
        # Format the extracted information
        info = f"Name: {name}\nRELEASE_FRONTEND: {release_frontend}\nRELEASE_BACKEND: {release_backend}"
        
        # Log the extracted information
        event_logger.info(f"Extracted Info: {info}")
        
        return info
    else:
        # Return an error message
        error_msg = f"Error {response.status_code}: Unable to retrieve information."
        event_logger.error(error_msg)
        return error_msg

# Command handler function
def handle_message(update, context):
    # Extract the message text, chat ID, and user information
    message_text = update.message.text
    chat_id = update.message.chat_id
    user = update.message.from_user
    # Check if the username exists and is not empty
    username = f"@{user.username}" if user.username else f"{user.first_name}"
    last_name = user.last_name or ""
    group_name = f"'{update.message.chat.title}'" if update.message.chat.title else ""
    
    # Determine if the message is from a group chat or a private chat and log accordingly
    if update.message.chat.type == 'group':
        group_chat_logger.info(f"Group Chat {group_name} Message from {user.first_name} {last_name} [{username}] (ID: {user.id}): {message_text}")
    else:
        private_chat_logger.info(f"Private Message from {user.first_name} {last_name} [{username}] (ID: {user.id}): {message_text}")
    
    # Log the received message
    event_logger.info(f"Received {update.message.chat.type} {group_name} message from {user.first_name} {last_name} [{username}] (ID: {user.id}): {message_text}")
    
    # Check if the message starts with the command prefix
    if message_text.startswith("@portainerobot"):
        # Extract the command
        command_parts = message_text.split()
        if len(command_parts) == 1:
            context.bot.send_message(chat_id=chat_id, text="Give me the stack name, e.g. @portainerobot dev (or dev2, dev3, stage-eis)", reply_to_message_id=update.message.message_id)
        else:
            # Extract the stack name
            _, stack_name = command_parts
            # Get the stack information
            info = get_stack_info(stack_name)
            # Send the message back to the user, citing their message
            reply_text = f"{username} requested info:\n{info}"
            context.bot.send_message(chat_id=chat_id, text=reply_text, reply_to_message_id=update.message.message_id)
    else:
        # If the message does not start with the command prefix, ignore it
        pass

def main():
    updater = Updater(TELEGRAM_API_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()