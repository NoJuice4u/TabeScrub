import requests

TAG_SEARCH = "div"

def parseRestaurantFile(file):
    file = open(file, 'r', encoding='utf-8')
    content = file.read()
    
    return findCoords(content)

def parseRestaurantURL(url):
    print("PROCESSING: " + url)
    r = requests.get(url)
    content = r.text

    return findCoords(content)

def findCoords(content):
    coordsStart = content.find("center=") + 7
    coordsEnd = content.find("&amp;", coordsStart)

    coords = content[coordsStart:coordsEnd].split(",")
    return {"longitude": coords[0], "latitude": coords[1]}

    # resultTable = parseDivs(contents)

def parseDivs(contents):
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

            tagPosition = contents.find("class=\"rstinfo-table\"", indexPos, indexPos+127)
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