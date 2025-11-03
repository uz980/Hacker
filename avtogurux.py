from telethon.sync import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import InputPeerUser
from telethon.errors import UserPrivacyRestrictedError, FloodWaitError, UserAlreadyParticipantError
import time
import os

# API ID va Hash (my.telegram.org)
api_id = '22210367'
api_hash = '29a1097b9da5f9a6e8bafaaee6dc6ae4'

session_file = 'member_mover_session'

def login():
    phone = input("Telefon raqamingiz (+998...): ")
    client = TelegramClient(session_file, api_id, api_hash)
    client.start(phone=phone)
    print("Login muvaffaqiyatli! Session saqlandi.")
    return client

if __name__ == "__main__":
    # Session
    client = TelegramClient(session_file, api_id, api_hash)
    client.connect()
    if not client.is_user_authorized():
        client = login()

    with client:
        print("Guruhdan guruhga a'zo ko'chirish (xavfsiz rejim)\n")

        # 1-guruh (a'zolar ko'rinadigan bo'lishi kerak)
        source_input = input("1-guruh (a'zolar olinadigan): @username yoki link: ")
        source_entity = client.get_entity(source_input)

        # 2-guruh (SIZ ADMIN bo'lishingiz kerak)
        target_input = input("2-guruh (a'zolar qo'shiladigan): @username yoki link: ")
        target_entity = client.get_entity(target_input)

        # Limitlar
        limit = int(input("Nechta a'zo qo'shmoqchisiz? (50-100 tavsiya etiladi): "))
        delay = int(input("Har bir qo'shish orasida necha sekund kutish? (5-10): "))

        print(f"\nA'zolar yuklanmoqda... (maks: {limit})")
        members = client.get_participants(source_entity, aggressive=True)

        added = 0
        skipped_privacy = 0
        skipped_already = 0
        skipped_bot = 0
        skipped_error = 0

        print("\n" + "="*60)
        for user in members:
            if added >= limit:
                break

            # Bot, o'chirilgan, o'zimni o'tkazib yuborish
            if user.bot or user.deleted or user.is_self:
                skipped_bot += 1
                continue

            # Allaqa'chon 2-guruxda bo'lsa
            try:
                client.get_participants(target_entity, search=user.id, limit=1)
                skipped_already += 1
                continue
            except:
                pass  # topilmadi → qo'shish mumkin

            try:
                # Qo'shish
                client(InviteToChannelRequest(
                    channel=target_entity,
                    users=[InputPeerUser(user.id, user.access_hash)]
                ))
                added += 1
                print(f"{added}/{limit} ✅ {user.first_name} (@{user.username or '—'}) qo'shildi.")
                time.sleep(delay)

            except UserPrivacyRestrictedError:
                # Maxfiylik sozlamasi tufayli qo'shib bo'lmaydi
                skipped_privacy += 1
                print(f"❌ {user.first_name} — guruhga qo'shilishni o'chirgan.")
                time.sleep(1)

            except UserAlreadyParticipantError:
                skipped_already += 1
                print(f"⚠️ {user.first_name} allaqachon a'zo.")
                time.sleep(1)

            except FloodWaitError as e:
                wait = e.seconds
                print(f"⏳ FLOOD! {wait} sekund kutilyapti...")
                time.sleep(wait + 5)

            except Exception as e:
                skipped_error += 1
                print(f"⚠️ Xato: {e}")
                time.sleep(2)

        # Natija
        print("\n" + "="*60)
        print("JARAYON TUGADI".center(60))
        print("="*60)
        print(f"Qo'shildi          : {added}")
        print(f"Maxfiylik (o'chirgan) : {skipped_privacy}")
        print(f"Allaqa'chon a'zo   : {skipped_already}")
        print(f"Bot/o'chirilgan    : {skipped_bot}")
        print(f"Boshqa xato        : {skipped_error}")
        print(f"Jami tekshirildi   : {added + skipped_privacy + skipped_already + skipped_bot + skipped_error}")
        print("="*60)
