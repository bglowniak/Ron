import discord
from discord.ext.commands import Bot, command, CommandNotFound
from dotenv import load_dotenv
import os
import logging
import praw
import random

class Ron(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%H:%M:%S')

        load_dotenv()
        self.reddit = praw.Reddit(
            client_id = os.getenv("REDDIT_ID"),
            client_secret = os.getenv("REDDIT_SECRET"),
            user_agent = "Discord bot script"
        )

        self.add_command(self.deepdives)

        # https://deeprockgalactic.gamepedia.com/Voicelines
        self.drg_salutes = ["Rock on!", "Rock and stone.. Yeeaaahhh!", "Rock and stone forever!",
                            "ROCK... AND... STONE!", "Rock and stone!", "For rock and stone!",
                            "We are unbreakable!", "Rock and roll!", "Stone and rock!",
                            "Rock and roll and stone!", "That's it lads! Rock and stone!",
                            "Like that! Rock and stone!", "Yeaahhh! Rock and stone!",
                            "None can stand before us!", "Rock solid!", "Stone and rock! Oh wait...",
                            "Come on guys! Rock and stone!", "If you don't rock and stone, you ain't comin' home!",
                            "We fight for rock and stone!", "We rock!", "Rock and stone everyone!", "Stone!",
                            "Yeah yeah, rock and stone.", "Rock and stone in the heart!", "For teamwork!",
                            "Did I hear a rock and stone?"]

    #################################    EVENTS    #################################

    async def on_ready(self):
        logging.info(f'{self.user} has connected to Discord!')

    # override on_message to implement some functionality outside of normal commands
    async def on_message(self, message):
        if message.author == self.user or message.author.bot:
            return

        content = message.content.strip().lower()
        author_mention = "<@!" + str(message.author.id) + ">"

        if "rock and stone" in content or "for karl" in content:
            logging.info(f"Responding with salute to \"{message.content}\" sent by {message.author}")
            response = author_mention + " " + random.choice(self.drg_salutes)
            await message.channel.send(response)

        # once we have checked the full message, process any commands that may be present
        await self.process_commands(message)

    # add help command functionality at some point
    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            logging.warning(f"Command in message \"{ctx.message.content}\" not found. Ignoring.")
            return
        raise error

    #################################    COMMANDS    #################################

    @command(name="deepdives", pass_context=True, aliases=["dd", "dds", "deepdive"])
    async def deepdives(ctx):
        logging.info("Collecting weekly deep dives from Reddit.")

        reddit = ctx.bot.reddit

        if reddit is None:
            logging.error("Reddit session not available.")
            await ctx.send("Sorry, seems like I'm unable to connect to Reddit.")

        subreddit = reddit.subreddit("DeepRockGalactic")

        # Deep Dive Thread is stickied so it will always be in the first few posts of Hot
        deep_dive_message = ""
        for submission in subreddit.hot(limit=5):
            if submission.stickied and "Weekly Deep Dives Thread" in submission.title:
                url = submission.url
                content = submission.selftext.split("\n")
                idx = 0
                while idx < len(content):
                    line = content[idx]
                    if line.startswith("**Deep Dive**") or line.startswith("**Elite Deep Dive**"):
                        try:
                            deep_dive_message += ctx.bot.format_deep_dive(content[idx], content[idx + 4:idx + 7]) + "\n"
                        except IndexError as e:
                            logging.error("Deep dive post was found, but there was an error while parsing. Reddit post may not be formatted normally.")
                            logging.error(f"Error was \"{e}\" in format_deep_dive()")
                            await ctx.send("Hmm, seems like I ran into a problem parsing the deep dives thread. The error has been logged.")
                            return
                        idx += 8 # don't need to process the next few lines
                    else:
                        idx += 1

        if deep_dive_message.strip() == "":
            logging.error("Deep dive post was not found.")
            await ctx.send("Hmm, seems like I wasn't able to find the Weekly Deep Dives thread.")
        else:
            logging.info("Deep dives successfully retrieved. Sending message.")
            deep_dive_message = "Hey there, this is what I found from r/DeepRockGalactic:\n" + deep_dive_message + f"\n<{url}>"
            await ctx.send(deep_dive_message)

    #################################    HELPERS    #################################

    # Deep Dives are formatted as a table within the original Reddit post
    # info_line is the table header formatted as "Deep Dive Type | Name | Location"
    # stages are the three table rows formatted each as "| Stage # | Primary | Secondary | Anomalies | Warning |"
    def format_deep_dive(self, info_line, stages):
        deep_dive_info = "\n" + info_line
        for index, stage in enumerate(stages):
            parts = [s.strip() for s in stage.split("|")]
            deep_dive_info += f"\nStage {index + 1} | {parts[2]}, {parts[3]} | {parts[4]} | {parts[5]}"

        return deep_dive_info