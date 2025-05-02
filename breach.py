import asyncio
from telethon import TelegramClient, events
import aiomysql

# Telegram Configuration
api_id = 
api_hash = ""
phone_number = '+YOUR_PHONE'
YOUR_PERSONAL_CHAT = "@"

MONITOR_CHANNELS = [
    "breachdetector",
    "https://t.me/+W7TYjNAEjqBkY2U6",
    # Add more channels here
]

KEYWORDS = [
    "data leak",
    "ransom feed",
    "credential leak",
    # Add more keywords here
]

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'DB_USER',
    'password': '73033',
    'db': 'DB_NAME',
    'charset': 'utf8mb4',
    'cursorclass': aiomysql.DictCursor
}

TABLE_NAME = 'alerts'

async def main():
    client = TelegramClient('user_session', api_id, api_hash)
    
    await client.start(phone=phone_number)
    print("✅ Logged in successfully")

    # Create database connection pool
    pool = await aiomysql.create_pool(**DB_CONFIG)
    print("✅ Database connected")

    @client.on(events.NewMessage(chats=MONITOR_CHANNELS))
    async def message_handler(event):
        message_text = event.message.text.lower()
        matched_keywords = [kw for kw in KEYWORDS if kw in message_text]
        
        if matched_keywords:
            try:
                # Get direct post URL
                if event.chat.username:
                    source_url = f"https://t.me/{event.chat.username}/{event.message.id}"
                else:
                    # For private channels/groups with invite links
                    chat = await event.get_chat()
                    if hasattr(chat, 'username') and chat.username:
                        source_url = f"https://t.me/{chat.username}/{event.message.id}"
                    else:
                        source_url = f"https://t.me/c/{chat.id}/{event.message.id}"

                channel_name = f"@{event.chat.username}" if event.chat.username else event.chat.title
                formatted_keywords = ", ".join([k.capitalize() for k in matched_keywords])

                # Send to Telegram
                alert_message = (
                    f"🚨 Alert from {channel_name}\n"
                    f"🔍 Matched keywords: {formatted_keywords}\n\n"
                    f"{event.message.text}"
                )
                await client.send_message(YOUR_PERSONAL_CHAT, alert_message)

                # Send to database
                async with pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(f"""
                            INSERT INTO {TABLE_NAME} 
                            (message_text, source_url, matched_keywords)
                            VALUES (%s, %s, %s)
                        """, (event.message.text, source_url, formatted_keywords))
                        await conn.commit()

                print(f"✅ Alert handled: {source_url}")

            except Exception as e:
                print(f"🚨 Error: {str(e)}")

    print(f"👂 Monitoring {len(MONITOR_CHANNELS)} channels...")
    await client.run_until_disconnected()
    pool.close()
    await pool.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())




-->>>>>for sql _>....>>>
setup the sql , then make a user so that u can add database ->
then 


-- Create database
CREATE DATABASE telegram_monitor;
USE telegram_monitor;

-- Create user (replace 'password' with your own)
CREATE USER 'telegram_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON telegram_monitor.* TO 'telegram_user'@'localhost';
FLUSH PRIVILEGES;

-- Create alerts table
CREATE TABLE alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message_text TEXT NOT NULL,
    source_url VARCHAR(255) NOT NULL,
    matched_keywords VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'DB_USER',
    'password': 'DB_PASSWORD',
    'db': 'DB_NAME',
    'charset': 'utf8mb4',
    'cursorclass': aiomysql.DictCursor
}



CREATE TABLE alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message_text TEXT NOT NULL,
    source_url VARCHAR(255) NOT NULL,
    matched_keywords VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


___--_____-----____-->>>


import asyncio
from telethon import TelegramClient, events

# Configuration
api_id = 
api_hash = ""
phone_number = '+91'
YOUR_PERSONAL_CHAT = "@adihacks2"

MONITOR_CHANNELS = [
    "breachdetector",
    "https://t.me/+W7TYjNAEjqBkY2U6",
    # Add more channels here
]

KEYWORDS = [
    "data leak",
    "ransom feed",
    "credential leak",
    # Add more keywords here
]

async def main():
    client = TelegramClient('user_session', api_id, api_hash)
    
    await client.start(phone=phone_number)
    print("✅ Logged in successfully")

    @client.on(events.NewMessage(chats=MONITOR_CHANNELS))
    async def message_handler(event):
        message_text = event.message.text.lower()
        # Find all matching keywords
        matched_keywords = [keyword for keyword in KEYWORDS 
                          if keyword.lower() in message_text]
        
        if matched_keywords:
            try:
                channel_name = f"@{event.chat.username}" if event.chat.username else event.chat.title
                # Format keywords with first letter capitalized
                formatted_keywords = ", ".join([k.capitalize() for k in matched_keywords])
                
                alert_message = (
                    f"🚨 Alert from {channel_name}\n"
                    f"🔍 Matched keywords: {formatted_keywords}\n\n"
                    f"{event.message.text}"
                )

                await client.send_message(
                    YOUR_PERSONAL_CHAT,
                    alert_message,
                    parse_mode='html'
                )
                print(f"New alert from {channel_name} - Triggers: {formatted_keywords}")
            except Exception as e:
                print(f"Error handling message: {str(e)}")

    print(f"👂 Monitoring {len(MONITOR_CHANNELS)} channels...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
