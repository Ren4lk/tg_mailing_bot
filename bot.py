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


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.message is None or update.message.from_user is None:
        return
    help_text = (
        "/start - Подписаться на рассылку\n" + "/help - Показать это сообщение\n"
    )

    if update.message.from_user.id == ADMIN_USER_ID:
        help_text += "/broadcast - Начать рассылку сообщения\n"

    await update.message.reply_text(help_text)


async def broadcast_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
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
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return ConversationHandler.END


async def broadcast_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
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
                chat_id=user.user_id.item(),
                text=message_text,
            )

        message = Message(user_id=user_id, message=message_text)
        session.add(message)
        session.commit()

        await update.message.reply_text("Сообщение разослано")
    return ConversationHandler.END


def main() -> None:
    application = ApplicationBuilder().token(str(TELEGRAM_BOT_TOKEN)).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

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
