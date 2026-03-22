import telebot
import config

bot = telebot.TeleBot(config.BOT_TOKEN)

# Basic profanity filter list - add any words you want to block here
BAD_WORDS = ['badword1', 'badword2', 'abuse1', 'abuse2', 'fuck', 'shit', 'bitch', 'asshole']

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 <b>Welcome to the Feedback Bot!</b>\n\n"
        "To submit feedback, please do one of the following:\n"
        "1️⃣ Send a <b>picture or video</b> with the caption starting with <code>/feedback</code>\n"
        "2️⃣ Reply to an existing picture/video with <code>/feedback</code>\n\n"
        f"⚠️ <b>Note:</b> You must be a member of our main group to submit feedback.\n\n"
        "Your feedback will be directly posted to our channel.\n\n"
        "<i>Note: Only photos and videos are accepted!</i>"
    )
    bot.reply_to(message, welcome_text, parse_mode='HTML')

def contains_bad_words(text):
    if not text:
        return False
    text_lower = text.lower()
    for word in BAD_WORDS:
        if word in text_lower:
            return True
    return False

def check_membership(user_id):
    try:
        member = bot.get_chat_member(config.REQUIRED_GROUP_ID, user_id)
        if member.status in ['member', 'administrator', 'creator', 'restricted']:
            return True
        return False
    except Exception as e:
        print(f"Error checking membership for user {user_id}: {e}")
        return False

@bot.message_handler(func=lambda msg: (msg.content_type == 'text' and msg.text and msg.text.startswith('/feedback')) or (msg.content_type in ['photo', 'video'] and msg.caption and msg.caption.startswith('/feedback')), content_types=['photo', 'video', 'text'])
def handle_feedback(message):
    user_id = message.from_user.id
    
    # 0. Membership Check
    if not check_membership(user_id):
        error_msg = (
            "❌ <b>Access Denied</b>\n\n"
            "You are not allowed to submit feedback because you are not a member of the required group."
        )
        bot.reply_to(message, error_msg, parse_mode='HTML')
        return

    feedback_text = ""
    file_id = None
    media_type = None
    
    # Check if it's a photo or video with caption starting with /feedback
    if message.content_type in ['photo', 'video']:
        if not message.caption or not message.caption.startswith('/feedback'):
            return
        feedback_text = message.caption[len('/feedback'):].strip()
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            media_type = 'photo'
        else:
            file_id = message.video.file_id
            media_type = 'video'
            
    # Check if it's a text message starting with /feedback replying to media
    elif message.content_type == 'text':
        if message.reply_to_message and message.reply_to_message.content_type in ['photo', 'video']:
            feedback_text = message.text[len('/feedback'):].strip()
            if message.reply_to_message.content_type == 'photo':
                file_id = message.reply_to_message.photo[-1].file_id
                media_type = 'photo'
            else:
                file_id = message.reply_to_message.video.file_id
                media_type = 'video'
        else:
            bot.reply_to(message, "⚠️ Please use /feedback as a caption when sending a photo/video, or reply to a photo/video with /feedback.")
            return

    if file_id:
        # 1. Profanity Filter Check
        if contains_bad_words(feedback_text):
            bot.reply_to(message, "❌ Your feedback contains inappropriate language and was rejected.")
            return

        try:
            # Format the beautiful caption for the public channel
            channel_caption = "✨ FEEDBACK RECEIVED ✨ \n———————————————————\nFrom : LGC CLAN MEMBER ✅\n\n"
            if feedback_text:
                channel_caption += f"📝 <b>User Caption:</b> {feedback_text}\n"

            # Send media directly to the channel
            if media_type == 'photo':
                bot.send_photo(
                    chat_id=config.CHANNEL_ID, 
                    photo=file_id, 
                    caption=channel_caption,
                    parse_mode='HTML'
                )
            elif media_type == 'video':
                bot.send_video(
                    chat_id=config.CHANNEL_ID, 
                    video=file_id, 
                    caption=channel_caption,
                    parse_mode='HTML'
                )
            
            # Confirm to the user
            bot.reply_to(message, "✅ Your feedback has been posted to our channel.")
        except Exception as e:
            bot.reply_to(message, f"❌ Sorry, there was an error processing your feedback. Please ensure the bot is an admin in the channel.\nError: {e}")
            print(f"Error: {e}")

if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()