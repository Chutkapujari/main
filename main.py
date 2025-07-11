import os
import openai
import logging
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

# ✅ Use environment variables (for Railway or locally)
TELEGRAM_TOKEN = os.getenv("7827676271:AAFiLpB31_vGo2KFNNTni2O_67sXeZ3k9wM")
OPENAI_API_KEY = os.getenv("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")

# Set OpenAI key
openai.api_key = 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

# Enable logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🟢 /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Welcome to Smart AI Bot!*\n\n"
        "Use /ask <your question>\n"
        "_Example:_ `/ask make a C file for hello world`",
        parse_mode="Markdown"
    )

# 🧠 Main /ask command
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗Usage: /ask <your question>")
        return

    question = " ".join(context.args)
    user = update.effective_user.first_name
    await update.message.reply_text("💭 Thinking... Please wait.")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant, respond clearly and in code if needed."},
                {"role": "user", "content": question}
            ],
            temperature=0.7
        )
        reply = response.choices[0].message.content.strip()

        # 🔍 Check if response includes code block
        if "```" in reply:
            lang = reply.split("```")[1].split("\n")[0].strip()
            code = reply.split("```")[1].split("\n", 1)[1].rsplit("```", 1)[0]

            filename = f"generated_code_{datetime.now().strftime('%H%M%S')}.{lang if lang else 'txt'}"
            filepath = f"/tmp/{filename}"

            with open(filepath, "w") as f:
                f.write(code)

            await update.message.reply_text("✅ Here's your code file:")
            await update.message.reply_document(InputFile(filepath, filename))
        else:
            await update.message.reply_text(reply[:4096])

    except Exception as e:
        logger.error(e)
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

# ⚠️ Error handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="❌ Exception occurred:", exc_info=context.error)

# 🚀 Run the bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ask", ask))
    app.add_error_handler(error_handler)

    print("✅ AI Bot is Running...")
    app.run_polling()

if __name__ == "__main__":
    main()