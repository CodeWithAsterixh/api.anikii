from app.helpers.json.jsonParser import jsonLoad,jsonSave
from app.helpers.json.pageLocator import ensure_page_exists
from app.structure.listItem import structureAnilistArray


def runCacheData(page: int, filePath: str):
    """
    Run the cache data
    """
    loadData = jsonLoad(filePath)
    if loadData and ensure_page_exists(loadData, page):
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
    jsonSave(filePath,page,{"lastPage":lastPage,"data":structuredData})
    return{
        "pageInfo":pageInfo,
        "data":structuredData
    }
    
    