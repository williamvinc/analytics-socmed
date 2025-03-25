import google.generativeai as genai
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from vanna.chromadb import ChromaDB_VectorStore
from vanna.google import GoogleGeminiChat
from dotenv import load_dotenv
from prompts.cpcm_prompts import system_prompts
import os
load_dotenv()

TOKEN: Final = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash"
BOT_USERNAME: Final = '@cpcm_insights_bot'

config = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "dbname": os.getenv("MYSQL_DATABASE"),
    "port": 3306
}

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=system_prompts)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hallo! Saya adalah CPCM bot yang dibuat khusus untuk pertanyaan seputar Social Media CPCM Indonesia. Silakan bertanya kepada saya!')
    
def handle_response(text: str):
    processed: str = text.lower()
    try:
        response = model.generate_content(processed)
        return(response.text)
    except Exception as e:
        return(f"Error: {e}")

async def handle_message(update: Update, context: ContextTypes. DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
        
        print('Bot:', response)
        await update.message.reply_text(response)
        
async def error(update: Update, context: ContextTypes. DEFAULT_TYPE): 
    print(f'Update {update} error {context.error}')






if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)
    
    print('Polling...')
    app.run_polling(poll_interval=3)