# Discord Bot - Render Deployment

## Local Development
Create a `.env` file in the same directory as bot.py:
```
DISCORD_TOKEN=your_discord_bot_token_here
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

## Render Deployment
1. Push code to GitHub
2. Create new Web Service on Render
3. Connect your GitHub repo
4. Add PostgreSQL database
5. Set environment variable:
   - `DISCORD_TOKEN` - Your Discord bot token
   - `DATABASE_URL` - Automatically provided by Render PostgreSQL

## Features
- 24/7 uptime with Flask keep-alive server
- PostgreSQL database for FAQ storage
- Auto-reply functionality
