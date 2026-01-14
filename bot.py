import os
import stripe
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

PRODUCTS = {
    "lead": ("🤖 Бот для заявок", 79),
    "pay": ("💳 Бот з онлайн-оплатою", 199),
    "shop": ("🛒 Telegram-магазин", 299),
    "ai": ("🧠 AI-бот (ChatGPT)", 399),
    "channel": ("📢 Бот для каналу", 149),
    "admin": ("🛡 Адмін-бот", 99),
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛒 Каталог ботів", callback_data="catalog")],
        [InlineKeyboardButton("📩 Задати питання", callback_data="question")]
    ]
    await update.message.reply_text(
        "Вітаю 👋\n\nЯ — магазин Telegram-ботів.\nОберіть дію 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for key, (name, price) in PRODUCTS.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{name} — {price}$",
                callback_data=f"buy_{key}"
            )
        ])
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back")])

    await update.callback_query.message.reply_text(
        "🛒 Наші продукти:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "catalog":
        await catalog(update, context)

    elif query.data.startswith("buy_"):
        key = query.data.replace("buy_", "")
        name, price = PRODUCTS[key]

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": name},
                    "unit_amount": price * 100,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="https://t.me/your_bot",
            cancel_url="https://t.me/your_bot",
        )

        await query.message.reply_text(
            f"💳 Оплата за **{name}**\n\n"
            f"Сума: {price}$\n\n"
            f"👉 {session.url}"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🧾 Клієнт відкрив оплату: {name} ({price}$)"
        )

    elif query.data == "question":
        await query.message.reply_text(
            "✍️ Напишіть ваше питання або запит:"
        )

    elif query.data == "back":
        await start(query, context)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.run_polling()
