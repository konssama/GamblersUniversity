import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from classes.sheets import CCell, register_user, UserAlreadyRegistered, generate_user_objects, get_user

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
async def on_member_join(member:discord.member.Member):
    try:
        register_user(member.id)
    except UserAlreadyRegistered:
        pass
    print(f"{member.name} just joined the server!")


# @bot.event
# async def on_message(msg:discord.message.Message):
#     if msg.author.id != bot.user.id:
#         await msg.channel.send(f"yes {msg.author.mention}")


@bot.tree.command(name="register", description="Κάνε register τον εαυτό σου σε περίπτωση που μπήκες στον server όταν το bot ήταν κλειστό")
async def register(interaction:discord.Interaction):
    try:
        register_user(interaction.user.id)
        await interaction.response.send_message(f"Οκ τώρα είσαι αποθηκευμένος {interaction.user.mention}")
    except UserAlreadyRegistered:
        await interaction.response.send_message(f"Ήσουν ήδη αποθηκευμένος {interaction.user.mention}")


@bot.tree.command(name="balance", description="Δες πόσα χρήματα έχεις")
async def register(interaction:discord.Interaction):
    stocks = {
        "TSL": 30,
        "CUM": 2,
        "MAGA": 9,
        "ELONMA": 12
    }
    cell = CCell(6,2)
    cell.set(stocks)
    print(cell.get_dict())

    user = get_user(interaction.user.id)
    await interaction.response.send_message(user.balance.get_float())


@bot.tree.command(name="coinflip", description="Double or nothing for your money")
async def coinflip(interaction:discord.Interaction):
    username = interaction.user.id
    await interaction.response.send_message(f"yo {username}")


generate_user_objects()
bot.run(TOKEN)