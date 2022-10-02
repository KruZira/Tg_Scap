from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import InviteToChannelRequest
import configparser
import os
import sys
import csv
import traceback
import time
import random

red="\033[1;31m"
green="\033[1;32m"
cyan="\033[1;36m"

print (red+"NOTE :")
print ("1. Telegram only allow to add 200 members in group by one user.")
print ("2. You can Use multiple Telegram accounts to add more members.")
print ("3. Add only 50 members in group each time otherwise you will get flood error.")
print ("4. Then wait for 15-30 miniute then add members again.")
print ("5. Make sure you enable Add User Permission in your group")

cpass = configparser.RawConfigParser()
cpass.read('config.data')

try:
    api_id = cpass['cred']['id']
    api_hash = cpass['cred']['hash']
    phone = cpass['cred']['phone']
    client = TelegramClient(phone, api_id, api_hash)
except KeyError:
    os.system('clear')
    print(red+"[!] run python setup.py first !!\n")
    sys.exit(1)

client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone)
    os.system('clear');banner()
    client.sign_in(phone, input(green+'[+] Enter the code: '+red))

users = []
with open(r"members.csv", encoding='UTF-8') as f:  #Enter your file name
    rows = csv.reader(f,delimiter=",",lineterminator="\n")
    next(rows, None)
    for row in rows:
        user = {}
        user['username'] = row[0]
        user['id'] = int(row[1])
        user['access_hash'] = int(row[2])
        user['name'] = row[3]
        users.append(user)

chats = []
last_date = None
chunk_size = 200
groups = []

result = client(GetDialogsRequest(
    offset_date=last_date,
    offset_id=0,
    offset_peer=InputPeerEmpty(),
    limit=chunk_size,
    hash=0
))
chats.extend(result.chats)

for chat in chats:
    try:
        if chat.megagroup == True:
            groups.append(chat)
    except:
        continue

print(green+'Choose a group to add members:'+cyan)
i = 0
for group in groups:
    print(str(i) + '- ' + group.title)
    i += 1

g_index = input(green+"Enter a Number: "+red)
target_group = groups[int(g_index)]

target_group_entity = InputPeerChannel(target_group.id, target_group.access_hash)

mode = int(input(green+"Enter 1 to add by username or 2 to add by ID: "+cyan))

n = 0

for user in users:
    n += 1
    if n % 80 == 0:
        sleep(60)
    try:
        print("Adding {}".format(user['id']))
        if mode == 1:
            if user['username'] == "":
                continue
            user_to_add = client.get_input_entity(user['username'])
        elif mode == 2:
            user_to_add = InputPeerUser(user['id'], user['access_hash'])
        else:
            sys.exit("Invalid Mode Selected. Please Try Again.")
        client(InviteToChannelRequest(target_group_entity, [user_to_add]))
        print("sleeping 5 secs")
        time.sleep(5)
    except PeerFloodError as error:
        print("Getting Flood Error from telegram. Please try again after some time.")
        print("Waiting 14 mins To Get pass ->    {error}")
        time.sleep(840)
    except UserPrivacyRestrictedError:
        print("The user's privacy settings do not allow you to do this. Skipping.")
        print("Waiting for 5 Seconds...")
        time.sleep(random.randrange(0, 5))
    except:
        traceback.print_exc()
        print("Unexpected Error")
        continue
