# Discord Bot - Koyeb Deployment

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

## Koyeb Deployment Steps
1. **Setup Database**: Create free MySQL on Aiven.io
2. **Push to GitHub**: Your code is ready
3. **Deploy on Koyeb**:
   - Go to koyeb.com and create account
   - Create new app from GitHub
   - Select your repository
   - Set environment variables
   - Deploy

## Environment Variables for Koyeb
- `DISCORD_TOKEN` - Your Discord bot token
- `MYSQL_HOST` - From Aiven dashboard
- `MYSQL_USER` - From Aiven dashboard  
- `MYSQL_PASSWORD` - From Aiven dashboard
- `MYSQL_DATABASE` - From Aiven dashboard
- `MYSQL_PORT` - Usually 3306

## Features
- 24/7 uptime with Flask keep-alive server
- Free Aiven MySQL database
- Auto-reply functionality
- Global edge deployment with Koyeb
