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

# Remove default help command
bot.remove_command("help")

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

    try:
        await ctx.send('You will have ' + resinAmount + ' resin in ' + hr + ' hours and ' + min[-2] + ' minutes...')
    except:
        await ctx.send('No resin available. Use !set to input resin or !help for commands.')
   
# Help commands
@bot.group(invoke_without_command = True)
async def help(ctx):
    emb = discord.Embed(title = "Help", description = "Use !help <command> for more info on a command.", color = ctx.author.color)
    emb.add_field(name = "Resin" , value = "set, check, when")
    await ctx.send(embed = emb)

@help.command()
async def set(ctx):
    emb = discord.Embed(title = "Set", description = "Set current resin amount", color = ctx.author.color)
    emb.add_field(name = "**Syntax**" , value = "!set <amount>")
    await ctx.send(embed = emb)

@help.command()
async def check(ctx):
    emb = discord.Embed(title = "Check", description = "Check current resin amount", color = ctx.author.color)
    emb.add_field(name = "**Syntax**" , value = "!check")
    await ctx.send(embed = emb)

@help.command()
async def when(ctx):
    emb = discord.Embed(title = "When", description = "View remaining time until specified resin", color = ctx.author.color)
    emb.add_field(name = "**Syntax**" , value = "!when <amount>")
    await ctx.send(embed = emb)

bot.run(TOKEN)
