TELEGRAM_BOT_TOKEN = '7188314998:AAHBEQ4qyEF8t_B8dsbZ-BZIcVoNFTqevFU' # Replace your_bot_token_here
ADMIN_USER_IDS = {959151693}  # Replace with actual admin user IDs

#Telegram DDoS Bot
A Python-based Telegram bot designed for educational purposes to simulate load testing on a specified IP address and port. The bot includes commands for starting and stopping attacks, as well as managing authorized users.

# Features
/start: Sends a welcome message to users.
/stop: Stops any ongoing attack.
/attack <IP> <port> <time_seconds> <threads>: Starts a load test on the specified IP address and port.
/adduser <user_id> <authorization_period>: Adds a user to the authorized list with a specific authorization period.
/removeuser <user_id>: Removes a user from the authorized list.

# Requirements
Python 3
python-telegram-bot
requests

# Installation
Clone the Repository
bash
Copy code
git clone https://github.com/bhikandeshmukh/TeleDDoSBot.git
cd TeleDDoSBot

# Install Dependencies
Run the Setup Script: Make sure the install.sh script is executable and run it to install the dependencies.
bash
Copy code
chmod +x install.sh
./install.sh
Configuration
Replace 'your_bot_token_here' in the script with your actual Telegram bot token. You can obtain this token by creating a bot via BotFather.

Update the ADMIN_USER_IDS in the script with the Telegram user IDs of admins who should have permission to use the /adduser and /removeuser commands.

Usage
Start the Bot:

bash
Copy code
python main.py
Bot Commands:

/start: Welcome message.
/stop: Stop any ongoing attack.
/attack <IP> <port> <time_seconds> <threads>: Start an attack.
/adduser <user_id> <authorization_period>: Add a user.
/removeuser <user_id>: Remove a user.
Permissions:

Only users listed in ADMIN_USER_IDS can use /adduser and /removeuser.

Running on Termux
Install Termux from Google Play Store or F-Droid.

Update Termux Packages:

bash
Copy code
pkg update
pkg upgrade
pkg install python
Install Dependencies:

bash
Copy code
pip install -r requirements.txt
Run the Bot:

bash
Copy code
python your_script_name.py
Contributing
Fork the repository.

Create a new branch:

bash
Copy code
git checkout -b feature-branch
Make your changes and commit:

bash
Copy code
git commit -am 'Add new feature'
Push to the branch:

bash
Copy code
git push origin feature-branch
Create a new Pull Request.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Disclaimer
This bot is intended for educational and testing purposes only. Misuse of this tool for unauthorized attacks on any system or network is illegal and unethical.