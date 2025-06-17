import os
import random
import time

import discord

# from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv

from library.menus import BuyMenu
from library.sheets import (
    generate_call_queues,
    pop_get_queue,
    push_set_queue,
    get_all_ids,
)
from library.time_module import get_timestamp, schedule_time, calc_time_difference
from library.user import (
    UserAlreadyRegistered,
    generate_user_objects,
    get_user,
    register_user,
)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
# intents.members = True # !FIXME add members permission in dev portal
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync()  # show bot / commands to the server commands

    refresh_user_id.start()

    print(f"{bot.user} is online")


@bot.event
async def on_member_join(member: discord.member.Member):
    try:  # !FIXME need to add members intent in the discord developers website
        register_user(member.id, member.name)
        # register_user(member._user.id)  # % _user may be a fix? not tested
    except UserAlreadyRegistered:
        pass
    print(f"{member.name} just joined the server!")


# @bot.event
# async def on_message(msg:discord.message.Message):
#     if msg.author.id != bot.user.id:
#         await msg.channel.send(f"yes {msg.author.mention}")


@tasks.loop(hours=1)
async def refresh_user_id():
    """Keeps the names updated if someone changes it and fixed the ids in case the database gets damaged."""

    ids = get_all_ids()
    for id in ids:
        discord_obj = bot.get_user(id)
        if discord_obj is None:
            # if the user is not in discord's cache try fetching it form the server
            try:
                discord_obj = await bot.fetch_user(id)
            except discord.NotFound:
                print(f"User of id {id} was not found in discord")
                continue

        python_obj = get_user(id)

        python_obj.user_id = discord_obj.id  # same value but ig update it
        python_obj.name = discord_obj.name
        python_obj.id_cell.next_value(discord_obj.id)
        python_obj.name_cell.next_value(discord_obj.name)

    push_set_queue()
    print("User IDs and names were refreshed")


@bot.tree.command(
    name="register",
    description="Κάνε register τον εαυτό σου σε περίπτωση που μπήκες στον server όταν το bot ήταν κλειστό",
)
async def register(interaction: discord.Interaction):
    await interaction.response.defer()

    try:
        register_user(interaction.user.id, interaction.user.name)
        await interaction.followup.send(
            f"Οκ τώρα είσαι αποθηκευμένος {interaction.user.mention}"
        )
    except UserAlreadyRegistered:
        await interaction.followup.send(
            f"Ήσουν ήδη αποθηκευμένος {interaction.user.mention}"
        )


@bot.tree.command(name="balance", description="Δες πόσα χρήματα έχεις")
async def balance(interaction: discord.Interaction):
    await interaction.response.defer()

    user = get_user(interaction.user.id)
    await interaction.followup.send(user.balance.get())


@bot.tree.command(name="cashout", description="Πάρε ό,τι λεφτά έχει μαζέψει το mining")
async def cashout(interaction: discord.Interaction):
    await interaction.response.defer()

    user = get_user(interaction.user.id)

    user.balance.queue_value()
    user.last_cashout.queue_value()
    user.gpu_count.queue_value()
    current_balance, old_time, gpu_count = pop_get_queue()

    new_time = get_timestamp()
    diff = calc_time_difference(old_time, new_time)

    gain = round(diff * gpu_count * 0.06, 2)
    current_balance += gain
    current_balance = round(current_balance, 2)

    user.balance.next_value(current_balance)
    user.last_cashout.next_value(new_time)
    push_set_queue()

    await interaction.followup.send(f"+{gain}€ Σύνολο: {current_balance}€")


@bot.tree.command(name="coinflip", description="Διπλά ή τίποτα σε ό,τι βάλεις")
async def coinflip(interaction: discord.Interaction, amount: float):
    await interaction.response.defer()

    user = get_user(interaction.user.id)
    current_balance = user.balance.get()
    if amount > current_balance:
        await interaction.followup.send(f"Μπρο δεν έχεις {amount}€")
        return

    if random.randrange(0, 2) == 0:
        user.balance.set(current_balance + amount * 2)
        await interaction.followup.send(f"Κέρδισες {amount * 2}€")
    else:
        user.balance.set(current_balance - amount)
        await interaction.followup.send(f"Έχασες {amount}€")


@bot.tree.command(name="buy", description="Κάνε αγορές")
async def buy(interaction: discord.Interaction):
    await interaction.response.defer()

    embed = discord.Embed(title="Αγορές", description="Μέσο Lidl", color=0x328FF2)
    view = BuyMenu(get_user(interaction.user.id))

    await interaction.followup.send(embed=embed, view=view)


@bot.tree.command(name="debug", description="Debug Info")
@commands.has_role("Admin")
async def debug(interaction: discord.Interaction):
    await interaction.response.send_message("pp")


if __name__ == "__main__":
    start_time = time.time()

    gen_start = time.time()
    generate_call_queues()
    generate_user_objects()
    print(f"Heap gen took: {time.time() - gen_start:.4f}s")

    bot.run(TOKEN)
