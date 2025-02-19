from .collection import collection_name
from app.helpers.json.jsonFormatRaw import generate_metadata


def addToDb(fileName:str, data:dict|list):
    

    collection_name.insert_one({
            "name": fileName,
            "data":data
        })


def updateInDb(fileName:str, data:dict|list):
    collection_name.update_one({
        "name": fileName,
    }, data,upsert=True)


def findFileByName(name:str):
    return collection_name.find_one({"name": name})


    