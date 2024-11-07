import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

from db import session, User, Message, init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


admin_user_id_str = os.getenv("ADMIN_USER_ID")
if not admin_user_id_str:
    raise ValueError("ADMIN_USER_ID must be set")

ADMIN_USER_ID = int(admin_user_id_str)


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN must be set")


BROADCAST_MESSAGE = 1


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    try:
        if update.message is None or update.message.from_user is None:
            return
        user_id = update.message.from_user.id
        user = session.query(User).filter_by(user_id=user_id).first()

        if not user:
            is_admin = user_id == ADMIN_USER_ID
            user = User(user_id=user_id, is_admin=is_admin)
            session.add(user)
            session.commit()
            if is_admin:
                await update.message.reply_text(
                    "Вы являетесь администратором, и сохранены как администратор"
                )
            await update.message.reply_text("Вы подписались на рассылку")
        else:
            await update.message.reply_text("Вы уже подписаны на рассылку")
    except Exception as e:
        logging.error(f"Error in start command: {e}")
        if ADMIN_USER_ID:
            await context.bot.send_message(
                chat_id=ADMIN_USER_ID, text=f"Произошла ошибка в команде /start: {e}"
            )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    try:
        if update.message is None or update.message.from_user is None:
            return
        help_text = (
            "/start - Подписаться на рассылку\n" "/help - Показать это сообщение\n"
        )

        if update.message.from_user.id == ADMIN_USER_ID:
            help_text += (
                "/broadcast - Начать рассылку сообщения\n"
                "/list_users - Показать количество подписавшихся пользователей\n"
                "/list_messages - Показать все отправленные сообщения\n"
            )

        await update.message.reply_text(help_text)
    except Exception as e:
        logging.error(f"Error in help command: {e}")
        if ADMIN_USER_ID:
            await context.bot.send_message(
                chat_id=ADMIN_USER_ID, text=f"Произошла ошибка в команде /help: {e}"
            )


async def list_users(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    try:
        if update.message is None or update.message.from_user is None:
            return
        if update.message.from_user.id != ADMIN_USER_ID:
            await update.message.reply_text(
                "У вас нет прав для выполнения этой команды."
            )
            return

        user_count = session.query(User).count()
        await update.message.reply_text(
            f"Количество подписавшихся пользователей: {user_count}"
        )
    except Exception as e:
        logging.error(f"Error in list_users command: {e}")
        if ADMIN_USER_ID:
            await context.bot.send_message(
                chat_id=ADMIN_USER_ID,
                text=f"Произошла ошибка в команде /list_users: {e}",
            )


async def list_messages(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    try:
        if update.message is None or update.message.from_user is None:
            return
        if update.message.from_user.id != ADMIN_USER_ID:
            await update.message.reply_text(
                "У вас нет прав для выполнения этой команды."
            )
            return

        messages = session.query(Message).all()
        if not messages:
            await update.message.reply_text("Нет отправленных сообщений.")
            return

        message_list = "\n".join(
            [f"{message.timestamp} - {message.message}" for message in messages]
        )
        await update.message.reply_text(
            f"Список отправленных сообщений:\n{message_list}"
        )
    except Exception as e:
        logging.error(f"Error in list_messages command: {e}")
        if ADMIN_USER_ID:
            await context.bot.send_message(
                chat_id=ADMIN_USER_ID,
                text=f"Произошла ошибка в команде /list_messages: {e}",
            )


async def broadcast_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    try:
        if update.message is None or update.message.from_user is None:
            return ConversationHandler.END
        user_id = update.message.from_user.id
        user = session.query(User).filter_by(user_id=user_id).first()

        if user and user.is_admin:
            await update.message.reply_text(
                "Введите сообщение для рассылки. Отмена - /cancel"
            )
            return BROADCAST_MESSAGE
        else:
            await update.message.reply_text(
                "У вас нет прав для выполнения этой команды."
            )
            return ConversationHandler.END
    except Exception as e:
        logging.error(f"Error in broadcast_start command: {e}")
        if ADMIN_USER_ID:
            await context.bot.send_message(
                chat_id=ADMIN_USER_ID,
                text=f"Произошла ошибка в команде /broadcast: {e}",
            )
        return ConversationHandler.END


async def broadcast_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    try:
        if update.message is None or update.message.from_user is None:
            return ConversationHandler.END
        user_id = update.message.from_user.id
        user = session.query(User).filter_by(user_id=user_id).first()

        if user and user.is_admin:
            message_text = update.message.text
            if message_text is None or message_text == "/cancel":
                await update.message.reply_text("Рассылка отменена")
                return ConversationHandler.END

            for user in session.query(User).all():
                await context.bot.send_message(
                    chat_id=user.user_id,  # type: ignore
                    text=message_text,
                )

            message = Message(user_id=user_id, message=message_text)
            session.add(message)
            session.commit()

            await update.message.reply_text("Сообщение разослано")
        return ConversationHandler.END
    except Exception as e:
        logging.error(f"Error in broadcast_message command: {e}")
        if ADMIN_USER_ID:
            await context.bot.send_message(
                chat_id=ADMIN_USER_ID,
                text=f"Произошла ошибка в команде /broadcast: {e}",
            )
        return ConversationHandler.END


def main() -> None:
    application = ApplicationBuilder().token(str(TELEGRAM_BOT_TOKEN)).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list_users", list_users))
    application.add_handler(CommandHandler("list_messages", list_messages))

    broadcast_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                "broadcast",
                broadcast_start,
            )
        ],
        states={
            BROADCAST_MESSAGE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    broadcast_message,
                )
            ]
        },
        fallbacks=[],
    )
    application.add_handler(broadcast_handler)

    application.run_polling()


if __name__ == "__main__":
    init_db()
    main()
