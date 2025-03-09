from pyrogram import Client, filters
from pymongo import MongoClient
import random, string

# MongoDB Connection
mongo_client = MongoClient("your_mongodb_url")
db = mongo_client["your_database_name"]
redeem_codes_collection = db["redeem_codes"]
users_collection = db["users"]

# Function to generate a random redeem code
def generate_redeem_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

# Command to create a new redeem code
@Client.on_message(filters.command("generate_code") & filters.user("your_admin_user_id"))
def generate_code(client, message):
    code = generate_redeem_code()
    redeem_codes_collection.insert_one({"code": code, "used": False})
    message.reply_text(f"✅ नया रिडीम कोड: `{code}`")

# Command to redeem a code
@Client.on_message(filters.command("redeem"))
def redeem(client, message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        return message.reply_text("❌ कृपया सही फॉर्मेट में कोड डालें: `/redeem CODE123`")
    
    code = args[1].strip().upper()
    code_data = redeem_codes_collection.find_one({"code": code, "used": False})
    
    if not code_data:
        return message.reply_text("❌ यह रिडीम कोड अमान्य या पहले ही उपयोग किया जा चुका है!")
    
    # Mark code as used and add benefits to the user
    redeem_codes_collection.update_one({"code": code}, {"$set": {"used": True}})
    users_collection.update_one({"user_id": user_id}, {"$set": {"premium": True}}, upsert=True)
    message.reply_text("✅ कोड सफलतापूर्वक रिडीम हो गया! अब आप प्रीमियम उपयोगकर्ता हैं।")
