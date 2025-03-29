import os
import discord
import random
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from models.user import User, Base

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()

# Bot setup with minimal intents for better performance
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Database setup
engine = create_async_engine(
    f"sqlite+aiosqlite:///{os.getenv('DATABASE_PATH', 'data/database.sqlite')}",
    echo=False
)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_user(session, user_id):
    stmt = select(User).where(User.user_id == str(user_id))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        user = User(user_id=str(user_id))
        session.add(user)
    return user

@bot.event
async def on_ready():
    await init_db()
    try:
        await bot.user.edit(username="Randy Marsh")
    except discord.HTTPException:
        pass  # Skip if we can't change the name due to rate limits
    logging.info(f'Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logging.error(f"Failed to sync commands: {e}")

@bot.tree.command(name="daily", description="Claim your daily Tegridy reward")
async def daily(interaction: discord.Interaction):
    async with AsyncSessionLocal() as session:
        user = await get_user(session, interaction.user.id)
        
        # Check if user can claim daily reward
        now = datetime.utcnow()
        if user.last_daily and (now - user.last_daily).days < 1:
            next_daily = user.last_daily + timedelta(days=1)
            time_left = next_daily - now
            hours = time_left.seconds // 3600
            minutes = (time_left.seconds % 3600) // 60
            await interaction.response.send_message(
                f"Hey hey hey, you need to wait {hours}h {minutes}m before getting more Tegridy!"
            )
            return

        daily_amount = int(os.getenv('DAILY_REWARD', 1000))
        user.balance += daily_amount
        user.total_earned += daily_amount
        user.last_daily = now
        await session.commit()

        await interaction.response.send_message(
            f"🌿 Got Tegridy! Here's your daily {daily_amount} {os.getenv('CURRENCY_SYMBOL', '🌿')} {os.getenv('CURRENCY_NAME', 'Tegridy Bucks')}!\n"
            f"Current Tegridy: {user.balance} {os.getenv('CURRENCY_SYMBOL', '🌿')}"
        )

@bot.tree.command(name="balance", description="Check your Tegridy balance")
async def balance(interaction: discord.Interaction):
    async with AsyncSessionLocal() as session:
        user = await get_user(session, interaction.user.id)
        await session.commit()
        
        await interaction.response.send_message(
            f"Your Tegridy balance: {user.balance} {os.getenv('CURRENCY_SYMBOL', '🌿')} {os.getenv('CURRENCY_NAME', 'Tegridy Bucks')}"
        )

@bot.tree.command(name="roll", description="Roll dice and bet your Tegridy Bucks")
@app_commands.describe(
    amount="Amount to bet (use 'all' for all your Tegridy)",
)
async def roll(interaction: discord.Interaction, amount: str):
    async with AsyncSessionLocal() as session:
        user = await get_user(session, interaction.user.id)
        
        # Convert amount to integer
        if amount.lower() == 'all':
            bet_amount = user.balance
        else:
            try:
                bet_amount = int(amount)
            except ValueError:
                await interaction.response.send_message("Please enter a valid number or 'all'")
                return

        # Validate bet amount
        if bet_amount <= 0:
            await interaction.response.send_message("Bet amount must be positive!")
            return
        if bet_amount > user.balance:
            await interaction.response.send_message("You don't have enough currency!")
            return

        # Roll dice (1-6)
        user_roll = random.randint(1, 6)
        bot_roll = random.randint(1, 6)

        # Determine outcome
        if user_roll > bot_roll:
            # Win (2x bet)
            winnings = bet_amount
            user.balance += winnings
            result = "won"
        elif user_roll < bot_roll:
            # Lose bet
            user.balance -= bet_amount
            winnings = -bet_amount
            result = "lost"
        else:
            # Tie (return bet)
            winnings = 0
            result = "tied"

        await session.commit()

        # Create response message
        message = (
            f"🎲 You rolled: {user_roll}\n"
            f"🤖 Bot rolled: {bot_roll}\n\n"
            f"You {result}! "
        )
        
        if result == "won":
            message += f"You won {winnings} {os.getenv('CURRENCY_SYMBOL', '🌿')}!"
        elif result == "lost":
            message += f"You lost {abs(winnings)} {os.getenv('CURRENCY_SYMBOL', '🌿')}!"
        else:
            message += "It's a tie! Your bet has been returned."

        message += f"\nNew balance: {user.balance} {os.getenv('CURRENCY_SYMBOL', '🌿')}"
        
        await interaction.response.send_message(message)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown. Try again in {error.retry_after:.2f}s")
    else:
        logging.error(f"Error: {str(error)}")

# Run the bot
def run_bot():
    try:
        bot.run(os.getenv('DISCORD_TOKEN'), log_handler=None)
    except Exception as e:
        logging.error(f"Failed to start bot: {e}")

if __name__ == "__main__":
    run_bot() 