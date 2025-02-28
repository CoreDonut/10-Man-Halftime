import json
from pynput import keyboard

class HalftimeManager:
    def __init__(self, bot, config_file="player_data.json"):
        self.bot = bot
        self.config_file = config_file
        self.team_channels = {}  # Stores player ID to voice channel mapping
        self.lobby_channel = None
        self.halftime_active = False
        self.toggle_state = False
        self.load_config()
        
        # Setup key listener
        listener = keyboard.Listener(on_press=self.on_key_press)
        listener.start()
    
    def load_config(self):
        """Load player data from JSON."""
        try:
            with open(self.config_file, "r") as file:
                data = json.load(file)
                self.lobby_channel = data.get("lobby_channel", None)
        except FileNotFoundError:
            print("Config file not found. Creating a new one.")
            self.save_config()
    
    def save_config(self):
        """Save player data to JSON."""
        with open(self.config_file, "w") as file:
            json.dump({"lobby_channel": self.lobby_channel}, file, indent=4)
    
    async def assign_teams(self, teams):
        """Assign players to their respective voice channels."""
        self.team_channels.clear()
        for team, players in teams.items():
            for player_id in players:
                member = self.bot.get_guild().get_member(player_id)
                if member:
                    self.team_channels[player_id] = team
                    await member.move_to(team)  # Move player to team channel
    
    async def move_to_lobby(self):
        """Move all players to the lobby during halftime."""
        if not self.lobby_channel:
            print("Lobby channel is not set.")
            return
        for player_id, channel in self.team_channels.items():
            member = self.bot.get_guild().get_member(player_id)
            if member:
                await member.move_to(self.lobby_channel)
        self.halftime_active = True
        
    async def return_to_teams(self):
        """Return players to their assigned team channels after halftime."""
        for player_id, channel in self.team_channels.items():
            member = self.bot.get_guild().get_member(player_id)
            if member:
                await member.move_to(channel)
        self.halftime_active = False
    
    async def toggle_lobby(self):
        """Toggle moving all players to the lobby and back."""
        if self.toggle_state:
            await self.return_to_teams()
        else:
            await self.move_to_lobby()
        self.toggle_state = not self.toggle_state
    
    def on_key_press(self, key):
        """Listen for key presses to trigger halftime actions."""
        try:
            if key.char == 'h':  # Move to halftime
                self.bot.loop.create_task(self.move_to_lobby())
            elif key.char == 't':  # Toggle lobby mode
                self.bot.loop.create_task(self.toggle_lobby())
        except AttributeError:
            pass