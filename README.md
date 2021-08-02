## Usage
* Use the Telegram "Botfather" to create a new Bot. Enter the bot's access token as 'TELEGRAM_TOKEN' in docker-compose.yml.
* Use Telegram's "IDBot" to find out your Telegram ID. Set this ID in docker-compose.yml as 'TELEGRAM_CHAT_ID'.

Start the container with `docker-compose up`.

The container will check every 5 minutes for available sites, and sends a notification test once a day (at 12:00).