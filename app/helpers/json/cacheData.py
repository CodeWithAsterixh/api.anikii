from app.helpers.json.jsonParser import jsonLoad,jsonSave
from app.helpers.json.pageLocator import ensure_page_exists
from app.structure.listItem import structureAnilistArray
from app.database.addFile import findFileByName, updateInDb

def runCacheData(page: int|None, filePath: str):
    """
    Run the cache data
    """
    
    
    loadData = jsonLoad(filePath)
    if not page:
        return loadData
    if loadData and ensure_page_exists(loadData, page) and page:
            print("serving from cache")
            lastPage = loadData["lastPage"]
            pageInfo = {
                "lastPage": lastPage,
                "currentPage": page
            }
            data = loadData["pages"][str(page)]
            return {
                "pageInfo": pageInfo,
                "data": data
            }, 200


    else:
        print("serving from API")
        
def saveCacheData(pageInfo:dict, media:list, filePath: str, page:int):
    """
    Save the cache data
    data should be an object that has the media and pageInfo keys
    """
    structuredData = structureAnilistArray(media)
    
    lastPage = min(pageInfo["lastPage"], 50)
    pageInfo = {
        "lastPage": lastPage,
        "currentPage": page
    }
    findDb = findFileByName(f"{filePath}.json")
    if(findDb):
        updateInDb(f"{filePath}.json", {"$set": { f"data.pages.{page}": structuredData }})
        print("up-db")
    
    jsonSave(filePath,page,{"lastPage":lastPage,"data":structuredData})
    return{
        "pageInfo":pageInfo,
        "data":structuredData
    }
    
    