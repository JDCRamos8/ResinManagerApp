# bot.py
import os
import discord
import asyncio
import random
import pymongo
from discord.ext import tasks, commands
from dotenv import load_dotenv
from datetime import timedelta
from pymongo import MongoClient


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CONNECTION = os.getenv('CONNECTION_URL')


bot = commands.Bot(command_prefix='-')  # Bot, subclass of Client discord API
bot.remove_command('help')              # Remove default help command

# Connect to MongoDB Cluster
cluster = MongoClient(CONNECTION)
db = cluster['UserData']
collection = db['UserData']


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    activity = discord.Activity(name='your Resin', type=discord.ActivityType.watching)     # Bot status
    await bot.change_presence(activity=activity)


# Set: Sets resin amount and records time to calculate resin refill at specified amount
@bot.command()
async def set(ctx, arg : int):
    myquery = { '_id': ctx.author.id }
    query = {'_id': ctx.author.id}
    user = collection.find(query)
    for result in user:
        resin = result['resin']
        reminder = result['reminder']

    if (collection.count_documents(myquery) == 0):  # User does not exist in database, add user
        post = {'_id': ctx.author.id, 'resin': arg, 'reminder': 0}
        collection.insert_one(post)

    else:                                           # User exists in database, update resin amount
        collection.delete_many({"_id": ctx.author.id})
        post = {'_id': ctx.author.id, 'resin': arg, 'reminder': 0}
        collection.insert_one(post)

    if arg in range(0, 161):
        @tasks.loop(seconds=3.0)                    # Increase resinAmount every 8 minutes
        async def count():
            query = {'_id': ctx.author.id}
            user = collection.find(query)
            for result in user:
                resin = result['resin']
                reminder = result['reminder']
        
            await asyncio.sleep(5)
            resin += 1

            filter = { '_id': ctx.author.id }
            updatedResin = { "$set": { 'resin': resin } }
            collection.update_one(filter, updatedResin) 

            discordUser = await bot.fetch_user(ctx.author.id)

            if (resin == reminder):                 # Notifies user of their when() command
                await discordUser.send('**%s Resin available!**' % str(reminder))

            if (resin == 160):                      # Max Resin reached, notifies user
                await discordUser.send('**Max Resin available!**')
                count.stop()

        count.start()                               # Begin resin count
        await ctx.send('Resin set to ' + str(arg) + '!')
    else:
       await ctx.send('Enter a valid Resin amount. (0-160)')


# Check: Display user's current Resin amount
@bot.command()
async def check(ctx):
    myquery = { '_id': ctx.author.id }

    if (collection.count_documents(myquery) == 0):  # User does not exist in database, give help command
        await ctx.send('No Resin available. Use -set to input Resin or -help for commands.')

    else:                                           # User exists in database, display current resin
        query = {'_id': ctx.author.id}
        user = collection.find({}, {'_id': 0, 'resin': 1, 'reminder': 0})

        for result in user:
            await ctx.send('You currently have ' + str(result[resin]) + ' Resin!')


# When: Shows remaning time left for Resin to refill at specified amount
# Calculated by taking Resin arg - current Resin and multiplies it by 8 to find remaining time
@bot.command()
async def when(ctx, arg : int):
    myquery = { '_id': ctx.author.id }

    if (collection.count_documents(myquery) == 0):  # User does not exist in database, give help command
        await ctx.send('No Resin available. Use -set to input Resin or -help for commands.')

    else:                                           # User exists in database, calculate time
        query = {'_id': ctx.author.id}
        user = collection.find(query)
        for result in user:
            resin = result['resin']
            reminder = result['reminder']

        filter = { '_id': ctx.author.id }
        updatedReminder = { "$set": { 'reminder': arg } }
        collection.update_one(filter, updatedReminder) 

        if arg < resin:
            await ctx.send('You already have ' + str(resin) + ' Resin!')

        elif arg in range (0,161):
            result = arg - resin

            # Time calculations
            duration = timedelta(minutes=(result) * 8)
            seconds = duration.total_seconds()
            hr = seconds // 3600
            min = (seconds % 3600) // 60

            await ctx.send('You will have %s Resin in %s hours and %s minutes.' % (str(arg), str(hr)[:-2], str(min)[:-2]))
   

# Refill: Adds a multiple of 60 to Resin amount
@bot.command()
async def refill(ctx, arg : int = 1):
    myquery = { '_id': ctx.author.id }

    if (collection.count_documents(myquery) == 0):  # User does not exist in database, give help command
        await ctx.send('No Resin available. Use -set to input Resin or -help for commands.')

    else:                                           # User exists in database, refill current resin
        query = {'_id': ctx.author.id}
        user = collection.find(query)
        for result in user:
            resin = result['resin']

        refill = 60 * arg
        resin += refill

        await ctx.invoke(bot.get_command('set'), arg=resin)


# Qoute: Displays a random Beidou quote to the user
@bot.command()
async def quote(ctx):
    line = random.choice(open('quotes.txt').readlines())
    await ctx.send(line)


# Help commands
@bot.group(invoke_without_command = True)
async def help(ctx):
    emb = discord.Embed(title = 'Help', description = 'Use -help <command> for more info on a command.', color = ctx.author.color)

    emb.add_field(name = 'Resin', value = 'set, check, when, refill')
    emb.add_field(name = 'Fun', value = 'quote')

    await ctx.send(embed = emb)


@help.command()
async def set(ctx):
    emb = discord.Embed(title = 'Set', description = 'Set current Resin amount', color = ctx.author.color)
    emb.add_field(name = '**Syntax**' , value = '-set <amount>')
    await ctx.send(embed = emb)


@help.command()
async def check(ctx):
    emb = discord.Embed(title = 'Check', description = 'Check current Resin amount', color = ctx.author.color)
    emb.add_field(name = '**Syntax**' , value = '-check')
    await ctx.send(embed = emb)


@help.command()
async def when(ctx):
    emb = discord.Embed(title = 'When', description = 'Show remaining time for specified Resin amount \n Notify user when Resin reaches <amount> and max', color = ctx.author.color)
    emb.add_field(name = '**Syntax**' , value = '-when <amount>')
    await ctx.send(embed = emb)


@help.command()
async def refill(ctx):
    emb = discord.Embed(title = 'Refill', description = 'Adds a multiple of 60 to Resin count', color = ctx.author.color)
    emb.add_field(name = '**Syntax**' , value = '-Refill <amount>')
    await ctx.send(embed = emb)


@help.command()
async def quote(ctx):
    emb = discord.Embed(title = 'Quote', description = 'Displays a random Beidou quote to the user', color = ctx.author.color)
    emb.add_field(name = '**Syntax**' , value = '-quote')
    await ctx.send(embed = emb)

bot.run(TOKEN)
