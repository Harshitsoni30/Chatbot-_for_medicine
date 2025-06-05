from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client.ChatBotValere
user_collection = db["User"]
session_id_collection = db["session_id"]
session_title_collection = db["session_chat"]
bot_prompt_collection = db["Bot_bot"]
