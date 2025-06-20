import os
import random
import time

import discord

from discord.ext import commands, tasks
from dotenv import load_dotenv

from library.functions.buy import handle_buy_command, BoughtItemNotFound
from library.menus import BuyMenu
from library.sheets import (
    generate_call_queues,
    pop_get_queue,
    push_set_queue,
    get_all_ids,
    new_backup,
)
from library.time_module import get_timestamp, schedule_time, calc_time_difference
from library.user import (
    UserAlreadyRegistered,
    generate_user_objects,
    get_user,
    register_user,
    get_all_users_sorted,
    get_all_users,
)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
is_prod = True if os.getenv("ENV") == "PROD" else False
TOKEN = (
    os.getenv("REAL_BOT_DISCORD_TOKEN")
    if is_prod
    else os.getenv("TEST_BOT_DISCORD_TOKEN")
)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync()  # show bot / commands to the server commands

    refresh_user_id.start()
    keep_backup.start()

    print(f"{bot.user} is online")


@bot.event
async def on_member_join(member: discord.member.Member):
    try:
        register_user(member.id, member.display_name)
    except UserAlreadyRegistered:
        pass
    print(f"{member.display_name} just joined the server!")


@tasks.loop(minutes=5)
async def keep_backup():
    backup_start = time.time()
    new_backup()
    print(
        f"Created new backup at: {get_timestamp()} and took {time.time() - backup_start:.4f}s"
    )


@tasks.loop(hours=1)
async def refresh_user_id():
    """Keeps the names updated if someone changes it and fixes the ids in case the database gets damaged."""

    users = get_all_users()
    for python_obj in users:
        discord_obj = bot.get_user(python_obj.user_id)
        if discord_obj is None:
            # if the user is not in discord's cache try fetching it form the server
            try:
                discord_obj = await bot.fetch_user(python_obj.user_id)
            except discord.NotFound:
                print(
                    f"User of id {python_obj.user_id}, supposed name {python_obj.name} was not found in discord"
                )
                continue

        python_obj.user_id = discord_obj.id  # same value but ig update it
        python_obj.name = discord_obj.display_name

        # if database id is wrong the cached id will fix it
        python_obj.id_cell.next_value(discord_obj.id)
        python_obj.name_cell.next_value(discord_obj.display_name)

    push_set_queue()
    print("User IDs and names were refreshed")


@bot.tree.command(
    name="register",
    description="Κάνε register τον εαυτό σου σε περίπτωση που μπήκες στον server όταν το bot ήταν κλειστό",
)
async def register(interaction: discord.Interaction):
    await interaction.response.defer()

    try:
        register_user(interaction.user.id, interaction.user.display_name)
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
    await interaction.followup.send(f"Έχεις {user.balance.get()}€")


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
    user.last_activity.next_value(get_timestamp())
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
        user.balance.next_value(current_balance + amount)
        await interaction.followup.send(f"Κέρδισες {amount * 2}€")
    else:
        user.balance.next_value(current_balance - amount)
        await interaction.followup.send(f"Έχασες {amount}€")

    user.last_activity.next_value(get_timestamp())
    push_set_queue()


@bot.tree.command(name="buy", description="Κάνε αγορές")
async def buy(interaction: discord.Interaction, item: str = "", amount: int = -1):
    await interaction.response.defer()

    user = get_user(interaction.user.id)
    user.last_activity.set(get_timestamp())

    if item == "":
        embed = discord.Embed(title="Αγορές", description="Μέσο Lidl", color=0x328FF2)
        view = BuyMenu(user)
        await interaction.followup.send(embed=embed, view=view)
        return  # let the menu handle everything

    if amount <= 0:
        amount = 1
    try:
        msg = handle_buy_command(user, item, amount)
        color = 0x328FF2
    except BoughtItemNotFound:
        msg = f"Τι εννοείς {item};"
        color = 0xFF0000

    embed = discord.Embed(title=msg, color=color)
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="leaderboard", description="Δες τις κατατάξεις")
async def leaderboard(interaction: discord.Interaction):
    await interaction.response.defer()

    users = get_all_users_sorted(key="balance")
    for user in users:
        user.balance.queue_value()

    balances = pop_get_queue()

    print_str = ""

    for i in range(len(users)):
        print_str += f"{i + 1}. {users[i].name}: {balances[i]}€\n"

    embed = discord.Embed(title="Leaderboard", description=print_str, color=0x328FF2)
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="debug_me", description="Δείξε debug info")
async def debug_me(interaction: discord.Interaction):
    await interaction.response.defer()
    debug_str = ""
    debug_str += f"Discord ID: {interaction.user.id}\n"
    debug_str += f"Discord name: {interaction.user.name}\n"
    if str(interaction.user.id) in get_all_ids():
        debug_str += "User is in sheets\n"
    else:
        debug_str += "User is not in sheets\n"
    debug_str += f"Channel ID: {interaction.channel_id}\n"
    debug_str += f"Guild ID: {interaction.guild_id}\n"
    await interaction.followup.send(debug_str)


@bot.tree.command(name="debug", description="Debug Info")
@commands.has_role("Admin")  # ! i think this doesn't work
async def debug(interaction: discord.Interaction):
    await interaction.response.send_message("pp")


if __name__ == "__main__":
    start_time = time.time()

    gen_start = time.time()
    generate_call_queues()
    generate_user_objects()
    print(f"Heap gen took: {time.time() - gen_start:.4f}s")

    bot.run(TOKEN)
