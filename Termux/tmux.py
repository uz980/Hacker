import asyncio
import os
from telethon import TelegramClient
from telethon.tl.functions.channels import CreateChannelRequest, InviteToChannelRequest
from telethon.tl import functions
from telethon.errors import (
    SessionPasswordNeededError,
    UserAlreadyParticipantError,
    ChatNotModifiedError,
)

# -------------------------------------------------
# API MA'LUMOTLARI (o'zingizniki bilan almashtiring!)
# -------------------------------------------------
API_ID = 22210367
API_HASH = '29a1097b9da5f9a6e8bafaaee6dc6ae4'
BOT_USERNAME = "tinglabot"          # bot username ( @siz)
SESSIONS_DIR = "sessions"           # sessiyalar saqlanadigan papka

# -------------------------------------------------
# YORDAMCHI FUNKSIYALAR
# -------------------------------------------------
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_sessions():
    return [
        f.split('.')[0]
        for f in os.listdir(SESSIONS_DIR)
        if f.endswith('.session')
    ]

# -------------------------------------------------
# AKKAUNT QO‘SHISH / O‘CHIRISH / RO‘YXAT
# -------------------------------------------------
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

# -------------------------------------------------
# BITTA GURUH YARATISH
# -------------------------------------------------
async def create_single_group(client: TelegramClient, group_number: int):
    try:
        print(f"  → Guruh {group_number} yaratilmoqda...")
        result = await client(CreateChannelRequest(
            title=f'Avto Guruh {group_number}',
            about='@tinglabot qo‘shildi. Tarix ochiq!',
            megagroup=True
        ))
        channel = result.chats[0]
        print(f"  ✓ Guruh: {channel.title} (ID: {channel.id})")

        # Tarixni yangi a’zolar uchun ochish
        try:
            await client(functions.channels.TogglePreHistoryHiddenRequest(
                channel=channel,
                enabled=False
            ))
        except ChatNotModifiedError:
            pass
        except Exception as e:
            print(f"    ⚠ Tarix sozlamasi xato: {e}")

        # Botni qo‘shish
        try:
            bot = await client.get_entity(BOT_USERNAME)
            await client(InviteToChannelRequest(channel=channel, users=[bot]))
        except UserAlreadyParticipantError:
            pass
        except Exception as e:
            print(f"    ⚠ Bot qo'shish xatosi: {e}")

        # Xush kelibsiz xabar
        try:
            await client.send_message(channel, "Xush kelibsiz! Guruh tayyor!")
        except Exception as e:
            print(f"    ⚠ Xabar yuborish xatosi: {e}")

    except Exception as e:
        print(f"  ✗ Guruh {group_number} yaratishda xato: {e}")

# -------------------------------------------------
# BITTA AKKAUNT UCHUN GURUHLAR
# -------------------------------------------------
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

# -------------------------------------------------
# GURUH YARATISH – BARCHA AKKAUNTLAR BLOKLAR BO'YICHA
# -------------------------------------------------
async def create_groups():
    clear_screen()
    sessions = get_sessions()
    if not sessions:
        print("Hech qanday akkaunt yo'q! Avval qo'shing.")
        input("\nEnter bosing...")
        return

    # Akkauntlarni 10 talik bloklarga bo'lish
    blocks = [sessions[i:i + 10] for i in range(0, len(sessions), 10)]

    print("=== GURUH YARATISH ===")
    for i, s in enumerate(sessions, 1):
        print(f"{i}. {s}")

    for idx, block in enumerate(blocks, 1):
        print(f"{idx:02d}. Top {idx} (10 talik)")

    # Tanlov
    choice = input("\nRaqam kiriting (yoki blok: 01, 02...): ").strip()

    # Agar 01,02... formatda bo'lsa
    if choice.isdigit() and len(choice) == 2:
        block_idx = int(choice) - 1
        if 0 <= block_idx < len(blocks):
            selected = blocks[block_idx]
        else:
            print("Noto'g'ri blok raqam!")
            input("\nEnter bosing...")
            return
    else:
        # Oddiy akkaunt raqami
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

    # Nechta guruh va delay
    try:
        num_groups = int(input("\nNechta guruh yaratmoqchisiz? "))
        if num_groups <= 0:
            raise ValueError
    except Exception:
        print("Musbat son kiriting!")
        input("\nEnter bosing...")
        return

    try:
        delay = float(input("Har bir guruh orasida sekund (masalan, 3-5): "))
        if delay < 0:
            raise ValueError
    except Exception:
        print("Raqam kiriting!")
        input("\nEnter bosing...")
        return

    print(f"\nBoshlanmoqda... {len(selected)} ta akkaunt, {num_groups} ta guruh, {delay}s oraliq\n")

    # ----------------- PARALLEL ISHGA TUSHIRISH -----------------
    semaphore = asyncio.Semaphore(5)

    async def limited_task(sess):
        async with semaphore:
            await create_groups_for_single_account(sess, num_groups, delay)

    tasks = [limited_task(s) for s in selected]
    await asyncio.gather(*tasks, return_exceptions=True)
    # -----------------------------------------------------------

    print("\nBARCHA GURUHLAR YARATILDI!")
    input("\nEnter bosing...")

# -------------------------------------------------
# ASOSIY MENYU
# -------------------------------------------------
def show_menu():
    clear_screen()
    print("===================================")
    print("      TELEGRAM AUTO TOOL        ")
    print("===================================")
    print("1️⃣  Akkaunt qo‘shish")
    print("2️⃣  Akkaunt o‘chirish")
    print("3️⃣  Faol akkauntlar")
    print("4️⃣  Guruh yaratish (parallel)")
    print("0️⃣  Chiqish")
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
            print("Noto'g'ri raqam! Qayta urining.")
            input("\nEnter bosing...")

if __name__ == '__main__':
    asyncio.run(main())
