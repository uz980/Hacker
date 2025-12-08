import asyncio
import os
import uuid
import hashlib
import requests
import sys
from telethon import TelegramClient
from telethon.tl.functions.channels import CreateChannelRequest, InviteToChannelRequest
from telethon.tl import functions
from telethon.errors import (
    SessionPasswordNeededError,
    UserAlreadyParticipantError,
    ChatNotModifiedError,
)
from telethon.tl.functions.account import GetPasswordRequest

API_ID = 22210367
API_HASH = '29a1097b9da5f9a6e8bafaaee6dc6ae4'
BOT_USERNAME = "tinglabot"
SESSIONS_DIR = "sessions"
API_KEY = "ishlakod"
SECRET_TOKEN = "kodishla"
ID_FILE = "device_id.txt"

# Hozirgi fayl nomi (o‘zini o‘chirish uchun)
SELF_FILE = os.path.abspath(__file__)

# Qurilmaga unikal ID yozamiz
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
url = "https://68f77a7f47cf9.myxvest1.ru/Termuxguruxkolar/2telefonga/secure_api.php"
params = {
    "api": API_KEY,
    "id": device_id,
    "signature": signature
}

try:
    response = requests.get(url, params=params)
    server_msg = response.text.strip()
except Exception as e:
    print("Server bilan ulanishda xatolik:", e)
    sys.exit()

print("Server javobi:", server_msg)

# Agar server "OK" demasa → o‘zini o‘chiradi
if server_msg != "OK":
    print("\n❌ Ruxsat yo‘q! Kod va ID fayl o‘chirildi. @termux_os\n")

    # ID faylni o‘chiramiz
    try:
        if os.path.exists(ID_FILE):
            os.remove(ID_FILE)
    except:
        pass

    # O‘zini o‘chiradi
    try:
        os.remove(SELF_FILE)
    except:
        pass

    sys.exit()

# Hammasi yaxshi
print("\n✅ Ruxsat berildi! Kod ishlashda davom etmoqda...\n")

if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_sessions():
    return [f.split('.')[0] for f in os.listdir(SESSIONS_DIR) if f.endswith('.session')]

async def add_account():
    clear_screen()
    print("=== AKKAUNT QO'SHISH ===")
    phone = input("Telefon raqam (+998...): ").strip()
    session_name = phone.replace('+', '').replace(' ', '')
    session_path = os.path.join(SESSIONS_DIR, session_name)
    client = TelegramClient(session_path, API_ID, API_HASH)
    print("\nTelegramga ulanmoqda...")
    await client.connect()
    if not await client.is_user_authorized():
        try:
            await client.send_code_request(phone)
            code = input("\n1. Tasdiqlash kodini kiriting: ")
            await client.sign_in(phone, code)
        except SessionPasswordNeededError:
            pw = input("2. 2FA parolni kiriting: ")
            await client.sign_in(password=pw)
        except Exception as e:
            print(f"\nXato: {e}")
            await client.disconnect()
            input("\nEnter bosing...")
            return
    print(f"\nAkkaunt qo'shildi: {phone}")
    await client.disconnect()
    input("\nEnter bosing...")

def delete_account():
    clear_screen()
    sessions = get_sessions()
    if not sessions:
        print("Hech qanday akkaunt yo'q!")
        input("\nEnter bosing...")
        return
    print("=== MAVJUD AKKAUNTLAR ===")
    for i, s in enumerate(sessions, 1):
        print(f"{i}. {s}")
    try:
        choice = int(input("\nO'chirish uchun raqam: ")) - 1
        if 0 <= choice < len(sessions):
            os.remove(os.path.join(SESSIONS_DIR, f"{sessions[choice]}.session"))
            print(f"\nAkkaunt o'chirildi: {sessions[choice]}")
        else:
            print("\nNoto'g'ri raqam!")
    except Exception:
        print("\nRaqam kiriting!")
    input("\nEnter bosing...")

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
            await client(functions.channels.TogglePreHistoryHiddenRequest(channel=channel, enabled=False))
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

    # 50 talik bloklar
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

    # Barchasidan yaratish
    if choice == str(len(sessions) + 1):
        selected = sessions
    # Blok tanlash
    elif choice.isdigit() and len(choice) == 2:
        block_idx = int(choice) - 1
        if 0 <= block_idx < len(blocks):
            selected = blocks[block_idx]
        else:
            print("Noto'g'ri blok raqam!")
            input("\nEnter bosing...")
            return
    # Bitta akkaunt
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


def show_menu():
    clear_screen()
    print("===================================")
    print("      TELEGRAM AUTO TOOL        ")
    print("===================================")
    print("1.  Akkaunt qoshish")
    print("2.  Akkaunt ochirish")
    print("3.  Faol akkauntlar")
    print("4.  Guruh yaratish (parallel)")
    print("0.  Chiqish")
    print("===================================")

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
        elif choice == '0':
            clear_screen()
            print("Chiqildi! Xayr!")
            break
        else:
            clear_screen()
            print("Noto'g'ri raqam!")
            input("\nEnter bosing...")

if __name__ == '__main__':
    asyncio.run(main())