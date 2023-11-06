from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.ext import Updater
from telegram import Bot
from telegram import ChatMemberUpdated





with open('token_telegram.txt', 'r') as f:
    TOKEN = f.read().strip()

BOT_USERNAME = '@barca_reminder_bot'
print("Starting bot...")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello!, if you add me to a group, I will remind you of the next Barça match.')
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Help!')

# Responses

def handle_response(text:str)-> str:
    lower_text = text.lower()
    if "hi" in lower_text or "hello" in lower_text:
        return "Hello!"
    else:
        return "I don't understand you!"
   
   
# a funciton to send a message to a chat on 11:00 pm every day
async def send_message(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id='@barca_reminder', text='Hello!')
    print('Message sent')
    
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text
    print(f'User {update.message.from_user.username} sent a message: {text}')
    
    if message_type == "group" or message_type == "supergroup":
        await update.message.reply_text(handle_response(text))
        if BOT_USERNAME in text:
            await update.message.reply_text("You mentioned me!")
            new_text = text.replace(BOT_USERNAME, "").strip()
            response = handle_response(new_text)
            await update.message.reply_text(response)
        else:
            return
    else:
        await update.message.reply_text(handle_response(text))
    
    print(f'Bot said: {handle_response(text)}')
    
    
async def handle_new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.my_chat_member.new_chat_members:
        if member.user.username == BOT_USERNAME:
            await context.bot.send_message(chat_id=update.my_chat_member.chat.id, text='Hello! Baby Dolls, Imma call the next Game!')


  
    
    
    
    
    
    
    
    
    
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')
    




if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    ## commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    # In your main function
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_chat_members))
    ## messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    ## errors
    app.add_error_handler(error)
    
    # polling
    print("Polling...")
    app.run_polling(poll_interval=5)
    

            