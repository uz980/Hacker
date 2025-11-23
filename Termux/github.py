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
from telethon.tl.functions.account import GetPasswordRequest

API_ID = 22210367
API_HASH = '29a1097b9da5f9a6e8bafaaee6dc6ae4'
BOT_USERNAME = "tinglabot"
SESSIONS_DIR = "sessions"

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
        logger.error(f"Akkauntlarni yuklashda xato: {e}")
        return {}

def save_accounts(data):
    """Akkauntlarni faylga saqlaydi."""
    try:
        with open(ACCOUNTS_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        logger.info("Akkauntlar faylga saqlandi.")
    except Exception as e:
        logger.error(f"Akkauntlarni saqlashda xato: {e}")

# manba bilan ol ! @termux_os
# === 📱 Yangi akkaunt qo‘shish ===
async def add_account(phone, accounts):
    """Yangi Telegram akkauntini qo'shadi."""
    try:
        client = TelegramClient(f"sessions/{phone}", API_ID, API_HASH)
        await client.connect()

        if not await client.is_user_authorized():
            logger.info(f"{phone} raqamiga kod yuborildi...")
            try:
                await client.send_code_request(phone)
                code = input(f"📲 {phone} uchun kodni kiriting: ").strip()
                await client.sign_in(phone, code)
            except errors.SessionPasswordNeededError:
                password = input("🔐 Ikki bosqichli parolni kiriting: ").strip()
                await client.sign_in(password=password)
            except PhoneNumberBannedError:
                logger.error(f"❌ {phone} raqami bloklangan.")
                return
            except Exception as e:
                logger.error(f"❌ Kirishda xato: {e}")
                return

            accounts[phone] = {"active": True}
            save_accounts(accounts)
            logger.info(f"✅ {phone} akkaunti muvaffaqiyatli qo‘shildi!")
        else:
            logger.info(f"⚠️ {phone} allaqachon ulangan.")
    except Exception as e:
        logger.error(f"Akkaunt qo‘shishda xato: {e}")
    finally:
        await client.disconnect()

# manba bilan ol ! @termux_os
# === 👥 Guruh yaratish (yangilangan) ===
async def create_groups(client, count=5, delay=5):
    """Berilgan sonli guruhlar yaratadi va ularga belgilangan botlarni qo'shadi."""
    bot_usernames = ['@tinglabot', '@oxangbot']

    for i in range(1, count + 1):
        group_name = f"Avto Guruh #{i}"
        try:
            result = await client(functions.messages.CreateChatRequest(
                users=[],  # Bo‘sh guruh
                title=group_name
            ))
            # Guruh ID sini olish
            chat = result.chats[0]
            chat_id = chat.id

            logger.info(f"✅ Guruh yaratildi: {group_name}")

            # Botlarni guruhga qo'shish
            for bot_username in bot_usernames:
                try:
                    await client(functions.channels.InviteToChannelRequest(
                        channel=chat_id,
                        users=[bot_username]
                    ))
                    logger.info(f"🤖 {bot_username} guruhga qo'shildi: {group_name}")
                except Exception as e:
                    logger.error(f"❌ {bot_username} guruhga qo'shishda xato: {e}")

        except FloodWaitError as e:
            logger.warning(f"⏳ Flood xatosi: {e.seconds} sekund kutish kerak.")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            logger.error(f"❌ Guruh yaratishda xato: {e}")

        await asyncio.sleep(delay)

# manba bilan ol ! @termux_os
# === 🚀 Akkaunt bilan ishga tushirish ===
async def start_account(phone):
    """Akkauntni ishga tushiradi."""
    try:
        client = TelegramClient(f"sessions/{phone}", API_ID, API_HASH)
        await client.start(phone)
        logger.info(f"▶️ {phone} akkaunt ishga tushdi.")
        return client
    except Exception as e:
        logger.error(f"Akkauntni ishga tushirishda xato: {e}")
        return None

# manba bilan ol ! @termux_os
# === 🧭 Asosiy menyuni boshqarish ===
async def main():
    # Sessiya papkasini yaratish
    if not os.path.exists('sessions'):
        os.makedirs('sessions')

    accounts = load_accounts()

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')  # Ekran tozalash
        print("===================================")
        print("      📲 TELEGRAM AUTO TOOL        ")
        print("===================================")
        print("1️⃣  Akkaunt qo‘shish")
        print("2️⃣  Akkaunt o‘chirish")
        print("3️⃣  Faol akkauntlar")
        print("4️⃣  Guruh yaratish (avto)")
        print("0️⃣  Chiqish")
        print("===================================")

        tanlov = input("Tanlov (0-4): ").strip()

        # 1. Akkaunt qo‘shish
        if tanlov == '1':
            phone = input("📱 Telefon raqam (+998...): ").strip()
            if not phone.startswith('+'):
                logger.error("❌ Telefon raqami + bilan boshlanishi kerak!")
                input("\nDavom etish uchun Enter bosing...")
                continue
            if phone in accounts:
                logger.warning("⚠️ Bu raqam allaqachon mavjud!")
            else:
                await add_account(phone, accounts)
            input("\nDavom etish uchun Enter bosing...")

        # 2. Akkaunt o‘chirish
        elif tanlov == '2':
            phone = input("📱 O‘chiriladigan raqam (+998...): ").strip()
            if phone in accounts:
                del accounts[phone]
                save_accounts(accounts)
                session_file = f"sessions/{phone}.session"
                if os.path.exists(session_file):
                    os.remove(session_file)
                    logger.info(f"🗑️ {phone} akkaunti va sessiyasi o‘chirildi.")
                else:
                    logger.info(f"🗑️ {phone} akkaunti o‘chirildi, sessiya topilmadi.")
            else:
                logger.error("❌ Bunday akkaunt topilmadi.")
            input("\nDavom etish uchun Enter bosing...")

        # 3. Faol akkauntlar
        elif tanlov == '3':
            if not accounts:
                logger.info("📭 Hozircha hech qanday akkaunt yo‘q.")
            else:
                print("\n📱 Faol akkauntlar:")
                for p, info in accounts.items():
                    holat = "✅ Faol" if info.get("active") else "❌ Nofaol"
                    print(f" - {p}: {holat}")
            input("\nDavom etish uchun Enter bosing...")

        # 4. Guruh yaratish
        elif tanlov == '4':
            active = [p for p, i in accounts.items() if i.get('active')]
            if not active:
                logger.error("❌ Hech qanday faol akkaunt yo‘q!")
                input("\nDavom etish uchun Enter bosing...")
                continue

            print("\n📱 Faol akkauntlar:")
            for i, p in enumerate(active, 1):
                print(f"{i}. {p}")

            try:
                tan = int(input("\nQaysi akkauntdan foydalanamiz (raqam): "))
                if tan < 1 or tan > len(active):
                    logger.error("❌ Noto‘g‘ri tanlov!")
                    input("\nDavom etish uchun Enter bosing...")
                    continue
            except ValueError:
                logger.error("❌ Raqam kiriting!")
                input("\nDavom etish uchun Enter bosing...")
                continue

            tanlangan = active[tan - 1]
            client = await start_account(tanlangan)
            if client:
                try:
                    son = int(input("Nechta guruh yaratiladi: "))
                    if son <= 0:
                        logger.error("❌ Guruhlar soni 0 dan katta bo‘lishi kerak!")
                        input("\nDavom etish uchun Enter bosing...")
                        continue
                    kechikish = int(input("Har guruh orasida kechikish (sekund): "))
                    if kechikish < 0:
                        logger.error("❌ Kechikish manfiy bo‘lishi mumkin emas!")
                        input("\nDavom etish uchun Enter bosing...")
                        continue
                    await create_groups(client, count=son, delay=kechikish)
                except ValueError:
                    logger.error("❌ Noto‘g‘ri qiymat kiritildi.")
                finally:
                    await client.disconnect()
            input("\nDavom etish uchun Enter bosing...")

        # 0. Chiqish
        elif tanlov == '0':
            logger.info("👋 Dastur tugadi.")
            break

        else:
            logger.error("❌ Noto‘g‘ri tanlov!")
            input("\nDavom etish uchun Enter bosing...")

# manba bilan ol ! @termux_os
# === 🔰 Ishga tushirish ===
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Foydalanuvchi tomonidan dastur to‘xtatildi.")
    except Exception as e:
        logger.error(f"Dasturda kutilmagan xato: {e}")
        # manba bilan ol ! @termux_os
        
stop code @shax_mobi
