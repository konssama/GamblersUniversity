import discord
from library.user import User
from library.abstract_menus import IntegerButtonView
from library.functions.buy import buy_gpus


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
            # item.disabled = True
            pass

            # self.clear_items()  # % maybe this is the method we need?
            # * WARNING also this should probably be in all View subclasses cause View's on_timeout() just passes?
            # bro i have 3 comments in 3 lines of code that do nothing smh,
            # that's what i get for vibe coding


class GpuMenu(IntegerButtonView):
    def __init__(self, user: User):
        self.user: User = user
        super().__init__([1, 2, 5])

    def on_click(self, amount: int) -> str:
        msg = buy_gpus(self.user, amount)
        return msg
