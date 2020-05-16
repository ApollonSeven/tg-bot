# Telegram bot on Flask
 Telegram bot on Python (Flask)
## Installing
1. Create web Flask app
2. Set telegram webhook 
```
https://api.telegram.org/bot{my_bot_token}/setWebhook?url={url_to_send_updates_to}
```
3. Add bot token in ```bot.py```
```
BOT_TOKEN = 'BOT-TOKEN'
URL='https://api.telegram.org/' + BOT_TOKEN
```
4. ???
5. PROFIT!
