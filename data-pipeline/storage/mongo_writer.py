import os
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class MongoWriter:
    def __init__(self):
        # It reads the same .env file as your backend!
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.client = MongoClient(uri)
        self.db = self.client["ChatBotCse"] 
        
        self.announcements_collection = self.db["cse_akdeniz_announcements"]
        self.menu_collection = self.db["yemekhane_listesi"]

    def is_exists(self, link):
        return self.announcements_collection.find_one({"link": link}) is not None

    def save_announcements(self, data):
        document = {
            **data,
            "created_at": datetime.utcnow(),
            "scraped_at": datetime.utcnow()
        }
        self.announcements_collection.insert_one(document)
        print(f"✅ Announcement Saved: {data['title']}")

    def save_menu(self, menu_list: list):
        """Saves the list of daily menus."""
        if not menu_list: return
        
        for item in menu_list:
            # Update if date exists, Insert if new
            self.menu_collection.update_one(
                {"date": item["date"]}, 
                {"$set": item}, 
                upsert=True
            )
        print(f"✅ Saved {len(menu_list)} menu items.")