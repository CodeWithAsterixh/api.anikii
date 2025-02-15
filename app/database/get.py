from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os

# Load environment variables from .env

def get_database():
    # Fetching the connection string from .env    
    
    # Connect to MongoDB Atlas (pass the URI directly)
    client = MongoClient("mongodb+srv://quizeen:Asterixh@cluster0.8zxmg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")        
    # Return the selected database
    return client.get_database("anikii")
    
    

