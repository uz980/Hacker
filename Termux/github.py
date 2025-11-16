# manba bilan ol ! @termux_os
import os
import json
import asyncio
import logging
from telethon import TelegramClient, functions, errors
from telethon.errors import FloodWaitError, PhoneNumberBannedError

# manba bilan ol ! @termux_os
# 🔧 Logging sozlash (xatolarni kuzatish uchun)
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('telegram_tool.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# manba bilan ol ! @termux_os
# 🔑 Telegram API ma'lumotlari
API_ID = 24615256  # O'zingizning API ID
API_HASH = '8a210e7fb0361891fb1a2776d9806166'  # O'zingizning API Hash
ACCOUNTS_FILE = 'accounts.json'

# manba bilan ol ! @termux_os
# === 📂 Akkauntlarni yuklash/saqlash ===
def load_accounts():
    """Akkauntlar faylidan ma'lumotlarni yuklaydi."""
    try:
        if os.path.exists(ACCOUNTS_FILE):
            with open(ACCOUNTS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
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
# === 👥 Guruh yaratish ===
async def create_groups(client, count=5, delay=5):
    """Berilgan sonli guruhlar yaratadi."""
    try:
        for i in range(1, count + 1):
            group_name = f"Avto Guruh #{i}"
            try:
                result = await client(functions.messages.CreateChatRequest(
                    users=[],  # Bo‘sh guruh
                    title=group_name
                ))
                logger.info(f"✅ Guruh yaratildi: {group_name}")
            except FloodWaitError as e:
                logger.warning(f"⏳ Flood xatosi: {e.seconds} sekund kutish kerak.")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                logger.error(f"❌ Guruh yaratishda xato: {e}")
            await asyncio.sleep(delay)
    except Exception as e:
        logger.error(f"Guruhlar yaratishda xato: {e}")

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
