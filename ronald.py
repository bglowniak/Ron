import discord
from discord.ext.commands import Bot, command, Cog

class Ron(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_command(self.placeholder)

    # EVENTS
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    # override on_message to implement some functionality outside of normal commands
    async def on_message(self, message):
        if message.author == self.user or message.author.bot:
            return

        content = message.content.strip().lower()
        author_mention = "<@!" + str(message.author.id) + ">"

        if content == "hello":
            await message.channel.send("salve")

        # once we have checked the full message, process any commands that may be present
        await self.process_commands(message)

    # COMMANDS
    @command(name="placeholder")
    async def placeholder(ctx, arg1, *args):
        pass

    # HELPERS