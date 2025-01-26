from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.ext import Updater
from telegram import Bot
from telegram import ChatMemberUpdated
from footballapi import get_next_barca_match, does_barca_play_today, get_barca_today_match
from datetime import time
import os


with open('token_telegram.txt', 'r') as f:
    TOKEN = f.read().strip()

BOT_USERNAME = '@barca_reminder_bot'
print("Starting bot...")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello!, if you add me to a group, I will remind you of the next Barça match.')
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Help!')

# Responses
async def nextmatch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    match = get_next_barca_match('matches.json')
    await context.bot.send_message(chat_id=update.message.chat_id, text=f"The next Barca match is {match}")

        
async def todaymatch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if does_barca_play_today('matches.json'):
        match = get_barca_today_match('matches.json')
        message = await context.bot.send_message(chat_id=update.message.chat_id, text=f"{match}")
        await context.bot.pin_chat_message(chat_id=update.message.chat_id, message_id=message.message_id)
    else:
        await context.bot.send_message(chat_id=update.message.chat_id, text="Barca doesn't play today!")
    


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
        if BOT_USERNAME in text:
            await update.message.reply_text("You mentioned me!")
            new_text = text.replace(BOT_USERNAME, "").strip()
            response = handle_response(new_text)
            await update.message.reply_text(response)
        else:
            pass
    else:
        pass
        # await update.message.reply_text(handle_response(text))
    
    print(f'Bot said: {response}')
    


async def handle_new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.my_chat_member.new_chat_members:
        if member.user.username == BOT_USERNAME:
            group_id = update.my_chat_member.chat.id
            if group_id not in group_ids:
                group_ids.append(group_id)
            await context.bot.send_message(chat_id=group_id, text='Hello! Baby Dolls, Imma call the next Game!')

async def check_barca_match(context: ContextTypes.DEFAULT_TYPE):
    if does_barca_play_today():
        match = get_next_barca_match()
        # Send match information to each group
        for group_id in group_ids:
            await context.bot.send_message(chat_id=group_id, text=f'{match}')


def add_daily_job(updater: Updater):
    updater.job_queue.run_daily(check_barca_match, time(hour=14))



    
    
    
    
    
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')
    




if __name__ == "__main__":
    group_ids = []
    # load group ids
    # Check if groups.txt exists
    if not os.path.exists('groups.txt'):
        with open('groups.txt', 'w') as f:
            f.write('')
    
    with open('groups.txt', 'r') as f:
        for line in f:
            group_ids.append(line.strip())
    
    
    app = Application.builder().token(TOKEN).build()
    # updater = Updater(TOKEN)

    ## commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('nextmatch', nextmatch_command))
    app.add_handler(CommandHandler('todaymatch', todaymatch_command))
    # In your main function
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_chat_members))
    ## messages
    # app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    ## errors
    app.add_error_handler(error)
    
    # Add daily job
    # add_daily_job(updater)

    # polling
    print("Polling...")
    app.run_polling(poll_interval=10)


