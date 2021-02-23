# bot.py
import os
import discord

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Bot, subclass of Client discord API
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Max resin bot command
@bot.command(amount='max' or '40')
async def _max(ctx):
    await ctx.send('You will have' + amount + 'resin in - hours and - minutes.')

bot.run(TOKEN)
