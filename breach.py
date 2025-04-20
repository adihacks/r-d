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
