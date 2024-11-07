# Telegram Broadcast Bot
This is a Telegram bot designed to manage user subscriptions and allow an administrator to broadcast messages to all subscribed users.

### Features
* Subscription Management: Users can subscribe to receive broadcast messages.
* Admin Commands: Only designated administrators can send broadcast messages.
* Command Help: Users can view available commands and their descriptions.
* User Count: Admins can view the number of subscribed users.
* Message Log: Admins can view all previously sent messages.
* Error Notifications: Admins receive notifications if something goes wrong.

### Prerequisites
* Docker
* Telegram Bot Token (Create a bot using BotFather)

## Setup
### Clone the repository

```Bash
git clone https://github.com/Ren4lk/tg_mailing_bot.git
cd telegram-broadcast-bot
```

### Environment Variables
Create a .env file in the root directory and add the following environment variables:

```Env
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
ADMIN_USER_ID=your-admin-user-id

POSTGRES_DB=your-database-name
POSTGRES_USER=your-database-username
POSTGRES_PASSWORD=your-database-password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

## Docker Setup
1. Build and Run Containers
Ensure you have Docker and Docker Compose installed. Then run the following command to build and start the containers:
```Bash
docker-compose up --build
```

2. Access PostgreSQL Data
The database data is stored in the ./db_data directory of your repository.

## Usage
### Available Commands
* `/start`: Subscribe to receive broadcast messages.
* `/help`: Show the list of available commands.
* `/broadcast`: Start broadcasting a message (admin only).
* `/list_users`: Show the number of subscribed users (admin only).
* `/list_messages`: Show all sent messages (admin only).

## Example Usage
1. Start the Bot
Users can subscribe to the bot by sending the /start command.

2. Broadcast a Message
The admin can send the /broadcast command. The bot will prompt the admin to enter a message, which will then be broadcasted to all subscribed users.

3. Command Help
Users can view the available commands by sending the /help command.

## Additional Features
1. User Count
Admins can use the /list_users command to view the total number of subscribed users.

2. Message Log
Admins can use the /list_messages command to view all previously sent messages.

3. Error Notifications
The bot will notify the admin if there is any error during operations, ensuring the admin is always informed about the bot's status.
