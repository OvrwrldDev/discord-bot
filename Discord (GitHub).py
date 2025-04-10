import discord
from discord.ext import commands
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import filedialog

# --- Bot Config ---
TOKEN = 'TOKEN HERE'
GUILD_ID = 123456789101112  # Replace with your actual server ID
CHANNEL_NAME = 'CHANNEL NAME HERE'  # Replace with your channel name

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# --- Folder Watcher Handler ---
class FolderEventHandler(FileSystemEventHandler):
    def __init__(self, root_path, send_change_message):
        self.root_path = root_path
        self.send_change_message = send_change_message

    def get_relative_path(self, full_path):
        return os.path.relpath(full_path, self.root_path).replace("\\", "/")

    def on_created(self, event):
        if not event.is_directory:
            rel_path = self.get_relative_path(event.src_path)
            self.send_change_message(f"📂 File added: `{rel_path}`")

    def on_deleted(self, event):
        if not event.is_directory:
            rel_path = self.get_relative_path(event.src_path)
            self.send_change_message(f"🗑️ File removed: `{rel_path}`")

observer = Observer()

# --- Discord Events ---
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user.name}")

    await bot.wait_until_ready()

    guild = discord.utils.get(bot.guilds, id=GUILD_ID)
    if guild is None:
        print("❌ ERROR: Guild (server) not found. Check GUILD_ID.")
        return

    channel = discord.utils.get(guild.text_channels, name=CHANNEL_NAME)
    if channel is None:
        print("❌ ERROR: Channel not found. Check CHANNEL_NAME.")
        return

    def send_change_message(msg):
        bot.loop.create_task(channel.send(msg))

    # File picker
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select folder to monitor")

    if folder_path:
        print(f"👀 Watching: {folder_path} and subfolders")
        event_handler = FolderEventHandler(folder_path, send_change_message)
        observer.schedule(event_handler, path=folder_path, recursive=True)
        observer.start()
    else:
        print("❌ No folder selected. Exiting...")
        await bot.close()

# --- Start Bot ---
bot.run(TOKEN)
