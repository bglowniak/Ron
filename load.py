import os
from ronald import Ron
from dotenv import load_dotenv
from discord.ext import commands

if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")

    bot = Ron(command_prefix=commands.when_mentioned_or("!"))
    bot.run(TOKEN)