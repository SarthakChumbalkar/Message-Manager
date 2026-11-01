import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient

load_dotenv()

api_id = os.getenv("TELEGRAM_API_ID", "").strip()
api_hash = os.getenv("TELEGRAM_API_HASH", "").strip()
phone = os.getenv("TELEGRAM_PHONE", "").strip()

if not api_id or not api_hash:
    raise RuntimeError("Set TELEGRAM_API_ID and TELEGRAM_API_HASH in your .env file.")

client = TelegramClient("telegram_session", int(api_id), api_hash)


def connect_telegram():
    if not client.is_connected():
        client.start(phone=phone or None)
    return client




def get_chats(limit=30):
    tg = connect_telegram()
    chats = []

    for dialog in tg.iter_dialogs():

        # Exclude groups, channels, and bots
        if not dialog.is_user:
            continue

        if getattr(dialog.entity, "bot", False):
            continue

        last_message = dialog.message

        chats.append({
            "id": dialog.id,
            "name": dialog.name or "Unknown",
            "last_message": (
                last_message.message or "[Media message]"
                if last_message else ""
            ),
            "unread_count": dialog.unread_count
        })

        if len(chats) >= limit:
            break

    return chats



def get_messages(chat_id, limit=50):
    tg = connect_telegram()
    entity = tg.get_entity(int(chat_id))
    messages = tg.get_messages(entity, limit=limit)
    result = []
    for message in reversed(messages):
        result.append({
            "id": message.id,
            "sender": "owner" if message.out else "customer",
            "text": message.message or "[Media message]",
            "date": message.date.strftime("%Y-%m-%d %H:%M") if message.date else "",
        })
    return result


def send_message(chat_id, text):
    tg = connect_telegram()
    entity = tg.get_entity(int(chat_id))
    return tg.send_message(entity, text)


if __name__ == "__main__":
    tg = connect_telegram()
    me = tg.get_me()
    print(f"Connected to Telegram as: {me.first_name}")
    for index, chat in enumerate(get_chats(20), start=1):
        print(f"{index}. {chat['name']} | Unread: {chat['unread_count']} | Chat ID: {chat['id']}")
    print("Telegram connection successful.")
