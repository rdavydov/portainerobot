# pip install python-telegram-bot==13.7 python-dotenv

import os
import logging
import requests
from telegram import BotCommand
from telegram.ext import Updater, CommandHandler
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

TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Function to get stack information


def get_stack_info(update, context):
    # Check if the command is sent from the specific group
    if str(update.message.chat_id) != CHAT_ID:
        event_logger.info(
            f"{update.message.from_user} tried to use the /get command from chat {update.message.chat_id}")
        return
    if len(context.args) == 0:
        reply_text = "Give me the stack name, e.g. /get dev (or dev2, dev3, stage-eis, reestr-rf) and I'll answer with the <stack name> <frontend version> <backend version>"
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=reply_text, reply_to_message_id=update.message.message_id)
        return
    else:
        stack_name = context.args[0]

    stack_id = os.getenv(stack_name)
    porta = stack_name == 'dev228'
    X_API_KEY = os.getenv(
        'X_API_KEY') if not porta else os.getenv('X_API_KEY_PORTA')
    stack_id = os.getenv(stack_name)
    url = f"https://portainer.eis-online.ru/api/stacks/{stack_id}" if not porta else f"https://porta.eis-online.ru/api/stacks/{stack_id}"
    headers = {
        "X-API-Key": X_API_KEY
    }
    event_logger.info(f"Request to {url} with stack ID {stack_id}")
    response = requests.get(url, headers=headers)
    event_logger.info(f"Response {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        name = data.get("Name")
        env = data.get("Env", [])
        release_frontend = next((item for item in env if item["name"] == "RELEASE_FRONTEND"), {
        }).get("value", "Not Found")
        release_backend = next((item for item in env if item["name"] == "RELEASE_BACKEND"), {
        }).get("value", "Not Found")
        info = f"{name} {release_frontend} {release_backend}"
        event_logger.info(f"Extracted Info: {info}")
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=info, reply_to_message_id=update.message.message_id)
    else:
        error_msg = f"Error {response.status_code}: Unable to retrieve information for stack {stack_name}"
        event_logger.error(error_msg)
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=error_msg, reply_to_message_id=update.message.message_id)


def set_stack_versions(update, context):
    # Check if the command is sent from the specific group
    if str(update.message.chat_id) != CHAT_ID:
        event_logger.info(
            f"{update.message.from_user} tried to use the /set command from chat {update.message.chat_id}")
        return
    if len(context.args) < 3 or not all([context.args[1].isdigit(), context.args[2].isdigit()]):
        reply_text = "Give me the stack name, frontend version and backend version, e.g. /set dev 10421 10430"
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=reply_text, reply_to_message_id=update.message.message_id)
    else:
        stack_name, front_ver, back_ver = context.args[0], context.args[1], context.args[2]
        stack_id = os.getenv(stack_name)
        porta = stack_name == 'dev228'
        file_url = f"https://portainer.eis-online.ru/api/stacks/{stack_id}/file" if not porta else f"https://porta.eis-online.ru/api/stacks/{stack_id}/file"

        stack_url = f"https://portainer.eis-online.ru/api/stacks/{stack_id}?endpointId=1" if not porta else f"https://porta.eis-online.ru/api/stacks/{stack_id}?endpointId=2"
        X_API_KEY = os.getenv(
            'X_API_KEY') if not porta else os.getenv('X_API_KEY_PORTA')
        headers = {
            "X-API-Key": X_API_KEY
        }
        # Retrieve the current stack file content and environment variables
        # Fetch stack file content
        file_response = requests.get(file_url, headers=headers)
        if file_response.status_code != 200:
            event_logger.error(
                f"Failed to get stack file with status code {file_response.status_code}")
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text=f"Failed to get stack file with status code {file_response.status_code}")
            return
        stack_file_content = file_response.json()["StackFileContent"]

        # Fetch current stack environment variables
        env_response = requests.get(stack_url, headers=headers)
        if env_response.status_code != 200:
            event_logger.error(
                f"Failed to get stack environment variables with status code {env_response.status_code}")
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text=f"Failed to get stack environment variables with status code {env_response.status_code}")
            return
        env_vars = env_response.json()["Env"]

        # Update the environment variables with the new versions
        for env_var in env_vars:
            if env_var["name"] == "RELEASE_FRONTEND":
                env_var["value"] = front_ver
            elif env_var["name"] == "RELEASE_BACKEND":
                env_var["value"] = back_ver

        # Construct the PUT request body
        put_data = {
            "StackFileContent": stack_file_content,
            "Env": env_vars,
            "Prune": False  # Set to False to not remove services not defined in the stack file
        }

        # Make the PUT request to update the stack
        put_response = requests.put(stack_url, headers=headers, json=put_data)
        if put_response.status_code == 200:
            event_logger.info(
                f"Set [{stack_name}]: front: {front_ver}, back: {back_ver}")
            reply_text = f"Set: {stack_name} {front_ver} {back_ver}"
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text=reply_text, reply_to_message_id=update.message.message_id)
        else:
            event_logger.error(
                f"Failed to update stack versions with status code {put_response.status_code}")
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text=f"Failed to update stack versions with status code {put_response.status_code}", reply_to_message_id=update.message.message_id)


def get_chat_id(update, context):
    chat_id = update.message.chat_id
    event_logger.info(f"Chat ID: {chat_id}")
    context.bot.send_message(
        chat_id=chat_id, text=f"This chat ID is: {chat_id}", reply_to_message_id=update.message.message_id)


def main():
    updater = Updater(TELEGRAM_API_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Define command handlers
    dp.add_handler(CommandHandler("get", get_stack_info))
    dp.add_handler(CommandHandler("set", set_stack_versions))
    dp.add_handler(CommandHandler("id", get_chat_id))

    # Register bot commands with Telegram
    commands = [
        BotCommand(
            'get', 'Returns <stack name> <frontend version> <backend version>'),
        BotCommand(
            'set', 'Sets <stack name> <frontend version> <backend version>'),
        BotCommand('id', 'Returns this chat ID')
    ]
    updater.bot.set_my_commands(commands)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
