# agent/telegram_bot.py
from telegram import Bot
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class TelegramNotifier:
    _bot = None

    @classmethod
    def get_bot(cls):
        if cls._bot is None and settings.TELEGRAM_BOT_TOKEN:
            cls._bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        return cls._bot

    @classmethod
    def send_task_notification(cls, user_telegram_id, task):
        try:
            bot = cls.get_bot()
            if bot:
                message = (
                    f"🎯 New Task Available!\n"
                    f"**{task.title}**\n"
                    f"Reward: {task.xp_reward} XP + {task.token_reward} LEARN\n"
                    f"[Start Task](https://yourdomain.com/task/{task.id})"
                )
                bot.send_message(
                    chat_id=user_telegram_id, text=message, parse_mode="Markdown"
                )
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
