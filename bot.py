import os
import json
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")  # Render'da qo'yamiz

def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

QUESTIONS = load_questions()

user_data = {}

SUBJECTS = {
    "anatomiya": "🦴 Anatomiya",
    "tibbiy_kimyo": "🧪 Tibbiy kimyo",
    "falsafa": "📚 Falsafa",
    "nemis": "🇩🇪 Nemis tili",
    "rus": "🇷🇺 Rus tili",
    "gistologiya": "🔬 Gistologiya"
}

MAX_QUESTIONS = 10  # xohlasang 100 qilamiz

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! Quiz Test KUAF botiga xush kelibsiz!\n\n"
        "Fan tanlash uchun /menu bosing."
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for key, name in SUBJECTS.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"sub_{key}")])

    await update.message.reply_text(
        "📌 Fan tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Testni boshlash uchun /menu dan fan tanlang.")

async def choose_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    subject = query.data.replace("sub_", "")

    user_data[query.from_user.id] = {
        "subject": subject,
        "score": 0,
        "count": 0
    }

    await send_question(query)

def get_question(subject):
    qlist = QUESTIONS.get(subject, [])
    if not qlist:
        return None
    return random.choice(qlist)

async def send_question(query):
    uid = query.from_user.id
    subject = user_data[uid]["subject"]

    q = get_question(subject)
    if q is None:
        await query.message.reply_text("❌ Bu fandan savollar yo‘q. Admin savol qo‘shishi kerak.")
        return

    user_data[uid]["current"] = q

    keyboard = [
        [InlineKeyboardButton("A", callback_data="ans_A"),
         InlineKeyboardButton("B", callback_data="ans_B")],
        [InlineKeyboardButton("C", callback_data="ans_C"),
         InlineKeyboardButton("D", callback_data="ans_D")]
    ]

    text = (
        f"📚 Fan: {SUBJECTS[subject]}\n"
        f"📝 Savol #{user_data[uid]['count']+1}/{MAX_QUESTIONS}\n\n"
        f"{q['question']}\n\n"
        f"A) {q['A']}\n"
        f"B) {q['B']}\n"
        f"C) {q['C']}\n"
        f"D) {q['D']}"
    )

    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    if uid not in user_data:
        await query.message.reply_text("❗ Avval /menu dan fan tanlang.")
        return

    chosen = query.data.replace("ans_", "")
    q = user_data[uid]["current"]

    user_data[uid]["count"] += 1

    if chosen == q["correct"]:
        user_data[uid]["score"] += 1
        await query.message.reply_text("✅ To‘g‘ri!")
    else:
        await query.message.reply_text(f"❌ Noto‘g‘ri! To‘g‘ri javob: {q['correct']}")

    if user_data[uid]["count"] >= MAX_QUESTIONS:
        score = user_data[uid]["score"]
        await query.message.reply_text(
            f"🎉 Test tugadi!\n"
            f"Natija: {score}/{MAX_QUESTIONS}\n\n"
            f"Qayta boshlash uchun /menu bosing."
        )
        del user_data[uid]
    else:
        await send_question(query)

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_data:
        await update.message.reply_text("Hozir test boshlanmagan. /menu bosing.")
        return
    await update.message.reply_text(
        f"Ball: {user_data[uid]['score']} / {user_data[uid]['count']}"
    )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in user_data:
        del user_data[uid]
    await update.message.reply_text("🛑 Test to‘xtatildi. /menu bosing.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Buyruqlar:\n"
        "/start - botni ishga tushirish\n"
        "/menu - fan tanlash\n"
        "/score - natija\n"
        "/stop - testni to‘xtatish\n"
        "/help - yordam"
    )

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN topilmadi! Render'da Environment Variable qo'shing.")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("score", score))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("help", help_cmd))

    app.add_handler(CallbackQueryHandler(choose_subject, pattern="^sub_"))
    app.add_handler(CallbackQueryHandler(answer, pattern="^ans_"))

    app.run_polling()

if __name__ == "__main__":
    main()
