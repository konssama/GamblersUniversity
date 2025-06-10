import discord
from classes.user import User
from classes.sheets import pop_get_queue, push_set_queue
from classes.abstract_menus import IntegerButtonView


class BuyMenu(discord.ui.View):
    def __init__(self, user: User):
        self.user: User = user
        super().__init__(timeout=180)  # Menu expires after 180 seconds

    @discord.ui.button(label="GPUs", style=discord.ButtonStyle.primary)
    async def gpu(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="GPUs",
            description="Αγόρασε GPUs για περισσότερο mining.",
            color=0x328FF2,
        )
        view = GpuMenu(self.user)

        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Menu Cancelled",
            description="You cancelled the menu.",
            color=0xFF0000,
        )
        await interaction.response.edit_message(embed=embed, view=None)

    async def on_timeout(self):
        # !FIXME claude hallucinated item.disabled
        for item in self.children:
            item.disabled = True


class GpuMenu(IntegerButtonView):
    def __init__(self, user: User):
        self.user: User = user
        super().__init__([1, 2, 5])  # Menu expires after 180 seconds

    def on_click(self, amount: int) -> str:
        gpu_price = 100.0

        self.user.gpu_count.queue_value()
        self.user.balance.queue_value()
        gpus, current_balance = pop_get_queue()

        if gpu_price * amount > current_balance:
            return "Δεν έχεις αρκετά χρήματα"

        gpus += amount
        current_balance -= gpu_price * amount

        if gpus > 10:
            # return without pushing to database
            return "Μπορείς να έχεις μόνο μέχρι 10 gpu."

        self.user.gpu_count.next_value(gpus)
        self.user.balance.next_value(current_balance)
        push_set_queue()

        return f"Όκε έχεις {gpus} gpu."
