from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
# Load environment variables from .env

def get_database():
    load_dotenv()
    # Fetching the connection string from .env
    envar = os.getenv("MongoUri") 
    
    # Connect to MongoDB Atlas (pass the URI directly)
    client = MongoClient(envar)        
    # Return the selected database
    return client.get_database("anikii")
    
    

