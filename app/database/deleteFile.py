from .collection import collection_name


def DeleteDb(fileName:str):
    

    collection_name.delete_one({
            "name": fileName,
        })
    
    


    