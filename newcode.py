# -*- coding: utf-8 -*-
import pyfiglet
import asyncio
import os
import uuid
import hashlib
import platform
import requests
import sys
import random
from colorama import init, Fore, Back, Style
from telethon import TelegramClient
from telethon.tl.functions.channels import (
    CreateChannelRequest,
    InviteToChannelRequest,
    JoinChannelRequest,
    LeaveChannelRequest,
    TogglePreHistoryHiddenRequest,
)
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.functions.account import GetPasswordRequest
from telethon.tl.types import ReactionEmoji
from telethon.errors import (
    SessionPasswordNeededError,
    UserAlreadyParticipantError,
    ChatNotModifiedError,
)
from telethon import functions

# Sozlamalar
API_ID = 22210367
API_HASH = '29a1097b9da5f9a6e8bafaaee6dc6ae4'
BOT_USERNAME = "tinglabot"
SESSIONS_DIR = "sessions"
API_KEY = "ishlakod"
SECRET_TOKEN = "kodishla"

if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

# Yordamchi funksiyalar
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_sessions():
    return [f.split('.')[0] for f in os.listdir(SESSIONS_DIR) if f.endswith('.session')]

ID_FILE = "device_id.txt"

# Hozir ishlayotgan fayl nomi (self-delete uchun)
SELF_FILE = os.path.abspath(__file__)

# Qurilmaga unikal ID yozib qo’yamiz
if not os.path.exists(ID_FILE):
    device_id = str(uuid.uuid4())
    with open(ID_FILE, "w") as f:
        f.write(device_id)
else:
    with open(ID_FILE, "r") as f:
        device_id = f.read().strip()

# Signature yaratamiz
signature = hashlib.sha256((device_id + SECRET_TOKEN).encode()).hexdigest()

# Serverga yuboramiz
url = "https://68f77a7f47cf9.myxvest1.ru/Termuxguruxkolar/Maxsusakga/secure_api.php"
params = {
    "api": API_KEY,
    "id": device_id,
    "signature": signature
}

response = requests.get(url, params=params)
server_msg = response.text.strip()

print("Server javobi:", server_msg)

#  Agar server OK demasa  o‘zini va ID faylni o‘chiradi
if server_msg != "OK":
    print("\n Ruxsat yo‘q! Kod va fayl o‘chirildi. @termux_os")

    # ID faylni o'chiramiz
    try:
        if os.path.exists(ID_FILE):
            os.remove(ID_FILE)
    except:
        pass

    # PY faylning o‘zini o‘chiradi
    try:
        os.remove(SELF_FILE)
    except:
        pass

    sys.exit()

# Hammasi OK
print("\n Ruxsat berildi! Kod ishlashda davom etmoqda...\n")

def list_accounts():
    clear_screen()
    sessions = get_sessions()
    print("=== FAOL AKKAUNTLAR ===")
    if not sessions:
        print("Hech qanday faol akkaunt yo'q!")
    else:
        for i, s in enumerate(sessions, 1):
            print(f"{i}. {s}")
    input("\nEnter bosing...")

# Hisob qo'shish
async def add_account():
    clear_screen()
    session_name = input("Yangi session nomi (masalan: user1): ").strip()
    if not session_name:
        print("Noto'g'ri nom!")
        input("\nEnter bosing...")
        return

    session_path = os.path.join(SESSIONS_DIR, session_name)
    client = TelegramClient(session_path, API_ID, API_HASH)

    try:
        await client.start()
        me = await client.get_me()
        print(f"\nMuvaffaqiyatli ulandi: {me.first_name} ({me.phone})")
    except Exception as e:
        print(f"Ulanishda xato: {e}")
    finally:
        await client.disconnect()
    input("\nEnter bosing...")

# Hisobni o'chirish
def delete_account():
    clear_screen()
    sessions = get_sessions()
    if not sessions:
        print("Hech qanday akkaunt mavjud emas!")
        input("\nEnter bosing...")
        return

    print("=== HISOBNI O'CHIRISH ===")
    for i, s in enumerate(sessions, 1):
        print(f"{i}. {s}")

    choice = input("\nO'chirmoqchi bo'lgan akkauntni tanlang (raqam): ").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(sessions):
            session_file = os.path.join(SESSIONS_DIR, sessions[idx] + ".session")
            os.remove(session_file)
            print(f"{sessions[idx]} muvaffaqiyatli o'chirildi!")
        else:
            print("Noto'g'ri raqam!")
    except Exception as e:
        print(f"Xatolik: {e}")
    input("\nEnter bosing...")

# Guruh yaratish
async def create_single_group(client: TelegramClient, group_number: int):
    try:
        print(f"  Guruh {group_number} yaratilmoqda...")
        result = await client(CreateChannelRequest(
            title=f'Avto Guruh {group_number}',
            about='@tinglabot qoshildi. Tarix ochiq!',
            megagroup=True
        ))
        channel = result.chats[0]
        print(f"  Guruh: {channel.title} (ID: {channel.id})")
        try:
            await client(TogglePreHistoryHiddenRequest(channel=channel, enabled=False))
        except ChatNotModifiedError:
            pass
        except Exception as e:
            print(f"    Tarix sozlamasi xato: {e}")
        try:
            bot = await client.get_entity(BOT_USERNAME)
            await client(InviteToChannelRequest(channel=channel, users=[bot]))
        except UserAlreadyParticipantError:
            pass
        except Exception as e:
            print(f"    Bot qo'shish xatosi: {e}")
        try:
            await client.send_message(channel, "Xush kelibsiz! Guruh tayyor!")
        except Exception as e:
            print(f"    Xabar yuborish xatosi: {e}")
    except Exception as e:
        print(f"  Guruh {group_number} yaratishda xato: {e}")

async def create_groups_for_single_account(session_name: str, num_groups: int, delay: float):
    session_path = os.path.join(SESSIONS_DIR, session_name)
    client = TelegramClient(session_path, API_ID, API_HASH)
    try:
        print(f"\n[{session_name}] Ulanmoqda...")
        await client.start()
        print(f"[{session_name}] Muvaffaqiyatli ulandi!")
        for i in range(1, num_groups + 1):
            await create_single_group(client, i)
            if i < num_groups and delay > 0:
                await asyncio.sleep(delay)
        print(f"[{session_name}] {num_groups} ta guruh yaratildi!")
    except Exception as e:
        print(f"[{session_name}] Umumiy xato: {e}")
    finally:
        await client.disconnect()

async def create_groups():
    clear_screen()
    sessions = get_sessions()
    if not sessions:
        print("Hech qanday akkaunt yo'q! Avval qo'shing.")
        input("\nEnter bosing...")
        return

    BLOCK_SIZE = 50
    blocks = [sessions[i:i + BLOCK_SIZE] for i in range(0, len(sessions), BLOCK_SIZE)]

    print("=== GURUH YARATISH ===")
    for i, s in enumerate(sessions, 1):
        print(f"{i}. {s}")

    print("\n--- 50 talik bloklar ---")
    for idx, block in enumerate(blocks, 1):
        print(f"{idx:02d}. Top {idx} ({len(block)} ta)")

    print(f"\n{len(sessions)+1}. BARCHASIDAN yaratish")

    choice = input("\nRaqam kiriting (01, 02... yoki barchasi): ").strip()

    if choice == str(len(sessions) + 1):
        selected = sessions
    elif choice.isdigit() and len(choice) == 2:
        block_idx = int(choice) - 1
        if 0 <= block_idx < len(blocks):
            selected = blocks[block_idx]
        else:
            print("Noto'g'ri blok raqam!")
            input("\nEnter bosing...")
            return
    else:
        try:
            choice_num = int(choice) - 1
            if 0 <= choice_num < len(sessions):
                selected = [sessions[choice_num]]
            else:
                print("Noto'g'ri akkaunt raqam!")
                input("\nEnter bosing...")
                return
        except ValueError:
            print("Raqam kiriting!")
            input("\nEnter bosing...")
            return

    try:
        num_groups = int(input("\nNechta guruh yaratmoqchisiz? "))
        if num_groups <= 0:
            raise ValueError
    except Exception:
        print("Musbat son kiriting!")
        input("\nEnter bosing...")
        return

    try:
        delay = float(input("Har bir guruh orasida sekund (3-5): "))
        if delay < 0:
            raise ValueError
    except Exception:
        print("Raqam kiriting!")
        input("\nEnter bosing...")
        return

    print(f"\nBoshlanmoqda... {len(selected)} ta akkaunt, {num_groups} ta guruh, {delay}s oraliq\n")

    semaphore = asyncio.Semaphore(5)
    async def limited_task(sess):
        async with semaphore:
            await create_groups_for_single_account(sess, num_groups, delay)
    tasks = [limited_task(s) for s in selected]
    await asyncio.gather(*tasks, return_exceptions=True)

    print("\nBARCHA GURUHLAR YARATILDI!")
    input("\nEnter bosing...")

# Kanalga obuna
async def subscribe_channel():
    clear_screen()
    print("=== KANALGA OBUNA QILDIRISH ===")

    sessions = get_sessions()
    if not sessions:
        print("Hech qanday session mavjud emas!")
        input("\nEnter bosing...")
        return

    channel_username = input("Qaysi kanalga obuna qilamiz? (@ bilan): ").strip()
    if not channel_username.startswith("@"):
        print("Noto'g'ri format! @kanal tarzida kiriting!")
        input("\nEnter bosing...")
        return

    limit = input("Nechta akkaunt ishlasin? (0 = hammasi): ").strip()
    try:
        limit = int(limit)
    except:
        limit = 0

    if limit == 0:
        limit = len(sessions)

    print("\nObuna jarayoni boshlanmoqda...\n")

    subscribed_count = 0
    for session_name in sessions[:limit]:
        session_path = os.path.join(SESSIONS_DIR, f"{session_name}.session")
        client = TelegramClient(session_path, API_ID, API_HASH)

        try:
            await client.connect()
            if not await client.is_user_authorized():
                print(f"{session_name}: Avtorizatsiya qilinmagan — o‘tkazildi ")
                await client.disconnect()
                continue

            me = await client.get_me()
            phone = me.phone or "Noma'lum"

            already = False
            try:
                await client.get_participant(channel_username)
                already = True
            except:
                pass

            if already:
                print(f"{phone}: Allaqachon obuna bo‘lgan — tashlab ketildi ")
                await client.disconnect()
                continue

            try:
                await client(JoinChannelRequest(channel_username))
                print(f"{phone}: Muvaffaqiyatli obuna bo‘ldi! ")
                subscribed_count += 1
                with open("subscribed_channels.txt", "a") as f:
                    f.write(channel_username + "\n")
            except Exception as e:
                print(f"{phone}: Obuna bo‘lmadi: {e}")

        except Exception as e:
            print(f"{session_name}: Xatolik: {e}")

        finally:
            if client.is_connected():
                await client.disconnect()

    print(f"\nJami {subscribed_count} ta akkaunt {channel_username} kanaliga obuna bo‘ldi.")
    input("\nEnter bosing...")

# Kanaldan chiqish
async def leave_channel():
    clear_screen()
    print("=== KANALDAN CHIQISH ===")

    if not os.path.exists("subscribed_channels.txt"):
        print("Hali hech qanday kanalga obuna qilinmagan!")
        input("\nEnter bosing...")
        return

    with open("subscribed_channels.txt", "r") as f:
        channels = list(set([x.strip() for x in f.readlines() if x.strip()]))

    if not channels:
        print("Ro‘yxatda hech qanday kanal yo‘q!")
        input("\nEnter bosing...")
        return

    print("\nObuna qilingan kanallar:")
    for i, ch in enumerate(channels, 1):
        print(f"{i}. {ch}")

    choice = input("\nQaysi kanaldan chiqmoqchisiz? (raqam kiriting): ").strip()
    try:
        choice = int(choice)
        if choice < 1 or choice > len(channels):
            raise ValueError
    except:
        print("Noto‘g‘ri tanlov!")
        input("\nEnter bosing...")
        return

    selected_channel = channels[choice - 1]
    print(f"\nBarcha akkauntlar {selected_channel} kanalidan chiqmoqda...\n")

    sessions = get_sessions()

    for session_name in sessions:
        session_path = os.path.join(SESSIONS_DIR, f"{session_name}.session")
        client = TelegramClient(session_path, API_ID, API_HASH)

        try:
            await client.connect()
            if not await client.is_user_authorized():
                await client.disconnect()
                continue

            me = await client.get_me()
            phone = me.phone or "Noma'lum"

            try:
                await client.get_participant(selected_channel)
            except:
                print(f"{phone}: Bu kanalga obuna bo‘lmagan — o‘tkazildi ")
                await client.disconnect()
                continue

            try:
                await client(LeaveChannelRequest(selected_channel))
                print(f"{phone}: Chiqdi ")
            except Exception as e:
                print(f"{phone}: Chiqishda xatolik: {e}")

        except Exception as e:
            print(f"{session_name}: Xatolik: {e}")

        finally:
            if client.is_connected():
                await client.disconnect()

    channels.remove(selected_channel)
    with open("subscribed_channels.txt", "w") as f:
        for ch in channels:
            f.write(ch + "\n")

    print(f"\nBarcha akkauntlar {selected_channel} kanalidan chiqdi!")
    input("\nEnter bosing...")

# Reaksiya qo'shish
async def reaction():
    clear_screen()
    print("=== REAKSIYA QO'SHISH ===")

    sessions = get_sessions()
    if not sessions:
        print("Hech qanday akkaunt mavjud emas!")
        input()
        return

    url = input("Xabar havolasini kiriting:\n").strip()
    if not url:
        print("Havola bosh!")
        input()
        return

    try:
        limit = int(input(f"Nechta akkaunt ishlatilsin? (0=barchasi {len(sessions)}): "))
    except:
        print("Noto'g'ri kiritildi!")
        input()
        return

    if limit == 0:
        selected_sessions = sessions
    elif 1 <= limit <= len(sessions):
        selected_sessions = sessions[:limit]
    else:
        print("Limit ortiqcha!")
        input()
        return

    print("\nReaksiya tanlang:")
    print("1. Salbiy")
    print("2. Ijobiy")
    print("3. Aralash")
    choice = input("Tanlov (1/2/3): ").strip()

    POS = ["", "", "", "", "", "", "", ""]
    NEG = ["", "", "", "", "", ""]

    if choice == "1":
        reactions = NEG
    elif choice == "2":
        reactions = POS
    elif choice == "3":
        reactions = NEG + POS
    else:
        print("Noto'g'ri tanlov!")
        input()
        return

    try:
        count = int(input("Nechta reaksiya qo'shilsin? (1-3): "))
        if not 1 <= count <= 3:
            count = 1
    except:
        count = 1

    print(f"Reaksiyalarni yuborish boshlandi... ({len(selected_sessions)} ta akkaunt)")

    success = 0

    try:
        parts = url.split("/")
        msg_id = int(parts[-1])
        if "/c/" in url:
            entity = int(parts[-2])
        else:
            entity = parts[-2]
    except:
        print("Havola noto'g'ri!")
        input()
        return

    for session in selected_sessions:
        path = os.path.join(SESSIONS_DIR, f"{session}.session")
        client = TelegramClient(path, API_ID, API_HASH)

        try:
            await client.connect()
            if not await client.is_user_authorized():
                print(session, "Avtorizatsiya qilinmagan!")
                continue

            ent = await client.get_entity(entity)

            for _ in range(count):
                await client(
                    SendReactionRequest(
                        peer=ent,
                        msg_id=msg_id,
                        reaction=[ReactionEmoji(random.choice(reactions))]
                    )
                )

            print(session, ": OK")
            success += 1

        except Exception as e:
            print(session, "Xato:", e)

        finally:
            try:
                await client.disconnect()
            except:
                pass

    print(f"\n{success} ta akkaunt muvaffaqiyatli bajardi!")
    input("\nEnter bosing...")

# 2FA o'rnatish
async def set_2fa_all():
    clear_screen()
    print("=== 2FA O'RNATISH ===")
    sessions = get_sessions()
    if not sessions:
        print("Hech qanday akkaunt yo'q!")
        input("\nEnter bosing...")
        return
    needs_2fa = []
    print("Sessiyalar tahlil qilinmoqda...\n")
    for session_name in sessions:
        session_path = os.path.join(SESSIONS_DIR, f"{session_name}.session")
        client = TelegramClient(session_path, API_ID, API_HASH)
        try:
            await client.connect()
            if not await client.is_user_authorized():
                print(f"Skipping {session_name}: Ulanmagan")
                await client.disconnect()
                continue
            me = await client.get_me()
            phone = me.phone if me.phone else "Noma'lum"
            full_name = f"{me.first_name} {me.last_name or ''}".strip()
            password_info = await client(GetPasswordRequest())
            if password_info.has_password:
                print(f"Skipping {session_name} ({phone}): 2FA bor")
                await client.disconnect()
                continue
            needs_2fa.append((session_path, phone, full_name))
            print(f"Check {session_name} ({phone})  2FA yo'q")
            await client.disconnect()
        except Exception as e:
            print(f"Error {session_name}: {e}")
            if client.is_connected():
                await client.disconnect()
    if not needs_2fa:
        print("\n2FA o'rnatish kerak bo'lgan akkaunt topilmadi.")
        input("\nEnter bosing...")
        return
    print(f"\n{len(needs_2fa)} ta akkaunt 2FA yo'q:")
    for i, (_, phone, name) in enumerate(needs_2fa, 1):
        print(f"{i}. {phone}  {name}")
    code = input("\n2FA parolni kiriting (masalan, 1590): ").strip()
    if not code:
        print("Parol kiritilmadi!")
        input("\nEnter bosing...")
        return
    print(f"\n2FA o'rnatilmoqda... ({code})\n")
    for session_path, phone, name in needs_2fa:
        client = TelegramClient(session_path, API_ID, API_HASH)
        try:
            await client.connect()
            await client.start()
            await client.edit_2fa(new_password=code, hint="Auto set")
            print(f"Success 2FA: {phone}  {name}")
        except Exception as e:
            print(f"Error 2FA: {phone}  {e}")
        finally:
            await client.disconnect()
    print(f"\n{len(needs_2fa)} ta akkauntga 2FA o'rnatildi!")
    input("\nEnter bosing...")

# Menyu
def show_menu():
    clear_screen()
    logo = pyfiglet.figlet_format("Telegram", font="slant")
    print(Fore.CYAN + Style.BRIGHT + logo)
    print(Fore.WHITE + "" * 44)
    print(Fore.CYAN + Style.BRIGHT + "           TELEGRAM PANEL            ".center(44))
    print(Fore.WHITE + "" * 44)

    menu = [
        "[1] Hisoblar qo'shish.",
        "[2] Hisobdan chiqish.",
        "[3] Faol akkauntlar",
        "[4] Guruh ochish.",
        "[5] 2FA ulash.",
        "[6] Kanalga azo.",
        "[7] Aytgan kanallardan chiqish.",
        "[99] Reaksiya qo'shish.",
        "[0] Chiqish"
    ]

    for item in menu:
        if "[7]" in item or "[0]" in item:
            print(Fore.RED + Style.BRIGHT + "| " + item)
        elif "[5]" in item or "[99]" in item:
            print(Fore.MAGENTA + Style.BRIGHT + "| " + item)
        else:
            print(Fore.GREEN + "| " + item)

    print(Fore.WHITE + "" * 44)

# Asosiy dastur
async def main():
    while True:
        show_menu()
        choice = input("Raqam kiriting: ").strip()
        if choice == '1':
            await add_account()
        elif choice == '2':
            delete_account()
        elif choice == '3':
            list_accounts()
        elif choice == '4':
            await create_groups()
        elif choice == '5':
            await set_2fa_all()
        elif choice == '6':
            await subscribe_channel()
        elif choice == '7':
            await leave_channel()
        elif choice == '99':
            await reaction()
        elif choice == '0':
            clear_screen()
            print("Chiqildi! Xayr!")
            break
        else:
            clear_screen()
            print("Noto'g'ri raqam!")
            input("\nEnter bosing...")

if __name__ == '__main__':
    init(autoreset=True)
    asyncio.run(main())