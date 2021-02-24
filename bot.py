# bot.py
import os
import discord

from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Bot, subclass of Client discord API
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Set: Sets resin amount and record time to calculate resin refill at specified amount
@bot.command()
async def set(ctx, arg):
    global setTime, resinAmount
    setTime = datetime.now(tz=None)   # Get current time
    resinAmount = arg

    await ctx.send('Resin set to ' + arg + '!')

# Check: Updates resin amount

# When: Shows remaning time left for resin to refill at specified amount
@bot.command()
async def when(ctx, arg):
    if arg == 'max':
        d = datetime.now(tz=None)    
        hr = str(d.hour)
        min = str(d.minute)

    await ctx.send('You will have ' + resinAmount + ' resin in ' + hr + ' hours and ' + min[-2] + ' minutes...')

bot.run(TOKEN)
