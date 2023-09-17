import discord
from discord.ext import commands
from typing import Union


class Paginator(discord.ui.View):
    def __init__(self, pages = [], single_user_only: bool = True, timeout: int = 180) -> None:
        super().__init__(timeout=timeout)
        if len(pages) == 1:
            self.page = pages[0]
        self.single_user_only = single_user_only
        self.pages = pages
        self.current_page = 0
        self.num_pages = len(pages)-1

    async def interaction_check(self, interaction):
        if self.single_user_only and interaction.user.id != self.starter_id:
            await interaction.response.defer()
            return False
        return True

    async def _update(self, interaction: discord.Interaction) -> discord.Message:
        await self._setup_buttons()
        self.page_indicator_button.label = f"{self.current_page+1}/{self.num_pages+1}"
        if isinstance(self.pages[self.current_page], discord.Embed):
            return await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)
        return await interaction.response.edit_message(content=self.pages[self.current_page], view=self)

    async def _setup_buttons(self) -> None:
        self.first_page_button.disabled = False
        self.previous_page_button.disabled = False
        self.next_page_button.disabled = False
        self.last_page_button.disabled = False

        if self.current_page in (0, 1):
            self.first_page_button.disabled = True

        if self.current_page == 0:
            self.previous_page_button.disabled = True
        
        if self.current_page == self.num_pages:
            self.next_page_button.disabled = True

        if self.current_page in (self.num_pages-1, self.num_pages):
            self.last_page_button.disabled = True
        

    async def start(self, context: Union[commands.Context, discord.Interaction]) -> discord.Message:
        if not isinstance(context, discord.Interaction) and not isinstance(context, commands.Context):
            raise TypeError("Paginator.start() only accepts discord.Interaction or commands.Context")
        if not getattr(self, "page", False):
            await self._setup_buttons()
        if isinstance(context, discord.Interaction):
            interaction = context
            self.starter_id = interaction.user.id
            if getattr(self, "page", False):
                if isinstance(self.page, discord.Embed):
                    return await interaction.edit_original_response(embed=self.page)
                  
                return await interaction.response.send_message(self.page)
            self.page_indicator_button.label = f"{self.current_page+1}/{self.num_pages+1}"
            if isinstance( [self.current_page], discord.Embed):
                return await interaction.edit_original_response(embed=self.pages[self.current_page], view=self)
            return await interaction.edit_original_response(embed=self.pages[self.current_page], view=self)
        ctx = context
        self.starter_id = ctx.author.id
        if getattr(self, "page", False):
            if isinstance(self.page, discord.Embed):
                return await ctx.send(embed=self.page)
            return await ctx.send(self.page)
        self.page_indicator_button.label = f"{self.current_page+1}/{self.num_pages+1}"
        if isinstance(self.pages[self.current_page], discord.Embed):
            return await ctx.send(embed=self.pages[self.current_page], view=self)
        return await ctx.send(self.pages[self.current_page], view=self)

    @discord.ui.button(label="<<", style=discord.ButtonStyle.blurple, disabled=True)
    async def first_page_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.current_page = 0
        await self._update(interaction)

    @discord.ui.button(label="<", style=discord.ButtonStyle.red, disabled=True)
    async def previous_page_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.current_page -= 1
        await self._update(interaction)

    @discord.ui.button(label="1/num", style=discord.ButtonStyle.grey)
    async def page_indicator_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        for button in self.children:
            button.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()

    @discord.ui.button(label=">", style=discord.ButtonStyle.green)
    async def next_page_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.current_page += 1
        await self._update(interaction)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.blurple)
    async def last_page_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.current_page = self.num_pages
        await self._update(interaction)

