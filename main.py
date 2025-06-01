import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from base import CCell

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync() #show bot / commands to the server commands
    print(f"{bot.user} is online")


@bot.event
async def on_message(msg:discord.message.Message):
    if msg.author.id != bot.user.id:
        await msg.channel.send(f"yes {msg.author.mention}")


@bot.tree.command(name="coinflip", description="Double or nothing for your money")
async def coinflip(interaction:discord.Interaction):
    username = interaction.user.id
    await interaction.response.send_message(f"yo {username}")


bot.run(TOKEN)