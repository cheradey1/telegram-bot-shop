import os
import stripe
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

PRICE_USD = 50  # ціна

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💳 Оплатити", callback_data="pay")],
        [InlineKeyboardButton("📩 Заявка", callback_data="order")]
    ]
    await update.message.reply_text(
        "Вітаю! Ви можете оплатити або залишити заявку 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "pay":
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Telegram-бот"},
                    "unit_amount": PRICE_USD * 100,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="https://t.me/your_bot",
            cancel_url="https://t.me/your_bot",
        )

        await query.message.reply_text(
            f"💳 Оплата за посиланням:\n{session.url}"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="🧾 Хтось відкрив оплату Stripe"
        )

    elif query.data == "order":
        await query.message.reply_text(
            "✍️ Напишіть, що вам потрібно:"
        )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.run_polling()
