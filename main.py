from telebot import TeleBot,types
from telebot.types import InlineKeyboardButton,InlineKeyboardMarkup
from googletrans import Translator
from collections import deque
import requests
import ssl


# ตั้งค่า Telegram Bot Token
Token = "6800120949:AAHeWsrkT38-SQHfoTLpkvEDk9KL-nDaY_8"
bot = TeleBot(Token)
translator = Translator()

# ประวัติการค้นหา (เก็บล่าสุด 10 รายการ)
search_history = deque(maxlen=10)


# แก้ไขปัญหา SSL
try:
    requests.packages.urllib3.disable_warnings()
    ssl._create_default_https_context = ssl.create_unverified_context
except AttributeError:
    pass


# ฟังก์ชันแปลข้อความเป็นภาษาอังกฤษ
def translate_to_english(text):
    translated = translator.translate(text,src="auto",dest='en')
    return translated.text


# ฟังก์ชันค้นหาคำถามใน Stack Overflow
def search_stackoverflow(query):
    url = "https://api.stackexchange.com/2.3/search/advanced"
    params =  {
        "order":"desc",
        "sort":"relevance",
        "q":query,
        "site":"stackoverflow",
        "accepted":True,
        "pageSize":4
    }
    try:
        response = requests.get(url,params=params ,verify=False)
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            results =["🔎ผลการค้นหา"]
            keyboard = types.InlineKeyboardMarkup()
            
            for question in data["items"]:
                title = question["title"]
                link = question["link"]
                
               
                results.append(f"📌 *{title}*")
                keyboard.add(types.InlineKeyboardButton("🔗 เปิดดูคำถาม", url=link))

            return "\n\n".join(results), keyboard
        else:
            return "❌ ไม่พบคำถามที่เกี่ยวข้อง 😢", None
          
    except requests.exceptions.RequestException as e:
        return f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {str(e)}",None
    

@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    bot.send_message(message.chat.id,"👋 สวัสดี! ส่งข้อความเพื่อค้นหาคำถามจาก Stack Overflow หรือใช้คำสั่ง /top เพื่อดูคำถามยอดนิยม")


@bot.message_handler(commands=['top'])
def get_top_questions(message):
    url = "https://api.stackexchange.com/2.3/questions"
    params = {
        "order": "desc",
        "sort": "votes",
        "site": "stackoverflow",
        "pagesize": 4  
    }
    try:
        response = requests.get(url, params=params, verify=False)
        data = response.json()

        if "items" in data and len(data["items"]) > 0:
            results = ["🔥คำถามยอดนิยมวันนี้"]
            keyboard = types.InlineKeyboardMarkup()
            for question in data["items"]:
                title = question["title"]
                link = question["link"]
                
                results.append(f"📌 *{title}*")
                keyboard.add(types.InlineKeyboardButton("🔗 เปิดดูคำถาม", url=link))
                
            bot.send_message(
                message.chat.id, "\n\n".join(results), reply_markup=keyboard
            )
        else:
            bot.send_message(message.chat.id, "ไม่พบคำถามยอดนิยมในขณะนี้ 😢")
    except requests.exceptions.RequestException as e:
        bot.send_message(message.chat.id, f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {str(e)}")
            
                            

@bot.message_handler(func=lambda message:True)
def search_question(message):
    query = message.text
    translator_query = translate_to_english(query)
    search_history.append(query)
    
    bot.reply_to(message,"🔎 _กรุณารอสักครู่..._")
    result,keybord = search_stackoverflow(translator_query)
    
    if keybord:
        bot.send_message(message.chat.id,result,reply_markup=keybord)
    else:    
        bot.send_message(message.chat.id,result)


        
if __name__ == "__main__":
    print("Bot is running....")
    bot.polling()