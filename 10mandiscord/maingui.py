import json
import random
import tkinter as tk
from tkinter import messagebox
from halftime import HalftimeManager
from discord_bot import DiscordBot
import threading

print("maingui.py is running...")

# Load player data from JSON
try:
    with open("players.json", "r") as file:
        PLAYERS = json.load(file)
except FileNotFoundError:
    messagebox.showerror("Error", "players.json file not found!")
    exit()
except json.JSONDecodeError:
    messagebox.showerror("Error", "players.json is not a valid JSON file!")
    exit()

# Load map data from JSON
try:
    with open("maps.json", "r") as file:
        MAP_POOLS = json.load(file)
except FileNotFoundError:
    messagebox.showerror("Error", "maps.json file not found!")
    exit()
except json.JSONDecodeError:
    messagebox.showerror("Error", "maps.json is not a valid JSON file!")
    exit()

class MainGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("10 Man Match Setup")
        self.root.geometry("800x800")
    
        # Initialize DiscordBot
        self.discord_bot = DiscordBot()

        # Initialize HalftimeManager
        self.halftime_manager = self.discord_bot.halftime_manager
    
        # Start the Discord bot in a separate thread
        discord_thread = threading.Thread(target=self.discord_bot.run_bot, daemon=True)
        discord_thread.start()
        
        self.selected_players = {}
        self.team1 = []
        self.team2 = []
        self.current_map_pool = "Active Duty"
        self.available_maps = MAP_POOLS[self.current_map_pool][:]
        
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.root, text="Select Players (10 max):").pack()
        self.player_frame = tk.Frame(self.root)
        self.player_frame.pack()
        
        self.selection_label = tk.Label(self.root, text="Selected: 0/10")
        self.selection_label.pack()
        
        self.checkboxes = {}
        for player in PLAYERS:
            var = tk.IntVar()
            chk = tk.Checkbutton(self.player_frame, text=player, variable=var, command=self.update_selection)
            chk.pack(anchor="w")
            self.selected_players[player] = var
            self.checkboxes[player] = chk
        
        self.generate_button = tk.Button(self.root, text="Generate Teams", command=self.generate_teams)
        self.generate_button.pack()
        
        self.team1_label = tk.Label(self.root, text="Team 1:")
        self.team1_label.pack()
        self.team2_label = tk.Label(self.root, text="Team 2:")
        self.team2_label.pack()
        
        self.map_ban_button = tk.Button(self.root, text="Proceed to Map Ban", state=tk.DISABLED, command=self.map_ban)
        self.map_ban_button.pack()
        
        self.coin_flip_button = tk.Button(self.root, text="Flip Coin", command=self.coin_flip, state=tk.DISABLED)
        self.coin_flip_button.pack()
        
        self.final_map_label = tk.Label(self.root, text="Final Map:")
        self.final_map_label.pack()

    def update_selection(self):
        selected_count = sum(var.get() for var in self.selected_players.values())
        self.selection_label.config(text=f"Selected: {selected_count}/10")
        for player, var in self.selected_players.items():
            if selected_count >= 10 and var.get() == 0:
                self.checkboxes[player].config(state=tk.DISABLED)
            else:
                self.checkboxes[player].config(state=tk.NORMAL)

    def generate_teams(self):
        active_players = [p for p, var in self.selected_players.items() if var.get() == 1]
        if len(active_players) != 10:
            messagebox.showwarning("Invalid Selection", "Please select exactly 10 players.")
            return
        
        random.shuffle(active_players)
        self.team1, self.team2 = active_players[:5], active_players[5:]
        
        self.team1_label.config(text=f"Team 1: {', '.join(self.team1)}")
        self.team2_label.config(text=f"Team 2: {', '.join(self.team2)}")
        self.map_ban_button.config(state=tk.NORMAL)
        
    def map_ban(self):
        if len(self.available_maps) <= 1:
            self.final_map_label.config(text=f"Final Map: {self.available_maps[0]}")
            self.coin_flip_button.config(state=tk.NORMAL)
            return
        
        banning_team = "Team 1" if random.randint(0, 1) == 0 else "Team 2"
        map_to_ban = random.choice(self.available_maps)
        self.available_maps.remove(map_to_ban)
        
        messagebox.showinfo("Map Ban", f"{banning_team} bans {map_to_ban}. Remaining maps: {', '.join(self.available_maps)}")
        
        if len(self.available_maps) > 1:
            self.map_ban()
        
    def coin_flip(self):
        winner = random.choice(["Team 1", "Team 2"])
        messagebox.showinfo("Coin Flip", f"{winner} wins the coin flip!")
        
        # Send match details to Discord
        match_data = {
            "team1": self.team1,
            "team2": self.team2,
            "map": self.available_maps[0],
            "coin_flip_winner": winner
        }
        self.discord_bot.send_match_details(match_data)
        
        # Assign players to voice channels
        self.halftime_manager.assign_teams(self.team1, self.team2)

if __name__ == "__main__":
    # Create the Tkinter GUI
    root = tk.Tk()
    gui = MainGUI(root)
    
    # Start the Tkinter main loop
    root.mainloop()