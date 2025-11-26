# -*- coding: utf-8 -*-
import pyfiglet
import asyncio
import os, random
import random  # ðŸ‘ˆ QO'SHILDI
from colorama import init, Fore, Back, Style
from telethon import TelegramClient
from telethon.tl.functions.channels import CreateChannelRequest, InviteToChannelRequest
from telethon.tl import functions
from telethon.errors import (
    SessionPasswordNeededError,
    UserAlreadyParticipantError,
    ChatNotModifiedError,
)
from telethon.tl.functions.account import GetPasswordRequest
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.messages import SendReactionRequest  # ðŸ‘ˆ QO'SHILDI
from telethon.tl.types import ReactionEmoji

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

def clear():
    os.system("clear")

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

async def subscribe_channel():
    clear_screen()
    print("=== KANALGA OBUNA QILDIRISH ===")

    sessions = get_sessions()
    if not sessions:
        print("Hech qanday session mavjud emas!")
        input("\nEnter bosing...")
        return

    # Kanal soâ€˜rash
    channel_username = input("Qaysi kanalga obuna qilamiz? (@ bilan): ").strip()
    if not channel_username.startswith("@"):
        print("Noto'g'ri format! @kanal tarzida kiriting!")
        input("\nEnter bosing...")
        return

    # Nechta akkaunt ishlasin?
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
                print(f"{session_name}: Avtorizatsiya qilinmagan â€” oâ€˜tkazildi âŒ")
                await client.disconnect()
                continue

            me = await client.get_me()
            phone = me.phone or "Noma'lum"

            # âš ï¸ Avval tekshiramiz â€” allaqachon obuna boâ€˜lganmi?
            already = False
            try:
                await client.get_participant(channel_username)
                already = True
            except:
                pass

            if already:
                print(f"{phone}: Allaqachon obuna boâ€˜lgan â€” tashlab ketildi âŒ")
                await client.disconnect()
                continue

            # ðŸ”¥ OBUNA QILAMIZ
            try:
                await client(JoinChannelRequest(channel_username))
                print(f"{phone}: Muvaffaqiyatli obuna boâ€˜ldi! âœ…")
                subscribed_count += 1

                # <<< FAYLGA YOZILADI >>>
                with open("subscribed_channels.txt", "a") as f:
                    f.write(channel_username + "\n")

            except Exception as e:
                print(f"{phone}: Obuna boâ€˜lmadi: {e}")

        except Exception as e:
            print(f"{session_name}: Xatolik: {e}")

        finally:
            if client.is_connected():
                await client.disconnect()

    print(f"\nJami {subscribed_count} ta akkaunt {channel_username} kanaliga obuna boâ€˜ldi.")
    input("\nEnter bosing...")

async def leave_channel():
    clear_screen()
    print("=== KANALDAN CHIQISH ===")

    # subscribe_channel orqali qoâ€˜shilgan kanallar roâ€˜yxati
    if not os.path.exists("subscribed_channels.txt"):
        print("Hali hech qanday kanalga obuna qilinmagan!")
        input("\nEnter bosing...")
        return

    with open("subscribed_channels.txt", "r") as f:
        channels = list(set([x.strip() for x in f.readlines() if x.strip()]))

    if not channels:
        print("Roâ€˜yxatda hech qanday kanal yoâ€˜q!")
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
        print("Notoâ€˜gâ€˜ri tanlov!")
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

            # âš ï¸ AVVAL TEKSHIRAMIZ: shu kanalga obuna boâ€˜lganmi?
            try:
                await client.get_participant(selected_channel)
            except:
                print(f"{phone}: Bu kanalga obuna boâ€˜lmagan â€” oâ€˜tkazildi âŒ")
                await client.disconnect()
                continue

            # â— Endi chiqish
            try:
                await client(LeaveChannelRequest(selected_channel))
                print(f"{phone}: Chiqdi âœ…")
            except Exception as e:
                print(f"{phone}: Chiqishda xatolik: {e}")

        except Exception as e:
            print(f"{session_name}: Xatolik: {e}")

        finally:
            if client.is_connected():
                await client.disconnect()

    # Fayldan oâ€˜chirib tashlaymiz
    channels.remove(selected_channel)
    with open("subscribed_channels.txt", "w") as f:
        for ch in channels:
            f.write(ch + "\n")

    print(f"\nBarcha akkauntlar {selected_channel} kanalidan chiqdi!")
    input("\nEnter bosing...")

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

    # nechta akkaunt ishlashini so‘raymiz
    try:
        limit = int(input(f"Nechta akkaunt ishlatilsin? (0=barchasi {len(sessions)}): "))
    except:
        print("Notogri kiritildi!")
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

    # reaksiya variantlari
    POS = ["👍", "❤️", "🔥", "👏", "😁", "🎉", "💯", "😍"]
    NEG = ["👎", "😡", "😢", "🤬", "😱", "😐"]

    if choice == "1":
        reactions = NEG
    elif choice == "2":
        reactions = POS
    elif choice == "3":
        reactions = NEG + POS
    else:
        print("Notogri tanlov!")
        input()
        return

    try:
        count = int(input("Nechta reaksiya qoshilsin? (1-3): "))
        if not 1 <= count <= 3:
            count = 1
    except:
        count = 1

    print(f"Reaksiyalarni yuborish boshlandi... ({len(selected_sessions)} ta akkaunt)")

    success = 0

    # havolani parslash (to‘liq to‘g‘ri ishlaydigan)
    try:
        parts = url.split("/")
        msg_id = int(parts[-1])
        if "/c/" in url:
            entity = int(parts[-2])
        else:
            entity = parts[-2]
    except:
        print("Havola notogri!")
        input()
        return

    # asosiy aylanma
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
                        peer = ent,
                        msg_id = msg_id,
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
    

# Windows va Linux/Mac uchun colorama ishlatish
init(autoreset=True)

def show_menu():
    os.system("clear" if os.name == "posix" else "cls")

    # Telegram logosi - ko'k rangda
    logo = pyfiglet.figlet_format("Telegram", font="slant")
    print(Fore.CYAN + Style.BRIGHT + logo)

    # Sarlavha
    print(Fore.WHITE + "═" * 44)
    print(Fore.CYAN + Style.BRIGHT + "           TELEGRAM PANEL            ".center(44))
    print(Fore.WHITE + "═" * 44)

    # Menyu elementlari
    menu = [
        "[1] Hisoblar qoÊ»shish.",
        "[2] Hisobdan chiqish.",
        "[3] Faol akkauntlar",
        "[4] Gruh ochish.",
        "[5] 2fa ulash.",
        "[6] Kanalga azo.",
        "[7] Aytgan kanallardan chiqish.",
        "[0] Chiqish"
    ]

    # Rangli menyu + | chizig'i
    for item in menu:
        if "[7]" in item or "[0]" in item:
            print(Fore.RED + Style.BRIGHT + "| " + item)      # Muhim bo'limlar qizil
        elif "[5]" in item:
            print(Fore.MAGENTA + Style.BRIGHT + "| " + item)   # Botni ishga tushirish binafsha
        else:
            print(Fore.GREEN + "| " + item)

    print(Fore.WHITE + "•" * 44)

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
    asyncio.run(main())
