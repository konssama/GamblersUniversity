import os
import random
from datetime import datetime
import time
import discord

# from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from classes.sheets import generate_call_queues, push_set_queue, pop_get_queue
from classes.user import (
    UserAlreadyRegistered,
    generate_user_objects,
    get_user,
    register_user,
)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync()  # show bot / commands to the server commands
    print(f"{bot.user} is online")


@bot.event
async def on_member_join(member: discord.member.Member):
    try:  # !FIXME
        register_user(member.id)
    except UserAlreadyRegistered:
        pass
    print(f"{member.name} just joined the server!")


# @bot.event
# async def on_message(msg:discord.message.Message):
#     if msg.author.id != bot.user.id:
#         await msg.channel.send(f"yes {msg.author.mention}")


@bot.tree.command(
    name="register",
    description="Κάνε register τον εαυτό σου σε περίπτωση που μπήκες στον server όταν το bot ήταν κλειστό",
)
async def register(interaction: discord.Interaction):
    await interaction.response.defer()

    try:
        register_user(interaction.user.id)
        await interaction.response.send_message(
            f"Οκ τώρα είσαι αποθηκευμένος {interaction.user.mention}"
        )
    except UserAlreadyRegistered:
        await interaction.response.send_message(
            f"Ήσουν ήδη αποθηκευμένος {interaction.user.mention}"
        )


@bot.tree.command(name="balance", description="Δες πόσα χρήματα έχεις")
async def balance(interaction: discord.Interaction):
    await interaction.response.defer()

    user = get_user(interaction.user.id)
    await interaction.response.send_message(user.balance.get())


@bot.tree.command(name="cashout", description="Πάρε ό,τι λεφτά έχει μαζέψει το mining")
async def cashout(interaction: discord.Interaction):
    await interaction.response.defer()

    user = get_user(interaction.user.id)

    user.balance.add_to_get()
    user.last_cashout.add_to_get()
    current_balance, old_time = pop_get_queue()

    new_time: datetime = datetime.now().replace(microsecond=0)
    diff = (new_time - old_time).total_seconds()

    current_balance = diff * 2
    user.balance.next_value(current_balance)
    user.last_cashout.next_value(new_time)
    push_set_queue()

    await interaction.response.send_message(f"{current_balance}")


@bot.tree.command(name="coinflip", description="Διπλά ή τίποτα σε ό,τι βάλεις")
async def coinflip(interaction: discord.Interaction, amount: float):
    await interaction.response.defer()

    user = get_user(interaction.id)
    current_balance = user.balance.get()
    if amount > current_balance:
        await interaction.response.send_message(f"Μπρο δεν έχεις {amount}€")
        return

    if random.randrange(0, 2) == 0:
        user.balance.set(current_balance + amount * 2)
        await interaction.response.send_message(f"Κέρδισες {amount * 2}€")
    else:
        user.balance.set(current_balance - amount)
        await interaction.response.send_message(f"Έχασες {amount}€")


if __name__ == "__main__":
    start_time = time.time()

    gen_start = time.time()
    generate_call_queues()
    generate_user_objects()
    print(f"Heap gen took: {time.time() - gen_start:.4f}s")

    bot.run(TOKEN)
