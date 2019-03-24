import requests

from logger import logger as Logger

## TODO: restaurant status:: rst-status-badge-large rst-st-closed
TAG_SEARCH = "div"

def parseRestaurantFile(file):
    file = open(file, 'r', encoding='utf-8')
    content = file.read()
    
    return findCoords(content)

def parseRestaurantURL(url):
    Logger.log("parseRestaurantURL", url)
    r = requests.get(url)
    content = r.text

    return findCoords(content)
    
def parseRestaurantComments(url):
    Logger.log("parseRestaurantComments", url)
    r = requests.get(url)
    content = r.text

    return findReviewers(content)
    
def findCoords(content):
    result = {}
    if(content.find("rst-st-closed") > 0):
        Logger.log("CLOSED", ".")
        result['status'] = "closed"
        
    coordsStart = content.find("center=") + 7
    coordsEnd = content.find("&amp;", coordsStart)

    coords = content[coordsStart:coordsEnd].split(",")
    try:
        result['coords'] = {"longitude": float(coords[0]), "latitude": float(coords[1])}
    except:
        result['coords'] = {"longitude": 0.0, "latitude": 0.0}
        
    costStart = content.find("class=\"rdheader-budget__price-target\"") + 38
    costEnd = content.find("<", costStart)
    result['cost'] = {}
    result['cost']['lunch'] = content[costStart:costEnd]
    
    costStart = content.find("class=\"rdheader-budget__price-target\"", costEnd) + 38
    costEnd = content.find("<", costStart)
    result['cost']['dinner'] = content[costStart:costEnd]
    
    return result
    
    # resultTable = parseDivs(contents)
def findReviewers(content):
    resultTable = extractDivs(content, "class=\"rvw-item js-rvw-item-clickable-area\"")
    reviewerTable = {}
    
    for pos in resultTable:
        elementDiv = content[pos['start']:pos['end']]
        rvwrPos_Start = elementDiv.find("href=\"/rvwr") + 12
        rvwrPos_End = elementDiv.find("\"", rvwrPos_Start) - 1
        
        Logger.log("ReviewerPos", str(rvwrPos_Start) + ":" + str(rvwrPos_End))
        reviewer = elementDiv[rvwrPos_Start:rvwrPos_End]
        
        ratingPos_Start = elementDiv.find("c-rating__val c-rating__val--strong")
        ratingPos_Start = elementDiv.find(">", ratingPos_Start) + 1
        ratingPos_End = elementDiv.find("<", ratingPos_Start)
        
        rating = elementDiv[ratingPos_Start:ratingPos_End]
        
        reviewerTable[reviewer] = rating

    return reviewerTable

def extractDivs(contents, search):
    pos = 0
    indexPos = 0
    braceCount = 0
    positionMap = []

    while(True):
        indexPos = contents.find(TAG_SEARCH, pos)
        if(indexPos == -1):
            break
        pos = indexPos + 2
        
        if(contents[indexPos-1] == "<"):
            braceCount += 1

            tagPosition = contents.find(search, indexPos, indexPos+127)
            if(tagPosition > 0):
                braceCount = 0
                positionMap.append({"start": tagPosition - 5, "end": -1})
                pos = tagPosition + 2

        elif(contents[indexPos+len(TAG_SEARCH)] == ">"):
            braceCount -= 1
            if(braceCount == 1 and len(positionMap) > 0):
                positionMap[len(positionMap)-1]["end"] = indexPos + 4
            endPos = indexPos + len(TAG_SEARCH) + 1

    return positionMap

if __name__ == "__main__":
    result = parseRestaurantFile("data/restaurant.html")
    # result = parseRestaurantURL("https://tabelog.com/tokyo/A1314/A131401/13094789/")
    print(result)