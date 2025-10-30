import asyncio
import os
import sys
from telethon import TelegramClient
from telethon.tl.functions.channels import CreateChannelRequest, TogglePreHistoryHiddenRequest, InviteToChannelRequest
from telethon.tl.functions.messages import SendMessageRequest
from telethon.errors import SessionPasswordNeededError, ChatNotModifiedError, UserAlreadyParticipantError

# @termux_os manba bolan ol
API_ID = 24615256        # O'z API ID'ingizni qo'ying
API_HASH = '8a210e7fb0361891fb1a2776d9806166'  # O'z API Hash'ingizni qo'ying

# Bot foydalanuvchi nomi
BOT_USERNAME = "tinglabot"

# Sessiyalar papkasi
SESSIONS_DIR = "new"
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

# Ekran tozalash (Windows + Linux)
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Sessiyalarni olish
def get_sessions():
    return [f.split('.')[0] for f in os.listdir(SESSIONS_DIR) if f.endswith('.session')]

# @termux_os manba bolan ol
# Yangi akkaunt qo'shish
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
            password = input("2. 2FA parolni kiriting: ")
            await client.sign_in(password=password)
        except Exception as e:
            print(f"\nXato: {e}")
            await client.disconnect()
            input("\nEnter bosing...")
            return

    print(f"\nAkkaunt qo'shildi: {phone}")
    await client.disconnect()
    input("\nEnter bosing...")

# @termux_os manba bolan ol
# Akkaunt o'chirish
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
            os.remove(os.path.join(SESSIONS_DIR, sessions[choice] + '.session'))
            print(f"\nAkkaunt o'chirildi: {sessions[choice]}")
        else:
            print("\nNoto'g'ri raqam!")
    except:
        print("\nRaqam kiriting!")
    input("\nEnter bosing...")

# Faol akkauntlar
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

# Bitta guruh yaratish
async def create_single_group(client, group_number):
    print(f"\n{group_number}-guruh yaratilmoqda...")
    result = await client(CreateChannelRequest(
        title=f'Avto Guruh {group_number}',
        about='@tinglabot qo‘shildi. Tarix ochiq!',
        megagroup=True
    ))
    channel = result.chats[0]
    print(f"Guruh yaratildi: {channel.title} (ID: {channel.id})")

    # Tarixni ochish
    try:
        await client(TogglePreHistoryHiddenRequest(channel=channel, enabled=True))
    except ChatNotModifiedError:
        pass
    try:
        await client(TogglePreHistoryHiddenRequest(channel=channel, enabled=False))
    except ChatNotModifiedError:
        pass

    # Bot qo'shish
    try:
        bot_entity = await client.get_entity(BOT_USERNAME)
        await client(InviteToChannelRequest(channel=channel, users=[bot_entity]))
        print(f"@{BOT_USERNAME} qo'shildi")
    except UserAlreadyParticipantError:
        print(f"@{BOT_USERNAME} allaqachon guruhda")
    except Exception as e:
        print(f"Bot qo'shish xatosi: {e}")

    # Xabar yuborish
    try:
        await client.send_message(channel, "Xush kelibsiz! Guruh tayyor!")
        print("Xabar yuborildi")
    except Exception as e:
        print(f"Xabar xatosi: {e}")

# @termux_os manba bolan ol
# Ko'p guruh yaratish
async def create_groups():
    clear_screen()
    sessions = get_sessions()
    if not sessions:
        print("Hech qanday akkaunt yo'q! Avval qo'shing.")
        input("\nEnter bosing...")
        return

    print("=== GURUH YARATISH ===")
    print("Akkaunt tanlang:")
    for i, s in enumerate(sessions, 1):
        print(f"{i}. {s}")

    try:
        choice = int(input("\nRaqam: ")) - 1
        if not (0 <= choice < len(sessions)):
            print("Noto'g'ri tanlov!")
            input("\nEnter bosing...")
            return
    except:
        print("Raqam kiriting!")
        input("\nEnter bosing...")
        return

    session_name = sessions[choice]
    client = TelegramClient(os.path.join(SESSIONS_DIR, session_name), API_ID, API_HASH)
    await client.start()

    try:
        num_groups = int(input("\nNechta guruh yaratmoqchisiz? "))
        if num_groups <= 0:
            print("Musbat son kiriting!")
            await client.disconnect()
            input("\nEnter bosing...")
            return
    except:
        print("Raqam kiriting!")
        await client.disconnect()
        input("\nEnter bosing...")
        return

    try:
        delay = float(input("Har bir guruh orasida sekund (masalan, 5): "))
        if delay < 0:
            print("Noto'g'ri qiymat!")
            await client.disconnect()
            input("\nEnter bosing...")
            return
    except:
        print("Raqam kiriting!")
        await client.disconnect()
        input("\nEnter bosing...")
        return

    print(f"\nBoshlanmoqda... {num_groups} ta guruh, {delay} sekund oraliq\n")
    for i in range(1, num_groups + 1):
        await create_single_group(client, i)
        if i < num_groups:
            print(f"\n{int(delay)} sekund kutilyapti...")
            await asyncio.sleep(delay)

    print(f"\nBarcha {num_groups} ta guruh yaratildi!")
    await client.disconnect()
    input("\nEnter bosing...")

# @termux_os manba bolan ol
# Asosiy menyu
def show_menu():
    clear_screen()
    print("===================================")
    print("      TELEGRAM AUTO TOOL        ")
    print("===================================")
    print("1.  Akkaunt qo'shish")
    print("2.  Akkaunt o'chirish")
    print("3.  Faol akkauntlar")
    print("4.  Guruh yaratish (avto)")
    print("0.  Chiqish")
    print("===================================")

async def main():
    # Dastur boshlanganda ekran tozalanadi
    clear_screen()
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
            print("Noto'g'ri raqam! Qayta urining.")
            input("\nEnter bosing...")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        clear_screen()
        print("\nDastur to'xtatildi.")
        # @termux_os manba bolan ol
