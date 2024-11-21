import os
import discord
from discord.ext import commands
import random
import csv
import pandas as pd
from datetime import datetime
import pytz
import threading
import tkinter as tk
from tkinter import messagebox

quote = []  # Array for data to be stored in
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())  # Connecting to discord API

last_saved_file = ""
last_save_time = ""

# Function to start the bot in a separate thread
def start_bot():
    bot.run("OTYyOTMxNjcwODA0MjIyMDAy.G_l8WX.T1MI3_u0XNOWoJF5oMzMU6Hbd0519AXpAWU_8Q")

# Function to stop the bot
def stop_bot():
    loop = bot.loop
    loop.create_task(bot.close())  # Safely stop the bot within the event loop

# GUI functions
def update_last_saved_info():
    """Updates the labels showing the last saved file and time"""
    last_saved_label.config(text=f"Last save: {last_saved_file}")

def start_button_click():
    """Starts the bot in a new thread."""
    start_button.config(state=tk.DISABLED)  # Disable start button
    stop_button.config(state=tk.NORMAL)  # Enable stop button
    thread = threading.Thread(target=start_bot)
    thread.start()

def stop_button_click():
    """Stops the bot."""
    stop_bot()  # Stop the bot safely
    start_button.config(state=tk.NORMAL)  # Enable start button
    stop_button.config(state=tk.DISABLED)  # Disable stop button
    messagebox.showinfo("Bot Stopped", "The bot has been stopped.")
    root.destroy()

def fetch_random_quote():
    """Fetches a random quote and updates the quote text area"""
    global last_saved_file
    # Find the most recent Quotes file
    quotes_files = [f for f in os.listdir() if f.startswith("Quotes_") and f.endswith(".txt")]
    if not quotes_files:
        quote_text_area.delete(1.0, tk.END)
        quote_text_area.insert(tk.END, "No quotes file found.")
        return

    # Sort files by date extracted from filename in descending order to get the latest file
    quotes_files.sort(key=lambda f: datetime.strptime(f[7:-4], "%d_%m_%Y"), reverse=True)
    latest_file = quotes_files[0]
    last_saved_file = latest_file  # Update last saved file

    # Update last save time
    global last_save_time
    last_save_time = datetime.strptime(latest_file[7:-4], "%d_%m_%Y").strftime("%d-%m-%Y")
    
    # Read quotes from the latest file
    with open(latest_file, 'r', encoding='utf-8') as f:
        quotes = [line.strip() for line in f if line.strip()]

    # Select a random quote
    if quotes:
        chosen_quote = random.choice(quotes)
        print(chosen_quote)
        quote_text_area.configure(state=tk.NORMAL)
        quote_text_area.delete(1.0, tk.END)  # Clear any previous quote
        quote_text_area.insert(tk.END, chosen_quote)  # Insert the new quote
        quote_text_area.configure(state=tk.DISABLED)
    else:
        quote_text_area.delete(1.0, tk.END)
        quote_text_area.insert(tk.END, "No quotes available in the latest file.")

    # Update last saved file info
    update_last_saved_info()

# Bot event when the bot is ready
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    messagebox.showinfo("Bot Started", "The bot has started.")
    for guild in bot.guilds:
        print(guild.name)

    # Get the most recent Quotes file on bot startup
    quotes_files = [f for f in os.listdir() if f.startswith("Quotes_") and f.endswith(".txt")]
    if quotes_files:
        # Sort files by date extracted from filename in descending order to get the latest file
        quotes_files.sort(key=lambda f: datetime.strptime(f[7:-4], "%d_%m_%Y"), reverse=True)
        latest_file = quotes_files[0]
        global last_saved_file
        last_saved_file = latest_file  # Update last saved file

        # Extract the last saved date from the filename
        global last_save_time
        last_save_time = datetime.strptime(latest_file[7:-4], "%d_%m_%Y").strftime("%d-%m-%Y")

        # Update the GUI with the last saved info
        update_last_saved_info()

# Command to handle !boop
@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def boop(ctx):
    global last_saved_file
    # Find the most recent Quotes file
    quotes_files = [f for f in os.listdir() if f.startswith("Quotes_") and f.endswith(".txt")]
    if not quotes_files:
        await ctx.send("No quotes file found.")
        return

    # Sort files by date extracted from filename in descending order to get the latest file
    quotes_files.sort(key=lambda f: datetime.strptime(f[7:-4], "%d_%m_%Y"), reverse=True)
    latest_file = quotes_files[0]
    last_saved_file = latest_file  # Update last saved file

    # Update last save time
    global last_save_time
    last_save_time = datetime.strptime(latest_file[7:-4], "%d_%m_%Y").strftime("%d-%m-%Y")
    
    # Read quotes from the latest file
    with open(latest_file, 'r', encoding='utf-8') as f:
        quotes = [line.strip() for line in f if line.strip()]

    # Select a random quote
    if quotes:
        chosen_quote = random.choice(quotes)
        print(chosen_quote)
        await ctx.channel.send(chosen_quote)
    else:
        await ctx.send("No quotes available in the latest file.")
    
    # Update last saved file info
    update_last_saved_info()

# Command to handle !save
@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def save(ctx):
    global last_save_time
    # Delete the user's !save message
    await ctx.message.delete()

    print("Saving...")
    messages = []

    # Collect messages, filtering out bot commands, bot messages, and blank lines within each message
    async for msg in ctx.channel.history(limit=1000):
        if msg.content and not msg.content.startswith("!") and msg.author != bot.user:
            lines = [line.strip() for line in msg.content.splitlines() if line.strip()]
            if lines:
                cleaned_message = "\n".join(lines)
                messages.append(cleaned_message)

    # Get Australian Eastern Time (Sydney Time)
    aust_time = pytz.timezone('Australia/Sydney')
    current_date = datetime.now(aust_time).strftime("%d_%m_%Y")
    print(current_date)

    # Generate file name with current date
    file_location = f"Quotes_{current_date}.txt"

    # Write cleaned messages to the file
    with open(file_location, 'w', encoding='utf-8') as f:
        for message in messages:
            f.write(message + "\n")

    print("Successfully saved!")

    # Update last save time
    last_save_time = datetime.now(aust_time).strftime("%Y-%m-%d %H:%M:%S")
    update_last_saved_info()

    # Get the guild and channel using the provided IDs
    guild_id = 1306551380789432370
    channel_id = 1307684427828166756
    guild = bot.get_guild(guild_id)
    target_channel = guild.get_channel(channel_id)

    # Check if the channel was found and send the file
    if target_channel:
        with open(file_location, 'rb') as file:
            await target_channel.send("Here's the saved quotes file:", file=discord.File(file, file_location))

# GUI Setup
root = tk.Tk()
root.title("Discord Bot Control Panel")
root.geometry("350x400")  # Increased the height of the window

# Display last saved file and time
last_saved_label = tk.Label(root, text="Last save: None", font=("Arial", 12))
last_saved_label.pack(pady=10)

# Text area to show random quote
# Text area to show random quote (adjust width to not take up the entire space)
quote_text_area = tk.Text(root, height=5, width=40, font=("Arial", 12))  # Adjust width here
quote_text_area.pack(pady=10, padx=20)  # Adding padding to the sides to prevent it from stretching



# Button to get random quote
random_quote_button = tk.Button(root, text="Get Random Quote", font=("Arial", 14), command=fetch_random_quote)
random_quote_button.pack(pady=10)

# Start and Stop buttons
start_button = tk.Button(root, text="Start Bot", font=("Arial", 14), command=start_button_click)
start_button.pack(pady=20)

stop_button = tk.Button(root, text="Stop Bot", font=("Arial", 14), state=tk.DISABLED, command=stop_button_click)
stop_button.pack(pady=20)

# Start the GUI
root.mainloop()
