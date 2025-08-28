# Discord Bot - Aiven MySQL + Free Hosting

## Local Development
Create a `.env` file in the same directory as bot.py:
```
DISCORD_TOKEN=your_discord_bot_token_here
MYSQL_HOST=your_aiven_host
MYSQL_USER=your_aiven_user
MYSQL_PASSWORD=your_aiven_password
MYSQL_DATABASE=your_database_name
MYSQL_PORT=3306
```

## Aiven MySQL Setup
1. Go to aiven.io and create free account
2. Create free MySQL service
3. Get connection details from dashboard
4. Use these details in your hosting platform

## Deployment (Railway/Render/etc)
1. Push code to GitHub
2. Connect to your hosting platform
3. Set environment variables from Aiven
4. Deploy

## Features
- 24/7 uptime with Flask keep-alive server
- Free Aiven MySQL database
- Auto-reply functionality
- Scalable and reliable
