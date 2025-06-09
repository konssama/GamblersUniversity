import os
import random
from datetime import datetime

import discord
# from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# from classes.sheets import CCell
from classes.user import (
    UserAlreadyRegistered,
    generate_user_objects,
    get_user,
    register_user,
    get_all_users,
)

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
    try: # !FIXME
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
async def balance(interaction:discord.Interaction):
    print(get_all_users())
    user = get_user(interaction.user.id)
    await interaction.response.send_message(user.balance.get_float())


@bot.tree.command(name="cashout", description="Πάρε ό,τι λεφτά έχει μαζέψει το mining")
async def cashout(interaction:discord.Interaction):
    user = get_user(interaction.user.id)
    user.last_cashout.set(datetime.now().replace(microsecond=0))
    print(user.last_cashout.get_time())

    await interaction.response.send_message(user.balance.get_float())


@bot.tree.command(name="coinflip", description="Διπλά ή τίποτα σε ό,τι βάλεις")
async def coinflip(interaction:discord.Interaction, amount:float):
    user = get_user(interaction.id)
    print(random.randrange(0,2))
    if amount > user.balance.get_float():
        await interaction.response.send_message(f"Μπρο δεν έχεις {amount}€")
        return

    if random.randrange(0,2) == 0:
        user.balance.set(user.balance.get_float() + amount*2)
        await interaction.response.send_message(f"Κέρδισες {amount*2}€")
    else:
        user.balance.set(user.balance.get_float() - amount)
        await interaction.response.send_message(f"Έχασες {amount}€")


generate_user_objects()
bot.run(TOKEN)