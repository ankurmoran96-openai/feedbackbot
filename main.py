import telebot
import config
from datetime import datetime

bot = telebot.TeleBot(config.BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 <b>Welcome to the Feedback Bot!</b>\n\n"
        "We'd love to see your feedback. Please send a <b>picture/photo</b> along with an optional caption, "
        "and I will share it directly to our feedback channel.\n\n"
        "<i>Note: Only photo submissions are accepted!</i>"
    )
    bot.reply_to(message, welcome_text, parse_mode='HTML')

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        # Get the highest resolution photo
        file_id = message.photo[-1].file_id 
        
        # User details
        user_identifier = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
        
        # Date & Time
        current_time = datetime.now().strftime("%d %b %Y, %I:%M %p")
        
        # Format the beautiful caption
        caption = "✨ <b>FEEDBACK RECEIVED</b> ✨\n\n"
        caption += f"👤 <b>Shared By:</b> {user_identifier}\n"
        
        if message.caption:
            caption += f"📝 <b>User Caption:</b> {message.caption}\n"
            
        caption += f"🕒 <b>Date & Time:</b> {current_time}\n\n"
        caption += "━━━━━━━━━━━━━━━━━━━━━\n"
        caption += "🔥 <b>Legacy isnt here only for win , Its here for dominance</b> 👑"
        
        # Send photo to the channel with HTML parse mode
        bot.send_photo(
            chat_id=config.CHANNEL_ID, 
            photo=file_id, 
            caption=caption,
            parse_mode='HTML'
        )
        
        # Confirm to the user
        bot.reply_to(message, "✅ The feedback is shared to the channel, thank you for your feedback")
    except Exception as e:
        bot.reply_to(message, "❌ Sorry, there was an error sending your picture. Please ensure the bot is an admin in the channel.")
        print(f"Error: {e}")

# Also handle cases where a user sends text instead of a photo
@bot.message_handler(content_types=['text'])
def handle_text(message):
    bot.reply_to(message, "⚠️ Please send a picture/photo for feedback. Text messages are not accepted.")

if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()