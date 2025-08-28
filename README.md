# Discord Bot - WispByte Deployment

## Local Development
Create a `.env` file in the same directory as bot.py:
```
DISCORD_TOKEN=your_discord_bot_token_here
```

## WispByte Deployment
1. Push code to GitHub
2. Create account on WispByte
3. Connect your GitHub repo
4. Set environment variable:
   - `DISCORD_TOKEN` - Your Discord bot token
5. Deploy with Procfile

## Features
- 24/7 uptime with Flask keep-alive server
- SQLite database for FAQ storage (no external DB needed)
- Auto-reply functionality
- Lightweight and fast
