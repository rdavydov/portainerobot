# Portainerobot

Portainerobot is a Telegram bot designed to help users control their Portainer stacks via simple commands. Initially developed for internal use at [eis-online.ru](https://eis-online.ru), it can be useful for anyone using Portainer who wants to manage stacks through a Telegram interface. The bot allows users to retrieve and set stack versions (frontend and backend) directly from their Telegram chat.

## Features

- **Retrieve Stack Information:** Get details about the Portainer stack, including the frontend and backend release versions.
- **Set Stack Versions:** Update the frontend and backend versions of a specific stack.
- **Group and Private Chat Logging:** Logs interactions in group and private chats for auditing.
- **Supports Multiple Environments:** Switch between different environments using API keys and stack IDs.

## Installation

### Prerequisites

- Python 3.6+
- A Portainer instance with API access.
- A Telegram bot token (You can create one using [BotFather](https://core.telegram.org/bots#botfather)).
- Environment variables configuration (detailed below).

### Dependencies

Install the required Python packages using pip:

```bash
pip install python-telegram-bot==13.7 python-dotenv requests
```

### Environment Variables

Create a `.env` file in the project root to store your sensitive data:

```bash
TELEGRAM_API_TOKEN=your_telegram_bot_token
CHAT_ID=your_chat_id
X_API_KEY=your_portainer_api_key
X_API_KEY_PORTA=your_portainer_api_key_for_different_instance (optional)
dev=your_stack_id_for_dev
dev2=your_stack_id_for_dev2
dev3=your_stack_id_for_dev3
stage-eis=your_stack_id_for_stage_eis
reestr-rf=your_stack_id_for_reestr_rf
dev228=your_stack_id_for_dev228
```

- Replace `your_telegram_bot_token` with your Telegram bot's token.
- Replace `your_portainer_api_key` and `your_stack_id` values with the actual values from your Portainer instance.
- The `dev228` environment and its `X_API_KEY_PORTA` are optional, but useful if you're managing multiple Portainer environments.

## Usage

After setting up the environment, you can use the following commands with the bot:

### Commands

- **/get `<stack_name>`**: Retrieves the current stack version (frontend and backend). Examples: `/get dev`, `/get stage-eis`, `/get reestr-rf`.

- **/set `<stack_name> <frontend_version> <backend_version>`**: Sets the frontend and backend versions for the specified stack. Example: `/set dev 10421 10430`.

- **/id**: Retrieves the current chat ID (useful for configuring the bot to work only in specific chats).

### Example

To get information about the `dev` stack:

```
/get dev
```

The bot will respond with the stack name, frontend version, and backend version.

To update the stack versions for `dev`:

```
/set dev 10500 10510
```

The bot will update the environment variables in Portainer for the specified stack.

## Logging

The bot logs all interactions in three different files for auditing purposes:

- `events.log`: Logs general events and API requests.
- `group_chat.log`: Logs all group chat messages.
- `private_chat.log`: Logs all private messages.

These logs can help trace bot usage and API interactions.

## Running the Bot

You can start the bot by running:

```bash
python portainerobot.py
```

The bot will start polling for messages in the configured Telegram chat.

## Files

- `portainerobot.py`: The main bot script that handles all Telegram commands and interactions with Portainer.
- `old-portainerobot.py`: An older version of the bot, kept for reference.

## Contributions

Contributions are welcome! If you have suggestions for new features or improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
