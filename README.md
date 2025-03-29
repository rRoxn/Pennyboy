# PennyBot - Discord Dice Rolling Bot

A lightweight Discord bot for dice rolling and betting, optimized for Raspberry Pi deployment.

## Features

- Daily currency rewards
- Dice rolling with betting (win double your bet!)
- Support for "all-in" betting
- Optimized for Raspberry Pi performance

## Requirements

- Python 3.9+
- Raspberry Pi (or any Linux system)
- Discord Bot Token

## Setup

1. Create a Python virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/Raspberry Pi
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your Discord bot token:

   ```bash
   cp .env.example .env
   ```

4. Start the bot:
   ```bash
   python src/bot.py
   ```

## Running on Raspberry Pi

### System Requirements

- Raspberry Pi 3 or newer recommended
- At least 512MB free RAM
- Python 3.9 or newer

### Running as a Service

1. Create a systemd service file:

   ```bash
   sudo nano /etc/systemd/system/pennybot.service
   ```

2. Add the following content:

   ```ini
   [Unit]
   Description=PennyBot Discord Bot
   After=network.target

   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/path/to/pennybot
   Environment=PATH=/path/to/pennybot/venv/bin
   ExecStart=/path/to/pennybot/venv/bin/python src/bot.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```bash
   sudo systemctl enable pennybot
   sudo systemctl start pennybot
   ```

## Commands

- `/daily` - Claim your daily reward
- `/balance` - Check your current balance
- `/roll <amount>` - Roll dice and bet (use 'all' to bet everything)

## How to Play

1. Get your daily coins using `/daily`
2. Check your balance with `/balance`
3. Bet coins using `/roll <amount>` or `/roll all`
4. Win double your bet if your roll is higher than the bot's!

## Configuration

Configure in `.env`:

- `DAILY_REWARD`: Amount of currency given for daily rewards
- `CURRENCY_SYMBOL`: Symbol to represent the currency
- `CURRENCY_NAME`: Name of the currency

## Maintenance

Check logs:

```bash
tail -f bot.log
```

Monitor system resources:

```bash
top -u pi  # Replace 'pi' with your username
```
