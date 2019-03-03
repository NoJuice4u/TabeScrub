import argparse
import requests
import json
import time
import re

from logger import logger as Logger

TAG_SEARCH = "div"

# Can I use function pointers here?
TAG_MAP = {
    "class=\"js-bookmark\"": "1",
    "class=\"js-bookmark\"": "2"}

mealTimes = {"lunch", "dinner"}

SEGMENT_MAP = []

# Go through every byte in the file.  This is to extract the braces to isolate each item
# Creates a dictionary to allow traversal.  Ignore items in blackList due to difficulty of parsing.
def process(configString, restaurant_tree, list, page):
    nodeDictionary = {}
    pos = 0
    commandStartPos = 0
    commandEndPos = 0
    braceCount = 0
    
    indexPos = 0
    positionMap = []
    i = 0

    restaurant_name = None
    reviewer_name = None
    restaurant_rating = None
    treeItem = {}
    limit = 0    

    # Reviewer Scanner
    ratingPos = configString.find("rvwr-nickname fs16")
    ratingPos = configString.find(">", ratingPos) + 1
    ratingEnd = configString.find("<", ratingPos)
    reviewer_name = configString[ratingPos:ratingEnd].strip()

    while(True):
        indexPos = configString.find(TAG_SEARCH, pos)
        if(indexPos == -1):
            break
        pos = indexPos + 2
        
        if(configString[indexPos-1] == "<"):
            braceCount += 1

            tagPosition = configString.find("class=\"js-bookmark\"", indexPos, indexPos+127)
            if(tagPosition > 0):
                braceCount = 0
                positionMap.append({"start": tagPosition - 5, "end": -1})
                pos = tagPosition + 2

        elif(configString[indexPos+len(TAG_SEARCH)] == ">"):
            limit += 1
            braceCount -= 1
            if(braceCount == 1 and len(positionMap) > 0):
                positionMap[len(positionMap)-1]["end"] = indexPos + 4
            endPos = indexPos + len(TAG_SEARCH) + 1

    i = 0
    for item in positionMap:
        segment = configString[item["start"]:item["end"]]
        SEGMENT_MAP.append(segment)
        ratingPos = segment.find("data-interested-review-id")
        ratingPos = segment.find("=\"", ratingPos) + 2
        ratingEnd = segment.find("\"", ratingPos)
        review_id = segment[ratingPos:ratingEnd]
        treeItem = {}
        treeItem["review_id"] = review_id

        tagPosition = segment.find("class=\"js-bookmark\"")
        if(tagPosition < 10 and tagPosition > 0):
            i += 1
            restaurant_rating = None
            ratingPos = segment.find("rvw-item__rst-name")

            linkStart = segment.find("href=", ratingPos) + 6
            linkEnd = segment.find("\"", linkStart)
            restaurant_url = segment[linkStart:linkEnd]

            ratingPos = segment.find(">", ratingPos) + 1
            ratingEnd = segment.find("<", ratingPos)
            restaurant_name = segment[ratingPos:ratingEnd]

            restaurant_tree[restaurant_name] = {}
            restaurant_tree[restaurant_name][reviewer_name] = {}
            restaurant_tree[restaurant_name][reviewer_name] = treeItem
            treeItem["url"] = restaurant_url

            # Category Scanner
            tagPosition = segment.find("class=\"rvw-item__rst-name\"")
            ratingPos = segment.find("rvw-item__rst-area-catg")
            ratingPos = segment.find(">", ratingPos) + 1
            ratingEnd = segment.find("<", ratingPos)

            categories = segment[ratingPos:ratingEnd].replace("（", "").replace("）", "").strip().split("、")
            treeItem["categories"] = categories

            # Lunch Scanner
            for mealTime in mealTimes:
                tagPosition = segment.find("class=\"c-rating__time c-rating__time--" + mealTime + "\"")
                if(tagPosition > 0):

                    if(mealTime not in treeItem):
                        treeItem[mealTime] = {}

                    # tagPosition = segment.find("class=\"js-bookmark\"", tagPosition)
                    ratingPos = segment.find("c-rating__val", tagPosition)
                    ratingPos = segment.find(">", ratingPos) + 1
                    ratingEnd = segment.find("<", ratingPos)
                    restaurant_rating = segment[ratingPos:ratingEnd]

                    try:
                        treeItem[mealTime]["overall"] = float(restaurant_rating)
                    except:
                        treeItem[mealTime]["overall"] = -1

                    xRatingPos = tagPosition
                    while(True):
                        xRatingPos = segment.find("rvw-item__ratings-dtlscore-line", xRatingPos)
                        if(xRatingPos == -1):
                            break
                        xRatingPos = segment.find(">", xRatingPos) + 1
                        xRatingEnd = segment.find("<", xRatingPos)
                    
                        ratingNameStart = xRatingEnd + 7
                        ratingNameEnd = segment.find("<", ratingNameStart)
                        ratingName = segment[ratingNameStart:ratingNameEnd].strip()
                    
                        ratingPos = segment.find("rvw-item__ratings-dtlscore-score", ratingNameStart)
                        ratingPos = segment.find(">", ratingPos) + 1
                        ratingEnd = segment.find("<", ratingPos)
                        restaurant_subrating = segment[ratingPos:ratingEnd]

                        if(restaurant_rating is not None):
                            try:
                                list.append(str(((page * 20) + i) * 0.02) + " " + segment[ratingPos:ratingEnd] + " 0 0.5 0.5 0 1 255 " + str(int(float(segment[ratingPos:ratingEnd]) * 51)) + " 0 ")
                                treeItem[mealTime]["rating_" + ratingName] = float(segment[ratingPos:ratingEnd])
                            except:
                                pass

                # Price Scanner
                tagPosition = segment.find("c-rating__time c-rating__time--" + mealTime + " rvw-item__usedprice-time")
                ratingPos = segment.find("c-rating__val rvw-item__usedprice-price", tagPosition)
                ratingPos = segment.find(">", ratingPos) + 1
                ratingEnd = segment.find("<", ratingPos)
                restaurant_price = segment[ratingPos:ratingEnd]
                price = restaurant_price.replace("￥", "").replace(",", "").split("～")
                try:
                    treeItem[mealTime]["price_min"] = int(price[0])
                    try:
                        treeItem[mealTime]["price_max"] = int(price[1])
                    except:
                        treeItem[mealTime]["price_max"] = int(price[0])
                except:
                    pass

            # Date Scanner
            tagPosition = segment.find("class=\"rvw-item__date rvw-item__date--rvwlst\"")
            ratingPos = segment.find("rvw-item__visited-date")
            ratingPos = segment.find(">", ratingPos) + 1
            ratingEnd = segment.find("<", ratingPos)
            visit_date = segment[ratingPos:ratingEnd].replace("訪問", "")
            treeItem["visit_date"] = visit_date

            # Date Scanner - rvw-item__visited-date
            
    return i

def parseReviewer(file, user):
    restaurant_tree = {}

    page = 1
    list = ["0 0 0 0.5 0.5 0 1 0 0 0 ", "0 1 0 0.5 0.5 0 1 0 0 0 ", "0 2 0 0.5 0.5 0 1 0 0 0 ", "0 3 0 0.5 0.5 0 1 0 0 0 ", "0 4 0 0.5 0.5 0 1 0 0 0 ", "0 5 0 0.5 0.5 0 1 0 0 0 "]
    while(True):
        r = requests.get("https://tabelog.com/rvwr/" + user + "/reviewed_restaurants/list/?bookmark_type=1&sk=&sw=&Srt=D&SrtT=mfav&review_content_exist=0&PG=" + str(page))
        contents = r.text
    
        #file = open(file, 'r', encoding='utf-8')
        #fileContents = file.read()
        result = process(contents, restaurant_tree, list, page)
        page += 1
        Logger.log("ParseReviewer", "Page [" + str(page) + "].  Results Found: [" + str(result) + "]")

        if(result < 20):
            break

    writeFile = open("data\\" + user + ".json", 'w', encoding="utf-8")
    writeFile.write(json.dumps(restaurant_tree, indent=4, separators=(',', ': '), ensure_ascii=False))
    writeFile.close()
    return result

def extract(currentDiv,  classIdentifier, element):
    tagPosition = currentDiv.find(classIdentifier)
    if(tagPosition < 10 and tagPosition > 0):
        ratingPos = currentDiv.find(element)
        ratingPos = currentDiv.find(">", ratingPos) + 1
        ratingEnd = currentDiv.find("<", ratingPos)
        return currentDiv[ratingPos:ratingEnd]

    return None