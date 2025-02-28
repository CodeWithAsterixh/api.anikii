from .collection import collection_name


def DeleteDb(fileName:str):
    collection_name.find_one_and_delete({
            "name": fileName,
    })
    
    


    