# bot.py
import os
import discord
import asyncio
from discord.ext import tasks, commands
from dotenv import load_dotenv
from datetime import timedelta


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='-')  # Bot, subclass of Client discord API
bot.remove_command('help')              # Remove default help command

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    activity = discord.Activity(name='your Resin', type=discord.ActivityType.watching)     # Bot status
    await bot.change_presence(activity=activity)

resinAmount = 0     # To be used as global variable

# Set: Sets resin amount and record time to calculate resin refill at specified amount
@bot.command()
async def set(ctx, arg : int):
    global resinAmount, count
    resinAmount = arg

    if resinAmount in range (0,161):
        @tasks.loop(minutes=8.0)      # Increase resinAmount every 8 minutes
        async def count():
            global resinAmount
            await asyncio.sleep(480)
            resinAmount += 1

            if resinAmount == 160:    # Stop resin count and notifies user
                channel = bot.get_channel(int(os.getenv('CHANNEL_ID')))
                await channel.send('**Max Resin available!**')
                count.stop()

        count.start()                 # Begin resin count
        await ctx.send('Resin set to ' + str(resinAmount) + '!')
    else:
       await ctx.send('Enter a valid Resin amount. (0-160)')


# Check: Updates resin amount
@bot.command()
async def check(ctx):
    try:
        await ctx.send('You currently have ' + str(resinAmount) + ' Resin!')
    except:
        await ctx.send('No Resin available. Use !set to input Resin or !help for commands.')


# When: Shows remaning time left for resin to refill at specified amount
# Calculated by taking Resin arg - current Resin and multiplies it by 8 to find remaining time
@bot.command()
async def when(ctx, arg : int):
    if arg < resinAmount:
        await ctx.send('You already have ' + str(resinAmount) + ' Resin!')
    elif arg in range (0,161):
        result = arg - resinAmount
        hr = str(timedelta(minutes=(result) * 8))[:2]
        min = str(timedelta(minutes=(result) * 8))[3:5]

        await ctx.send('You will have %s Resin in %s hours and %s minutes.' % (str(arg), hr, min))
    else:
        await ctx.send('No Resin available. Use !set to input Resin or !help for commands.')
   

# Help commands
@bot.group(invoke_without_command = True)
async def help(ctx):
    emb = discord.Embed(title = 'Help', description = 'Use !help <command> for more info on a command.', color = ctx.author.color)
    emb.add_field(name = 'Resin' , value = 'set, check, when')
    await ctx.send(embed = emb)


@help.command()
async def set(ctx):
    emb = discord.Embed(title = 'Set', description = 'Set current resin amount', color = ctx.author.color)
    emb.add_field(name = '**Syntax**' , value = '!set <amount>')
    await ctx.send(embed = emb)


@help.command()
async def check(ctx):
    emb = discord.Embed(title = 'Check', description = 'Check current resin amount', color = ctx.author.color)
    emb.add_field(name = '**Syntax**' , value = '!check')
    await ctx.send(embed = emb)


@help.command()
async def when(ctx):
    emb = discord.Embed(title = 'When', description = 'View remaining time until specified resin', color = ctx.author.color)
    emb.add_field(name = '**Syntax**' , value = '!when <amount>')
    await ctx.send(embed = emb)


bot.run(TOKEN)
