import telebot
import config
from datetime import datetime

bot = telebot.TeleBot(config.BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 <b>Welcome to the Feedback Bot!</b>\n\n"
        "To submit feedback, please do one of the following:\n"
        "1️⃣ Send a <b>picture/photo</b> with the caption starting with <code>/feedback</code>\n"
        "2️⃣ Reply to an existing photo with <code>/feedback</code>\n\n"
        "I will then share it directly to our feedback channel.\n\n"
        "<i>Note: Only photos are accepted!</i>"
    )
    bot.reply_to(message, welcome_text, parse_mode='HTML')

@bot.message_handler(func=lambda msg: (msg.content_type == 'text' and msg.text and msg.text.startswith('/feedback')) or (msg.content_type == 'photo' and msg.caption and msg.caption.startswith('/feedback')), content_types=['photo', 'text'])
def handle_feedback(message):
    feedback_text = ""
    photo_file_id = None
    
    # Check if it's a photo with caption starting with /feedback
    if message.content_type == 'photo':
        feedback_text = message.caption[len('/feedback'):].strip()
        photo_file_id = message.photo[-1].file_id
            
    # Check if it's a text message starting with /feedback
    elif message.content_type == 'text':
        if message.reply_to_message and message.reply_to_message.content_type == 'photo':
            feedback_text = message.text[len('/feedback'):].strip()
            photo_file_id = message.reply_to_message.photo[-1].file_id
        else:
            bot.reply_to(message, "⚠️ Please use /feedback as a caption when sending a photo, or reply to a photo with /feedback.")
            return

    if photo_file_id:
        try:
            # User details
            user_identifier = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
            
            # Date & Time
            current_time = datetime.now().strftime("%d %b %Y, %I:%M %p")
            
            # Format the beautiful caption
            caption = "✨ <b>FEEDBACK RECEIVED</b> ✨\n\n"
            caption += f"👤 <b>Shared By:</b> {user_identifier}\n"
            
            if feedback_text:
                caption += f"📝 <b>User Caption:</b> {feedback_text}\n"
                
            caption += f"🕒 <b>Date & Time:</b> {current_time}\n\n"
            caption += "━━━━━━━━━━━━━━━━━━━━━\n"
            caption += "🔥 <b>Legacy isnt here only for win , Its here for dominance</b> 👑"
            
            # Send photo to the channel with HTML parse mode
            bot.send_photo(
                chat_id=config.CHANNEL_ID, 
                photo=photo_file_id, 
                caption=caption,
                parse_mode='HTML'
            )
            
            # Confirm to the user
            bot.reply_to(message, "✅ The feedback is shared to the channel, thank you for your feedback")
        except Exception as e:
            bot.reply_to(message, "❌ Sorry, there was an error sending your picture. Please ensure the bot is an admin in the channel.")
            print(f"Error: {e}")

if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()
