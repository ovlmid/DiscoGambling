#Imports
import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
#Setup bot
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

#Loading cogs
async def load():
  for file in os.listdir('./cogs'):
    if file.endswith('.py'):
      await bot.load_extension(f'cogs.{file[:-3]}')

#Calling loading cogs
async def main():
  await load()
  await bot.start(os.getenv("TOKEN"))

#Run bot
asyncio.run(main())