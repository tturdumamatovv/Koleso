import asyncio

from telegram import Bot


async def async_send_message(bot_token, chat_id, message):
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message)


def send_telegram_message(bot_token, chat_id, message):
    try:
        asyncio.run(async_send_message(bot_token, chat_id, message))
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")
