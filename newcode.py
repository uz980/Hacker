# -*- coding: utf-8 -*-
import pyfiglet
import asyncio
import os
import random
from colorama import init, Fore, Back, Style

from telethon import TelegramClient, functions
from telethon.tl.functions.channels import (
    CreateChannelRequest,
    InviteToChannelRequest,
    JoinChannelRequest,
    LeaveChannelRequest,
    TogglePreHistoryHiddenRequest,
    GetParticipantRequest,
    EditAdminRequest,
    EditCreatorRequest
)
from telethon.tl.functions.messages import (
    SendReactionRequest,
    ExportChatInviteRequest
)
from telethon.tl.functions.account import GetPasswordRequest, UpdatePasswordSettingsRequest
from telethon.tl.types import ReactionEmoji, ChatAdminRights, InputCheckPasswordSRP
from telethon.errors import (
    SessionPasswordNeededError,
    UserAlreadyParticipantError,
    ChatNotModifiedError,
    PasswordHashInvalidError,
    UsernameInvalidError,
    UsernameNotOccupiedError,
    UserPrivacyRestrictedError,
    UserNotMutualContactError,
    ChatAdminRequiredError,
    FloodWaitError
)
from telethon.tl import types
from telethon.tl.types import ChannelParticipantCreator, ChannelParticipantAdmin
from telethon.password import compute_check, compute_digest

# Sozlamalar
API_ID = 22210367
API_HASH = '29a1097b9da5f9a6e8bafaaee6dc6ae4'
SESSIONS_DIR = "ulangan"
BOTS_FILE = "bots.txt"  # Botlar ro'yxati fayli

if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

# ============================================================
# BOT BOSHQARUV FUNKSIYALARI
# ============================================================

def get_bots():
    """Saqlangan botlar ro'yxatini olish"""
    if not os.path.exists(BOTS_FILE):
        return []
    with open(BOTS_FILE, "r", encoding="utf-8") as f:
        bots = [line.strip() for line in f.readlines() if line.strip()]
    return bots

def save_bots(bots: list):
    """Botlar ro'yxatini saqlash"""
    with open(BOTS_FILE, "w", encoding="utf-8") as f:
        for bot in bots:
            f.write(bot + "\n")

def manage_bots():
    """Botlarni boshqarish menyusi"""
    while True:
        clear_screen()
        bots = get_bots()

        print(Fore.CYAN + Style.BRIGHT + "=" * 50)
        print(Fore.CYAN + Style.BRIGHT + "         BOTLARNI BOSHQARISH          ".center(50))
        print(Fore.WHITE + "=" * 50)

        if bots:
            print(Fore.GREEN + f"\n📋 Saqlangan botlar ({len(bots)} ta):")
            for i, bot in enumerate(bots, 1):
                print(Fore.WHITE + f"  {i}. {bot}")
        else:
            print(Fore.YELLOW + "\n⚠ Hech qanday bot saqlanmagan!")

        print(Fore.WHITE + "\n" + "=" * 50)
        print(Fore.GREEN + "| [1] Bot qo'shish")
        print(Fore.RED   + "| [2] Bot o'chirish")
        print(Fore.CYAN  + "| [3] Barcha botlarni ko'rish")
        print(Fore.RED   + "| [0] Orqaga")
        print(Fore.WHITE + "=" * 50)

        choice = input("Raqam kiriting: ").strip()

        if choice == '1':
            _add_bot(bots)
        elif choice == '2':
            _delete_bot(bots)
        elif choice == '3':
            _list_bots(bots)
        elif choice == '0':
            break
        else:
            print(Fore.RED + "❌ Noto'g'ri raqam!")
            input("\nEnter bosing...")

def _add_bot(bots: list):
    """Bot qo'shish"""
    clear_screen()
    print(Fore.CYAN + "=== BOT QO'SHISH ===\n")

    print("Bir yoki bir nechta bot username kiriting.")
    print("Har birini yangi qatorga yozing, bo'sh qator - tugash.\n")

    added = 0
    while True:
        username = input("Bot username (@ bilan yoki @ siz, bo'sh = tugash): ").strip()
        if not username:
            break

        if not username.startswith("@"):
            username = "@" + username

        # Kichik harfga o'tkazish
        username = username.lower()

        if username in [b.lower() for b in bots]:
            print(Fore.YELLOW + f"  ⚠ {username} allaqachon ro'yxatda!")
        else:
            bots.append(username)
            save_bots(bots)
            print(Fore.GREEN + f"  ✅ {username} qo'shildi!")
            added += 1

    print(Fore.GREEN + f"\n✅ {added} ta bot qo'shildi.")
    input("\nEnter bosing...")

def _delete_bot(bots: list):
    """Bot o'chirish"""
    clear_screen()
    print(Fore.CYAN + "=== BOT O'CHIRISH ===\n")

    if not bots:
        print(Fore.YELLOW + "Ro'yxat bo'sh!")
        input("\nEnter bosing...")
        return

    for i, bot in enumerate(bots, 1):
        print(f"{i}. {bot}")

    print("\n0. Barchasini o'chirish")
    choice = input("\nO'chirmoqchi bo'lgan bot raqamini kiriting: ").strip()

    if choice == '0':
        confirm = input("Haqiqatan ham BARCHA botlarni o'chirasizmi? (y/n): ").lower()
        if confirm == 'y':
            bots.clear()
            save_bots(bots)
            print(Fore.GREEN + "✅ Barcha botlar o'chirildi!")
        else:
            print(Fore.YELLOW + "Bekor qilindi.")
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(bots):
                removed = bots.pop(idx)
                save_bots(bots)
                print(Fore.GREEN + f"✅ {removed} o'chirildi!")
            else:
                print(Fore.RED + "❌ Noto'g'ri raqam!")
        except ValueError:
            print(Fore.RED + "❌ Raqam kiritishingiz kerak!")

    input("\nEnter bosing...")

def _list_bots(bots: list):
    """Botlar ro'yxatini ko'rsatish"""
    clear_screen()
    print(Fore.CYAN + "=== BOTLAR RO'YXATI ===\n")

    if not bots:
        print(Fore.YELLOW + "Hech qanday bot saqlanmagan!")
    else:
        print(Fore.GREEN + f"Jami: {len(bots)} ta bot\n")
        for i, bot in enumerate(bots, 1):
            print(f"  {i}. {bot}")

    input("\nEnter bosing...")


# ============================================================
# YORDAMCHI FUNKSIYALAR
# ============================================================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_sessions():
    return [f.split('.')[0] for f in os.listdir(SESSIONS_DIR)
            if f.endswith('.session') and os.path.getsize(os.path.join(SESSIONS_DIR, f)) > 0]

def list_accounts():
    clear_screen()
    sessions = get_sessions()
    print("=== FAOL AKKAUNTLAR ===")
    if not sessions:
        print("Hech qanday faol akkaunt yo'q!")
    else:
        for i, s in enumerate(sessions, 1):
            session_path = os.path.join(SESSIONS_DIR, f"{s}.session")
            size_kb = os.path.getsize(session_path) / 1024
            print(f"{i}. {s} ({size_kb:.1f} KB)")
    input("\nEnter bosing...")

# Hisob qo'shish
async def add_account():
    clear_screen()
    session_name = input("Yangi session nomi (masalan: user1): ").strip()
    if not session_name:
        print("Noto'g'ri nom!")
        input("\nEnter bosing...")
        return

    session_path = os.path.join(SESSIONS_DIR, f"{session_name}.session")

    if os.path.exists(session_path):
        print(f"{session_name} sessioni allaqachon mavjud!")
        choice = input("Ustiga yozilsinmi? (y/n): ").lower()
        if choice != 'y':
            input("\nEnter bosing...")
            return

    client = TelegramClient(session_path, API_ID, API_HASH)

    try:
        print("Telegramga ulanmoqda...")
        await client.connect()

        phone = input("Telefon raqamingizni kiriting (masalan: +998901234567): ").strip()
        if not phone:
            print("Telefon raqam kiritilmadi!")
            await client.disconnect()
            input("\nEnter bosing...")
            return

        await client.send_code_request(phone)
        code = input("SMS yoki Telegram orqali kelgan kodni kiriting: ").strip()

        try:
            await client.sign_in(phone, code)
        except SessionPasswordNeededError:
            password = input("2-qadam parolini kiriting: ")
            await client.sign_in(password=password)

        me = await client.get_me()
        print(f"\n✅ Muvaffaqiyatli ulandi: {me.first_name} ({me.phone})")
        print(f"Session saqlandi: {session_name}.session")

    except Exception as e:
        print(f"❌ Ulanishda xato: {e}")
        if os.path.exists(session_path):
            os.remove(session_path)
    finally:
        if client.is_connected():
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
            session_file = os.path.join(SESSIONS_DIR, f"{sessions[idx]}.session")
            os.remove(session_file)
            print(f"✅ {sessions[idx]} muvaffaqiyatli o'chirildi!")
        else:
            print("❌ Noto'g'ri raqam!")
    except ValueError:
        print("❌ Raqam kiritishingiz kerak!")
    except Exception as e:
        print(f"❌ Xatolik: {e}")
    input("\nEnter bosing...")


# ============================================================
# GURUH YARATISH - BARCHA BOTLAR ADMIN QILINADI
# ============================================================

async def add_bots_to_channel(client: TelegramClient, channel, bots: list):
    """
    Saqlangan barcha botlarni kanalga qo'shib, admin qilish.
    Har bot uchun alohida xato ushlanadi.
    """
    if not bots:
        print("    ⚠ Bot ro'yxati bo'sh, bot qo'shilmadi.")
        return

    admin_rights = ChatAdminRights(
        change_info=True,
        post_messages=True,
        edit_messages=True,
        delete_messages=True,
        ban_users=True,
        invite_users=True,
        pin_messages=True,
        add_admins=False,
        anonymous=False,
        manage_call=True,
        other=True
    )

    for bot_username in bots:
        try:
            bot_entity = await client.get_entity(bot_username)

            # Qo'shish
            try:
                await client(InviteToChannelRequest(channel=channel, users=[bot_entity]))
                print(f"    ✅ {bot_username} qo'shildi")
            except UserAlreadyParticipantError:
                print(f"    ⚠ {bot_username} allaqachon guruhda")

            await asyncio.sleep(1)

            # Admin qilish
            try:
                await client(EditAdminRequest(
                    channel=channel,
                    user_id=bot_entity,
                    admin_rights=admin_rights,
                    rank="Bot"
                ))
                print(f"    👑 {bot_username} admin qilindi")
            except Exception as e:
                print(f"    ❌ {bot_username} admin qilishda xato: {e}")

        except Exception as e:
            print(f"    ❌ {bot_username} topilmadi yoki xato: {e}")

        await asyncio.sleep(0.5)

async def create_single_group(client: TelegramClient, group_number: int, bots: list):
    try:
        print(f"  Guruh {group_number} yaratilmoqda...")
        result = await client(CreateChannelRequest(
            title=f'Avto Guruh {group_number}',
            about='Tarix ochiq!',
            megagroup=True,
            broadcast=False
        ))
        channel = result.chats[0]
        print(f"  ✅ Guruh: {channel.title} (ID: {channel.id})")

        # Tarix ochish
        try:
            await client(TogglePreHistoryHiddenRequest(channel=channel, enabled=False))
            print("    ✅ Tarix ochiq qilindi")
        except ChatNotModifiedError:
            print("    ⚠ Tarix allaqachon ochiq")
        except Exception as e:
            print(f"    ⚠ Tarix sozlamasi xato: {e}")

        # Barcha botlarni qo'shib, admin qilish
        await add_bots_to_channel(client, channel, bots)

        # Xabar yuborish
        try:
            await client.send_message(channel, "Xush kelibsiz! Guruh tayyor!")
            print("    ✅ Xabar yuborildi")
        except Exception as e:
            print(f"    ⚠ Xabar yuborish xatosi: {e}")

        return channel
    except Exception as e:
        print(f"  ❌ Guruh {group_number} yaratishda xato: {e}")
        return None

async def create_groups_for_single_account(session_name: str, num_groups: int, delay: float, bots: list):
    session_path = os.path.join(SESSIONS_DIR, f"{session_name}.session")
    client = TelegramClient(session_path, API_ID, API_HASH)
    try:
        print(f"\n[{session_name}] Ulanmoqda...")
        await client.connect()
        if not await client.is_user_authorized():
            print(f"[{session_name}] ❌ Avtorizatsiya qilinmagan!")
            return

        me = await client.get_me()
        print(f"[{session_name}] ✅ Muvaffaqiyatli ulandi: {me.first_name}")

        created_count = 0
        for i in range(1, num_groups + 1):
            result = await create_single_group(client, i, bots)
            if result:
                created_count += 1
            if i < num_groups and delay > 0:
                await asyncio.sleep(delay)
        print(f"[{session_name}] ✅ {created_count}/{num_groups} ta guruh yaratildi!")
    except Exception as e:
        print(f"[{session_name}] ❌ Umumiy xato: {e}")
    finally:
        if client.is_connected():
            await client.disconnect()

async def create_groups():
    clear_screen()
    sessions = get_sessions()
    if not sessions:
        print("Hech qanday akkaunt yo'q! Avval qo'shing.")
        input("\nEnter bosing...")
        return

    # Botlar ro'yxatini ko'rsatish
    bots = get_bots()
    print("=== GURUH YARATISH ===")
    if bots:
        print(Fore.GREEN + f"\n🤖 Guruhga qo'shiladigan botlar ({len(bots)} ta):")
        for bot in bots:
            print(Fore.WHITE + f"   • {bot}")
    else:
        print(Fore.YELLOW + "\n⚠ Bot ro'yxati bo'sh! Botlar qo'shilmaydi.")
        print(Fore.YELLOW + "  Botlarni qo'shish uchun: Menyu → [11] Botlarni boshqarish")

    print(Fore.WHITE + "\nTanlov usullari:")
    print("1. Barcha akkauntlar")
    print("2. Blok (50 talik) bo'yicha")
    print("3. Faqat bitta akkaunt")

    choice_type = input("\nTanlov (1/2/3): ").strip()

    selected = []

    if choice_type == "1":
        selected = sessions
    elif choice_type == "2":
        BLOCK_SIZE = 50
        blocks = [sessions[i:i + BLOCK_SIZE] for i in range(0, len(sessions), BLOCK_SIZE)]

        print("\n--- Bloklar ---")
        for idx, block in enumerate(blocks, 1):
            print(f"{idx:02d}. Blok {idx} ({len(block)} ta)")

        block_choice = input("Blok raqamini kiriting: ").strip()
        try:
            block_idx = int(block_choice) - 1
            if 0 <= block_idx < len(blocks):
                selected = blocks[block_idx]
            else:
                print("❌ Noto'g'ri blok raqam!")
                input("\nEnter bosing...")
                return
        except ValueError:
            print("❌ Raqam kiritishingiz kerak!")
            input("\nEnter bosing...")
            return
    elif choice_type == "3":
        print("\nAkkauntlar ro'yxati:")
        for i, s in enumerate(sessions, 1):
            print(f"{i}. {s}")

        acc_choice = input("Akkaunt raqamini kiriting: ").strip()
        try:
            acc_idx = int(acc_choice) - 1
            if 0 <= acc_idx < len(sessions):
                selected = [sessions[acc_idx]]
            else:
                print("❌ Noto'g'ri akkaunt raqam!")
                input("\nEnter bosing...")
                return
        except ValueError:
            print("❌ Raqam kiritishingiz kerak!")
            input("\nEnter bosing...")
            return
    else:
        print("❌ Noto'g'ri tanlov!")
        input("\nEnter bosing...")
        return

    try:
        num_groups = int(input("\nHar bir akkaunt uchun nechta guruh yaratmoqchisiz? "))
        if num_groups <= 0 or num_groups > 100:
            print("❌ 1-100 oralig'ida son kiriting!")
            input("\nEnter bosing...")
            return
    except ValueError:
        print("❌ Raqam kiritishingiz kerak!")
        input("\nEnter bosing...")
        return

    try:
        delay = float(input("Har bir guruh orasida sekund (masalan: 3): "))
        if delay < 0 or delay > 60:
            print("❌ 0-60 oralig'ida son kiriting!")
            input("\nEnter bosing...")
            return
    except ValueError:
        print("❌ Raqam kiritishingiz kerak!")
        input("\nEnter bosing...")
        return

    print(f"\nBoshlanmoqda...")
    print(f"✅ Akkauntlar: {len(selected)} ta")
    print(f"✅ Har birida: {num_groups} ta guruh")
    print(f"✅ Kutilmoqda: {delay} sekund")
    print(f"🤖 Botlar: {len(bots)} ta\n")

    semaphore = asyncio.Semaphore(3)

    async def limited_task(sess):
        async with semaphore:
            await create_groups_for_single_account(sess, num_groups, delay, bots)

    tasks = [limited_task(s) for s in selected]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    errors = sum(1 for r in results if isinstance(r, Exception))

    print(f"\n{'='*50}")
    print(f"✅ BARCHA VAZIFALAR TUGATILDI!")
    print(f"📊 Jami akkauntlar: {len(selected)}")
    print(f"📊 Muvaffaqiyatli: {len(selected) - errors}")
    print(f"📊 Xatolar: {errors}")
    print(f"{'='*50}")

    input("\nEnter bosing...")


# ============================================================
# QOLGAN FUNKSIYALAR (o'zgarishsiz)
# ============================================================

async def subscribe_channel():
    clear_screen()
    print("=== KANALGA OBUNA QILDIRISH ===")

    sessions = get_sessions()
    if not sessions:
        print("Hech qanday session mavjud emas!")
        input("\nEnter bosing...")
        return

    channel_username = input("Qaysi kanalga obuna qilamiz? (@ belgisiz yoki @ bilan): ").strip()
    if not channel_username:
        print("Kanal nomi kiritilmadi!")
        input("\nEnter bosing...")
        return

    if not channel_username.startswith("@"):
        channel_username = "@" + channel_username

    limit = input("Nechta akkaunt ishlasin? (0 = hammasi): ").strip()
    try:
        limit = int(limit)
        if limit == 0:
            limit = len(sessions)
        elif limit < 1 or limit > len(sessions):
            print(f"❌ 1-{len(sessions)} oralig'ida son kiriting!")
            input("\nEnter bosing...")
            return
    except ValueError:
        print("❌ Raqam kiritishingiz kerak!")
        input("\nEnter bosing...")
        return

    print(f"\n📊 {limit} ta akkaunt {channel_username} kanaliga obuna qilmoqda...\n")

    subscribed_count = 0
    total = len(sessions[:limit])

    for idx, session_name in enumerate(sessions[:limit], 1):
        session_path = os.path.join(SESSIONS_DIR, f"{session_name}.session")
        client = TelegramClient(session_path, API_ID, API_HASH)

        try:
            await client.connect()
            if not await client.is_user_authorized():
                print(f"{idx}/{total}. {session_name}: ❌ Avtorizatsiya qilinmagan")
                continue

            me = await client.get_me()
            phone = me.phone or "Noma'lum"

            try:
                await client.get_entity(channel_username)
            except (UsernameInvalidError, UsernameNotOccupiedError):
                print(f"{idx}/{total}. {phone}: ❌ Kanal topilmadi: {channel_username}")
                continue
            except Exception as e:
                print(f"{idx}/{total}. {phone}: ⚠ Kanal tekshirishda xato: {e}")
                continue

            try:
                await client(GetParticipantRequest(channel=channel_username, participant=me.id))
                print(f"{idx}/{total}. {phone}: ⚠ Allaqachon obuna bo'lgan")
                subscribed_count += 1
                continue
            except:
                pass

            try:
                await client(JoinChannelRequest(channel_username))
                print(f"{idx}/{total}. {phone}: ✅ Obuna bo'ldi!")
                subscribed_count += 1

                with open("subscribed_channels.txt", "a", encoding='utf-8') as f:
                    f.write(f"{channel_username}|{session_name}|{phone}\n")

            except UserPrivacyRestrictedError:
                print(f"{idx}/{total}. {phone}: ❌ Maxfiylik to'siqlari")
            except FloodWaitError as e:
                print(f"{idx}/{total}. {phone}: ⏳ Kutilmoqda {e.seconds} soniya")
                await asyncio.sleep(e.seconds)
                try:
                    await client(JoinChannelRequest(channel_username))
                    print(f"{idx}/{total}. {phone}: ✅ Obuna bo'ldi! (qayta urinish)")
                    subscribed_count += 1
                except:
                    pass
            except Exception as e:
                print(f"{idx}/{total}. {phone}: ❌ Xatolik: {e}")

        except Exception as e:
            print(f"{idx}/{total}. {session_name}: ❌ Ulanishda xato: {e}")
        finally:
            if client.is_connected():
                await client.disconnect()

    print(f"\n📊 Natija: {subscribed_count}/{total} ta akkaunt muvaffaqiyatli obuna bo'ldi")
    input("\nEnter bosing...")

async def leave_channel():
    clear_screen()
    print("=== KANALDAN CHIQISH ===")

    if not os.path.exists("subscribed_channels.txt"):
        print("Hali hech qanday kanalga obuna qilinmagan!")
        input("\nEnter bosing...")
        return

    try:
        with open("subscribed_channels.txt", "r", encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
    except:
        print("Faylni o'qishda xatolik!")
        input("\nEnter bosing...")
        return

    if not lines:
        print("Ro'yxatda hech qanday kanal yo'q!")
        input("\nEnter bosing...")
        return

    channels_set = set()
    for line in lines:
        parts = line.split('|')
        if parts:
            channels_set.add(parts[0])

    channels = list(channels_set)

    if not channels:
        print("Kanallar ro'yxati topilmadi!")
        input("\nEnter bosing...")
        return

    print("\n📋 Obuna qilingan kanallar:")
    for i, ch in enumerate(channels, 1):
        count = sum(1 for line in lines if line.startswith(ch + "|"))
        print(f"{i}. {ch} ({count} ta akkaunt)")

    choice = input("\nQaysi kanaldan chiqmoqchisiz? (raqam kiriting): ").strip()
    try:
        choice = int(choice)
        if choice < 1 or choice > len(channels):
            print("❌ Noto'g'ri tanlov!")
            input("\nEnter bosing...")
            return
    except ValueError:
        print("❌ Raqam kiritishingiz kerak!")
        input("\nEnter bosing...")
        return

    selected_channel = channels[choice - 1]

    selected_sessions = []
    for line in lines:
        parts = line.split('|')
        if len(parts) >= 2 and parts[0] == selected_channel:
            selected_sessions.append(parts[1])

    if not selected_sessions:
        print(f"❌ {selected_channel} kanalida hech qanday akkaunt yo'q!")
        input("\nEnter bosing...")
        return

    print(f"\n📊 {len(selected_sessions)} ta akkaunt {selected_channel} kanalidan chiqmoqda...\n")

    left_count = 0
    total = len(selected_sessions)

    for idx, session_name in enumerate(selected_sessions, 1):
        session_path = os.path.join(SESSIONS_DIR, f"{session_name}.session")

        if not os.path.exists(session_path):
            print(f"{idx}/{total}. {session_name}: ❌ Session fayli topilmadi")
            continue

        client = TelegramClient(session_path, API_ID, API_HASH)

        try:
            await client.connect()
            if not await client.is_user_authorized():
                print(f"{idx}/{total}. {session_name}: ❌ Avtorizatsiya qilinmagan")
                continue

            me = await client.get_me()
            phone = me.phone or "Noma'lum"

            try:
                await client.get_entity(selected_channel)
            except:
                print(f"{idx}/{total}. {phone}: ⚠ Bu kanalga obuna bo'lmagan")
                continue

            try:
                await client(LeaveChannelRequest(selected_channel))
                print(f"{idx}/{total}. {phone}: ✅ Kanaldan chiqdi")
                left_count += 1
            except Exception as e:
                print(f"{idx}/{total}. {phone}: ❌ Chiqishda xato: {e}")

        except Exception as e:
            print(f"{idx}/{total}. {session_name}: ❌ Xatolik: {e}")
        finally:
            if client.is_connected():
                await client.disconnect()

    new_lines = [line for line in lines if not line.startswith(selected_channel + "|")]

    try:
        with open("subscribed_channels.txt", "w", encoding='utf-8') as f:
            for line in new_lines:
                f.write(line + "\n")
    except:
        print("⚠ Faylni yangilashda xatolik!")

    print(f"\n📊 Natija: {left_count}/{total} ta akkaunt kanaldan chiqdi")
    print(f"✅ {selected_channel} fayldan o'chirildi")

    input("\nEnter bosing...")

async def reaction():
    clear_screen()
    print("=== REAKSIYA QO'SHISH ===")

    sessions = get_sessions()
    if not sessions:
        print("Hech qanday akkaunt mavjud emas!")
        input("\nEnter bosing...")
        return

    url = input("Xabar havolasini kiriting (t.me/...):\n").strip()
    if not url:
        print("Havola bosh!")
        input("\nEnter bosing...")
        return

    try:
        limit = int(input(f"Nechta akkaunt ishlatilsin? (0=barchasi {len(sessions)}): "))
        if limit == 0:
            selected_sessions = sessions
        elif 1 <= limit <= len(sessions):
            selected_sessions = sessions[:limit]
        else:
            print("❌ Limit noto'g'ri!")
            input("\nEnter bosing...")
            return
    except ValueError:
        print("❌ Raqam kiritishingiz kerak!")
        input("\nEnter bosing...")
        return

    print("\n🎭 Reaksiya tanlang:")
    print("1. 👍 Salbiy")
    print("2. ❤️ Ijobiy")
    print("3. 🎭 Aralash")
    choice = input("Tanlov (1/2/3): ").strip()

    POS = ["👍", "❤️", "🔥", "👏", "😁", "🤩", "🎉"]
    NEG = ["👎", "😢", "🤮", "🤬", "😡", "💩"]

    if choice == "1":
        reactions = NEG
    elif choice == "2":
        reactions = POS
    elif choice == "3":
        reactions = NEG + POS
    else:
        print("❌ Noto'g'ri tanlov!")
        input("\nEnter bosing...")
        return

    try:
        count = int(input("Har bir akkaunt nechta reaksiya qo'shsin? (1-3): "))
        if not 1 <= count <= 3:
            print("⚠ 1-3 oralig'ida bo'lishi kerak, 1 qabul qilindi")
            count = 1
    except ValueError:
        print("⚠ Raqam kiritilmadi, 1 qabul qilindi")
        count = 1

    print(f"\n📤 Reaksiyalarni yuborish boshlandi... ({len(selected_sessions)} ta akkaunt)")

    try:
        parts = url.split("/")
        if len(parts) < 2:
            print("❌ Noto'g'ri havola formati!")
            input("\nEnter bosing...")
            return

        msg_id = int(parts[-1])
        if "/c/" in url:
            entity = int(parts[-2])
        else:
            entity = parts[-2]

        if not entity:
            print("❌ Havolada kanal/kontent topilmadi!")
            input("\nEnter bosing...")
            return

    except Exception as e:
        print(f"❌ Havolani tahlil qilishda xato: {e}")
        input("\nEnter bosing...")
        return

    success = 0
    total = len(selected_sessions)

    for idx, session in enumerate(selected_sessions, 1):
        path = os.path.join(SESSIONS_DIR, f"{session}.session")

        if not os.path.exists(path):
            print(f"{idx}/{total}. {session}: ❌ Session fayli topilmadi")
            continue

        client = TelegramClient(path, API_ID, API_HASH)

        try:
            await client.connect()
            if not await client.is_user_authorized():
                print(f"{idx}/{total}. {session}: ❌ Avtorizatsiya qilinmagan")
                continue

            try:
                ent = await client.get_entity(entity)
            except Exception as e:
                print(f"{idx}/{total}. {session}: ❌ Entity topilmadi: {e}")
                continue

            for reaction_num in range(count):
                reaction_emoji = random.choice(reactions)
                try:
                    await client(
                        SendReactionRequest(
                            peer=ent,
                            msg_id=msg_id,
                            reaction=[ReactionEmoji(reaction_emoji)]
                        )
                    )
                    print(f"{idx}/{total}. {session}: ✅ Reaktsiya {reaction_num+1} ({reaction_emoji})")
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"{idx}/{total}. {session}: ❌ Reaktsiya {reaction_num+1} xatosi: {e}")
                    break

            success += 1

        except Exception as e:
            print(f"{idx}/{total}. {session}: ❌ Xato: {e}")
        finally:
            try:
                if client.is_connected():
                    await client.disconnect()
            except:
                pass

    print(f"\n📊 Natija: {success}/{total} ta akkaunt muvaffaqiyatli reaktsiya qo'shdi")
    input("\nEnter bosing...")

async def set_2fa_all():
    clear_screen()
    print("=== 2FA O'RNATISH ===")
    sessions = get_sessions()
    if not sessions:
        print("Hech qanday akkaunt yo'q!")
        input("\nEnter bosing...")
        return

    needs_2fa = []
    print("🔍 Sessiyalar tahlil qilinmoqda...\n")

    total = len(sessions)
    for idx, session_name in enumerate(sessions, 1):
        session_path = os.path.join(SESSIONS_DIR, f"{session_name}.session")

        if not os.path.exists(session_path):
            print(f"{idx}/{total}. {session_name}: ❌ Session fayli topilmadi")
            continue

        client = TelegramClient(session_path, API_ID, API_HASH)

        try:
            await client.connect()
            if not await client.is_user_authorized():
                print(f"{idx}/{total}. {session_name}: ❌ Ulanmagan")
                continue

            me = await client.get_me()
            phone = me.phone if me.phone else "Noma'lum"
            full_name = f"{me.first_name} {me.last_name or ''}".strip()

            try:
                password_info = await client(GetPasswordRequest())
                if password_info.has_password:
                    print(f"{idx}/{total}. {session_name} ({phone}): ✅ 2FA bor")
                else:
                    needs_2fa.append((session_name, phone, full_name, session_path))
                    print(f"{idx}/{total}. {session_name} ({phone}): ❌ 2FA yo'q")
            except Exception as e:
                print(f"{idx}/{total}. {session_name}: ⚠ 2FA tekshirishda xato: {e}")

        except Exception as e:
            print(f"{idx}/{total}. {session_name}: ❌ Xato: {e}")
        finally:
            if client.is_connected():
                await client.disconnect()

    if not needs_2fa:
        print("\n✅ 2FA o'rnatish kerak bo'lgan akkaunt topilmadi.")
        input("\nEnter bosing...")
        return

    print(f"\n📊 {len(needs_2fa)} ta akkauntda 2FA yo'q:")
    for i, (session_name, phone, name, _) in enumerate(needs_2fa, 1):
        print(f"{i}. {session_name} - {phone} ({name})")

    code = input("\n🔐 Yangi 2FA parolni kiriting (4-6 raqam): ").strip()
    if not code or len(code) < 4 or len(code) > 6 or not code.isdigit():
        print("❌ Noto'g'ri parol! 4-6 raqam bo'lishi kerak.")
        input("\nEnter bosing...")
        return

    hint = input("📝 Parol uchun maslahat (ixtiyoriy): ").strip()
    if not hint:
        hint = "Auto set"

    print(f"\n🔄 2FA o'rnatilmoqda... ({code})\n")

    success_count = 0
    total_2fa = len(needs_2fa)

    for idx, (session_name, phone, name, session_path) in enumerate(needs_2fa, 1):
        print(f"{idx}/{total_2fa}. {session_name} ({phone})...")

        client = TelegramClient(session_path, API_ID, API_HASH)

        try:
            await client.connect()
            if not await client.is_user_authorized():
                print(f"   ❌ Avtorizatsiya qilinmagan")
                continue

            try:
                await client.edit_2fa(new_password=code, hint=hint)
                print(f"   ✅ 2FA o'rnatildi!")
                success_count += 1
            except Exception as e:
                print(f"   ❌ 2FA o'rnatishda xato: {e}")

        except Exception as e:
            print(f"   ❌ Ulanishda xato: {e}")
        finally:
            if client.is_connected():
                await client.disconnect()

    print(f"\n📊 Natija: {success_count}/{total_2fa} ta akkauntga 2FA o'rnatildi!")
    print(f"🔐 Parol: {code}")
    print(f"📝 Maslahat: {hint}")
    input("\nEnter bosing...")

async def is_admin(client, entity):
    try:
        me = await client.get_me()
        p = await client(GetParticipantRequest(entity, me.id))
        return isinstance(p.participant, (ChannelParticipantCreator, ChannelParticipantAdmin))
    except Exception as e:
        print(f"Admin tekshirishda xato: {e}")
        return False

async def get_password_obj(client):
    try:
        pwd = await client(functions.account.GetPasswordRequest())

        if not pwd.has_password:
            print("⚠ 2FA o'rnatilmagan! Avval 2FA o'rnating.")
            return None

        password_text = input("🔑 2FA parolini kiriting: ").strip()
        if not password_text:
            print("❌ Parol kiritilmadi!")
            return None

        try:
            pwd_hash = compute_check(pwd, password_text)
            return pwd_hash
        except Exception as e:
            print(f"❌ Parol hash hisoblashda xato: {e}")
            return None

    except Exception as e:
        print(f"❌ Parol olishda xato: {e}")
        return None

async def select_session():
    sessions = get_sessions()
    if not sessions:
        print("Hech qanday session yo'q!")
        return None

    clear_screen()
    print("=== SESSION TANLASH ===")
    for i, s in enumerate(sessions, 1):
        print(f"{i}. {s}")

    choice = input("\nSessionni tanlang (raqam): ").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(sessions):
            return sessions[idx]
    except ValueError:
        pass
    print("❌ Noto'g'ri tanlov!")
    return None

async def list_groups():
    session_name = await select_session()
    if not session_name:
        input("\nEnter bosing...")
        return

    session_path = os.path.join(SESSIONS_DIR, f"{session_name}.session")
    client = TelegramClient(session_path, API_ID, API_HASH)

    try:
        print(f"\n🔗 {session_name} ga ulanmoqda...")
        await client.start()
        me = await client.get_me()
        print(f"✅ Ulangan: {me.first_name}\n")

        dialogs = await client.get_dialogs(limit=100)

        total = 0
        admin_count = 0
        groups = []

        print(f"=== {session_name} GURUHLARI ===\n")

        for dialog in dialogs:
            if dialog.is_group:
                total += 1
                entity = dialog.entity
                groups.append({'name': dialog.name, 'id': entity.id, 'entity': entity, 'dialog': dialog})

        if not groups:
            print("❌ Hech qanday guruh topilmadi!")
            await client.disconnect()
            input("\nEnter bosing...")
            return

        print(f"📊 {total} ta guruh topildi. Tahlil qilinmoqda...\n")

        for group in groups:
            entity = group['entity']
            admin = await is_admin(client, entity)
            group_type = "Public" if hasattr(entity, 'username') and entity.username else "Private"

            print(f"📌 Nomi: {group['name']}")
            print(f"🆔 ID: {entity.id}")
            print(f"📋 Turi: {group_type}")

            if admin:
                admin_count += 1
                print("👑 Status: ADMIN")
                if not hasattr(entity, 'username') or not entity.username:
                    try:
                        link = await client(ExportChatInviteRequest(entity))
                        print(f"🔗 Invite link: {link.link}")
                    except Exception as e:
                        print(f"⚠ Link olinmadi: {e}")
            else:
                print("👤 Status: Oddiy a'zo")

            try:
                if hasattr(entity, 'participants_count'):
                    print(f"👥 A'zolar: {entity.participants_count}")
            except:
                pass

            print("-" * 40)

        print(f"\n📊 Jami guruhlar soni: {total}")
        print(f"👑 Admin bo'lgan guruhlar: {admin_count}")

    except Exception as e:
        print(f"❌ Xatolik: {e}")
    finally:
        if client.is_connected():
            await client.disconnect()

    input("\nEnter bosing...")

async def transfer_ownership(client, entity, user, password_obj):
    try:
        if not password_obj:
            print("❌ 2FA parol obj topilmadi!")
            return False

        channel_input = await client.get_input_entity(entity)

        print(f"🔄 Owner huquqini o'tkazish...")

        result = await client(EditCreatorRequest(
            channel=channel_input,
            user_id=user.id,
            password=password_obj
        ))

        print("✅ Owner huquqi muvaffaqiyatli o'tkazildi!")
        return True

    except PasswordHashInvalidError:
        print("❌ 2FA parol noto'g'ri!")
        return False
    except Exception as e:
        error_msg = str(e)
        print(f"⚠ Owner o'tkazishda xato: {error_msg}")
        return False

async def transfer_groups():
    session_name = await select_session()
    if not session_name:
        input("\nEnter bosing...")
        return

    username = input("Username kiriting (@user123 yoki user123): ").strip()
    if not username:
        print("❌ Username kiritilmadi!")
        input("\nEnter bosing...")
        return

    if not username.startswith("@"):
        username = "@" + username

    try:
        count = int(input("Nechta guruhni o'tkazmoqchisiz? (0 = hammasi): "))
        if count < 0:
            print("❌ Musbat son kiriting!")
            input("\nEnter bosing...")
            return
    except ValueError:
        print("❌ Raqam kiritishingiz kerak!")
        input("\nEnter bosing...")
        return

    owner_choice = input("Owner ham qilinsinmi? (y/n): ").lower()
    if owner_choice not in ['y', 'n']:
        print("❌ y yoki n kiriting!")
        input("\nEnter bosing...")
        return

    session_path = os.path.join(SESSIONS_DIR, f"{session_name}.session")
    client = TelegramClient(session_path, API_ID, API_HASH)

    try:
        print(f"\n🔗 {session_name} ga ulanmoqda...")
        await client.start()
        me = await client.get_me()
        print(f"✅ Ulandan: {me.first_name}")

        try:
            user = await client.get_entity(username)
            print(f"✅ User topildi: {user.first_name} (@{user.username})")
        except Exception as e:
            print(f"❌ User topilmadi: {e}")
            await client.disconnect()
            input("\nEnter bosing...")
            return

        password_obj = None
        if owner_choice == 'y':
            print("\n🔐 Owner qilish uchun 2FA parol kerak...")
            password_obj = await get_password_obj(client)
            if not password_obj:
                print("⚠ 2FA parol kiritilmadi, owner qilish amalga oshmaydi!")
                owner_choice = 'n'
            else:
                print("✅ 2FA parol tasdiqlandi!")

        dialogs = await client.get_dialogs(limit=200)

        eligible_groups = []
        print(f"\n🔍 Admin bo'lgan guruhlar qidirilmoqda...")

        for dialog in dialogs:
            if dialog.is_group:
                try:
                    if await is_admin(client, dialog.entity):
                        eligible_groups.append(dialog)
                        print(f"   ✅ {dialog.name} - Admin")
                    else:
                        print(f"   ❌ {dialog.name} - Admin emas")
                except Exception as e:
                    print(f"   ⚠ {dialog.name} - Tekshirishda xato: {e}")

        if not eligible_groups:
            print("❌ Admin bo'lgan guruh topilmadi!")
            await client.disconnect()
            input("\nEnter bosing...")
            return

        print(f"\n📊 {len(eligible_groups)} ta admin bo'lgan guruh topildi")

        if count == 0 or count > len(eligible_groups):
            count = len(eligible_groups)

        print(f"\n🚀 {count} ta guruhni o'tkazish boshlanmoqda...")

        done = 0
        failed = 0
        owner_success = 0
        owner_failed = 0

        for dialog in eligible_groups[:count]:
            entity = dialog.entity

            print(f"\n➡ [{done+1}/{count}] {dialog.name} guruhiga ishlov berilmoqda...")

            try:
                try:
                    await client(InviteToChannelRequest(entity, [user]))
                    print("   👤 User qo'shildi")
                except UserAlreadyParticipantError:
                    print("   ⚠ User allaqachon guruhda")
                except UserPrivacyRestrictedError:
                    print("   ❌ User maxfiylik sabab qo'shilmadi")
                    failed += 1
                    continue
                except Exception as e:
                    print(f"   ❌ User qo'shishda xato: {e}")
                    failed += 1
                    continue

                await asyncio.sleep(2)

                try:
                    rights = ChatAdminRights(
                        change_info=True,
                        post_messages=True,
                        edit_messages=True,
                        delete_messages=True,
                        ban_users=True,
                        invite_users=True,
                        pin_messages=True,
                        add_admins=True,
                        anonymous=False,
                        manage_call=True,
                        other=True
                    )
                    await client(EditAdminRequest(entity, user, rights, "Full Admin"))
                    print("   👑 To'liq admin qilindi")
                except Exception as e:
                    print(f"   ❌ Admin qilishda xato: {e}")
                    failed += 1
                    continue

                owner_transferred = False
                if owner_choice == 'y' and password_obj:
                    print("   👑 Owner huquqini o'tkazish...")
                    success = await transfer_ownership(client, entity, user, password_obj)
                    if success:
                        owner_success += 1
                        owner_transferred = True
                    else:
                        owner_failed += 1
                        print("   ⚠ Owner o'tkazilmadi, lekin admin qilindi")

                done += 1
                status = "Owner" if owner_transferred else "Admin"
                print(f"   ✅ {dialog.name} - {status} qilindi")

                if done < count:
                    wait_time = random.uniform(3, 7)
                    print(f"   ⏳ Keyingi guruhga o'tish: {wait_time:.1f}s")
                    await asyncio.sleep(wait_time)

            except FloodWaitError as e:
                print(f"   ⏳ Flood: {e.seconds} soniya kuting...")
                await asyncio.sleep(e.seconds)
                failed += 1
            except Exception as e:
                print(f"   ❌ Xatolik: {e}")
                failed += 1

        print(f"\n{'='*60}")
        print(f"🏁 TUGADI!")
        print(f"{'='*60}")
        print(f"📊 Jami guruhlar: {count} ta")
        print(f"✅ Muvaffaqiyatli: {done} ta")
        print(f"❌ Xatolar: {failed} ta")
        if owner_choice == 'y':
            print(f"👑 Owner o'tkazildi: {owner_success} ta")
            print(f"⚠ Owner o'tkazilmadi: {owner_failed} ta")
        print(f"{'='*60}")

    except Exception as e:
        print(f"❌ Umumiy xato: {e}")
    finally:
        if client.is_connected():
            await client.disconnect()

    input("\nEnter bosing...")


# ============================================================
# MENYU
# ============================================================

def show_menu():
    clear_screen()
    try:
        logo = pyfiglet.figlet_format("Telegram", font="slant")
        print(Fore.CYAN + Style.BRIGHT + logo)
    except:
        print(Fore.CYAN + Style.BRIGHT + "=" * 50)
        print(Fore.CYAN + Style.BRIGHT + "         TELEGRAM MANAGEMENT PANEL        ")
        print(Fore.CYAN + Style.BRIGHT + "=" * 50)

    # Botlar sonini ko'rsatish
    bots = get_bots()
    bot_info = f"({len(bots)} ta bot saqlangan)" if bots else "(bot yo'q!)"

    print(Fore.WHITE + "=" * 50)
    print(Fore.CYAN + Style.BRIGHT + "           TELEGRAM PANEL            ".center(50))
    print(Fore.WHITE + "=" * 50)

    menu_items = [
        (Fore.GREEN,   "[1]  Hisob qo'shish"),
        (Fore.GREEN,   "[2]  Hisobni o'chirish"),
        (Fore.GREEN,   "[3]  Faol akkauntlar"),
        (Fore.GREEN,   "[4]  Guruh ochish"),
        (Fore.MAGENTA, "[5]  2FA o'rnatish"),
        (Fore.GREEN,   "[6]  Kanalga obuna"),
        (Fore.RED,     "[7]  Kanaldan chiqish"),
        (Fore.GREEN,   "[8]  Reaksiya qo'shish"),
        (Fore.MAGENTA, "[9]  Guruh o'tkazish"),
        (Fore.MAGENTA, "[10] Guruhlarni ko'rish"),
        (Fore.YELLOW,  f"[11] Botlarni boshqarish {bot_info}"),
        (Fore.RED,     "[0]  Chiqish"),
    ]

    for color, item in menu_items:
        print(color + Style.BRIGHT + "| " + item)

    print(Fore.WHITE + "=" * 50)


# ============================================================
# ASOSIY DASTUR
# ============================================================

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
        elif choice == '8':
            await reaction()
        elif choice == '9':
            await transfer_groups()
        elif choice == '10':
            await list_groups()
        elif choice == '11':
            manage_bots()
        elif choice == '0':
            clear_screen()
            print("✅ Dastur to'xtatildi! Xayr!")
            break
        else:
            print("❌ Noto'g'ri raqam!")
            input("\nEnter bosing...")

if __name__ == '__main__':
    init(autoreset=True)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✅ Dastur foydalanuvchi tomonidan to'xtatildi!")
    except Exception as e:
        print(f"\n❌ Kutilmagan xatolik: {e}")
        input("\nDastur yopilmoqda...")
