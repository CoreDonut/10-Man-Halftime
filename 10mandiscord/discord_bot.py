import discord
from discord.ext import commands
import json
import asyncio
from halftime import HalftimeManager

# Load configuration and player data
with open("config.json", "r") as config_file:
    config = json.load(config_file)
TOKEN = config["TOKEN"]  # Ensure this is a valid token
CHANNEL_ID = config["CHANNEL_ID"]  # Ensure this is a valid channel ID

class DiscordBot:
    def __init__(self):
        # Initialize bot with intents
        intents = discord.Intents.default()
        intents.voice_states = True  # Allows the bot to move users between voice channels
        intents.guilds = True
        intents.members = True  # Required for fetching members
        self.bot = commands.Bot(command_prefix="!", intents=intents)

        # Initialize HalftimeManager
        self.halftime_manager = HalftimeManager(self.bot)

        # Register events and commands
        self.bot.event(self.on_ready)
        self.bot.add_command(self.announce)  # Register the announce command

    async def on_ready(self):
        """Event triggered when the bot is ready."""
        print(f'Logged in as {self.bot.user}')

    async def send_teams(self, teams, final_map, coinflip_winner):
        """Send the selected teams, final map, and coin flip winner to the specified channel."""
        channel = self.bot.get_channel(CHANNEL_ID)
        if channel:
            message = (
                f"**Team 1:** {', '.join(teams['Team 1'])}\n"
                f"**Team 2:** {', '.join(teams['Team 2'])}\n"
                f"**Final Map:** {final_map}\n"
                f"**Coin Flip Winner:** {coinflip_winner}"
            )
            await channel.send(message)
        else:
            print("Error: Channel not found.")

    async def send_match_details(self, match_data):
        """Send match details to the specified Discord channel."""
        await self.send_teams(
            match_data["team1"],
            match_data["map"],
            match_data["coin_flip_winner"]
        )

    @commands.command(name="announce")
    async def announce(self, ctx):
        """Manually trigger an announcement of the teams and map."""
        try:
            with open("game_data.json", "r") as game_file:
                game_data = json.load(game_file)
            
            await self.send_teams(
                game_data["teams"],
                game_data["final_map"],
                game_data["coinflip_winner"]
            )
        except Exception as e:
            await ctx.send(f"Error retrieving game data: {e}")

    def run_bot(self):
        """Run the Discord bot in a non-blocking way."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.bot.start(TOKEN))