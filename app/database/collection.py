from .get import get_database

dbname = get_database()

collection_name = dbname.get_collection("listings")