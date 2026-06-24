from dotenv import load_dotenv
import os
from mongoengine import connect

load_dotenv()

connect(
    db=os.getenv("MONGO_DB_CONTACTS"),
    host=os.getenv("MONGO_URI")
)

print("Connected")
