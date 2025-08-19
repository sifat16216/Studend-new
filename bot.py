import os
import telebot
import requests
from flask import Flask, request

# 🔑 Bot token Render Env থেকে পড়বে
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# 🔍 Student data fetch function
def get_student_details(username):
    login_url = "http://mcc.edu.bd/student/php/ui/login/login_with_password.php"
    data_url = "http://mcc.edu.bd/student/php/ui/admission/get_my_admissioninfo.php"

    session = requests.Session()
    login_data = {"username": username, "password": f"MCC{username}"}
    session.post(login_url, data=login_data)
    data_response = session.post(data_url)
    if data_response.status_code == 200:
        return data_response.json()
    return None

# 🎯 Start Command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 স্বাগতম! আপনার Username পাঠান, আমি আপনার Student Details পাঠাব।")

# 🎯 Fetch Student Details
@bot.message_handler(func=lambda message: True)
def fetch_details(message):
    username = message.text.strip()
    student_data = get_student_details(username)

    if student_data and not student_data.get("error"):  
        details = student_data["data"][0]
        appliedfor = details["appliedfor"][0]
        preveducation = details["preveducation"][0]

        # 📩 Format Message
        reply_text = f"""
┌───⭓📌<b>Student Details</b>
├⪦🎴আইডি : <code>{appliedfor["stdid"]}</code>
├⪦👤 নাম (বাংলা): <code>{details["name_bn"]}</code>
├⪦📝 নাম (English): <code>{details["name_en"]}</code>
├⪦🛐 ধর্ম: {details["rtitle"]}
├⪦📱নাম্বার: <code>{details["contactno"]}</code>
├⪦💌ইমেইল: <code>{details["email"]}</code>
├⪦🪪জন্ম নিবন্ধন/NID: <code>{details["stdbirthnid"]}</code>
├⪦🎂 জন্ম তারিখ: <code>{details["dob"]}</code>
├⪦🩸 ব্লাড গ্রুপ: {details["bloodgroup"]}
├⪦👨‍👩‍👧 বাবা: <code>{details["fname_bn"]}</code>
├⪦📱বাবার নাম্বার: <code>{details["fcontactno"]}</code>
├⪦👩 মা: <code>{details["mname_bn"]}</code>
├⪦🗺️জাতীয়তা: {details["nationality"]}
├⪦🏠 ঠিকানা: <code>{details["par_vill"]}</code>
├⪦🏘️স্থায়ী ঠিকানা: <code>{details["parmanent_address"]}</code>
└────⧕

┌────⭓🎓 <b>বর্তমান প্রতিষ্ঠান</b>
├⪦🏫প্রতিষ্ঠান: Mahila College Chattogram
├⪦🎴আইডি নং: <code>{appliedfor["stdid"]}</code>
├⪦📜ক্লাস রোল: <code>{appliedfor["rollno"]}</code>
├⪦🧠বিভাগ: {appliedfor["courseleveltitle"]}
├⪦🗓️ভর্তি সাল: {appliedfor["academicyear"]}
├⪦👩🏻ছাত্রী নং: <code>{appliedfor["stdno"]}</code>
└────⧕

┌────⭓🏫 <b>পূর্ববর্তী প্রতিষ্ঠান</b>
├⪦🏫প্রতিষ্ঠান: <code>{preveducation["institutename"]}</code>
├⪦🗓️সেকশন: {preveducation["sessiontext"]}
├⪦🧾SSC Roll: <code>{preveducation["rollno"]}</code>
├⪦💳SSC Reg: <code>{preveducation["regno"]}</code>
├⪦🗾শিক্ষা বোর্ড: {preveducation["boardtitle"]}
├⪦⚖️রেজাল্ট: {preveducation["result"]}
├⪦🗓️পাশের বছর: {preveducation["passyear"]}
└────⧕
"""

        # 🖼 Send Photo + Message
        bot.send_photo(message.chat.id, details["photourl"], caption=reply_text, parse_mode="HTML")

    else:
        bot.reply_to(message, "❌ তথ্য পাওয়া যায়নি! সঠিক *Username* দিন।")

# ✅ Flask route (Webhook endpoint)
@app.route("/" + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_str = request.stream.read().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    return "Bot is running!", 200

# 🚀 Main
if __name__ == "__main__":
    # Render এর domain এ webhook সেট করতে হবে
    url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=url)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
