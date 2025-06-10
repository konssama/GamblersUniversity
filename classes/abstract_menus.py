import discord
from typing import List


class IntegerButtonView(discord.ui.View):  # this class is mostly claude
    def __init__(
        self,
        integers: List[int],
    ):
        super().__init__(timeout=180)
        # Create a button for each integer
        for integer in integers:
            button = discord.ui.Button(
                label=str(integer),
                style=discord.ButtonStyle.primary,
                custom_id=f"int_button_{integer}",
            )

            # Create the callback for this specific button
            async def button_callback(interaction: discord.Interaction, value=integer):
                await interaction.response.defer()
                return_message = self.on_click(value)
                await interaction.edit_original_response(
                    embed=discord.Embed(title=return_message, color=0x328FF2),
                    view=None,
                )

            button.callback = button_callback
            self.add_item(button)

        # Add cancel button after the integer buttons
        cancel_button = discord.ui.Button(
            label="Cancel",
            style=discord.ButtonStyle.danger,
            custom_id="cancel_button",
        )

        async def cancel_callback(interaction: discord.Interaction):
            embed = discord.Embed(
                title="Menu Cancelled",
                description="You cancelled the menu.",
                color=0xFF0000,
            )
            await interaction.response.edit_message(embed=embed, view=None)

        cancel_button.callback = cancel_callback
        self.add_item(cancel_button)

    def on_click(self, amount: int) -> str:
        return f"Un-overridden result Message {amount}"
