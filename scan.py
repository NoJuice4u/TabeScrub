import argparse
import requests
import json
import time
import re

TAG_SEARCH = "div"

# Can I use function pointers here?
TAG_MAP = {
    "class=\"js-bookmark\"": "1",
    "class=\"js-bookmark\"": "2"}

parser = argparse.ArgumentParser(description='Tabelog User Review Scanner')
parser.add_argument('--user', required=True)

args = parser.parse_args()
                    
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
    

    # START WRAPPER: class="timeline js-timeline-content-wrap"

    # 1. Find DIV
    # 2. Find the associated tag from Map
    limit = 0
    while(True):
        indexPos = configString.find(TAG_SEARCH, pos)
        if(indexPos == -1):
            break
        pos = indexPos + 2
        
        if(configString[indexPos-1] == "<"):
            braceCount += 1
            positionMap.append(indexPos)
        elif(configString[indexPos+len(TAG_SEARCH)] == ">"):
            limit += 1
            braceCount -= 1
            startPos = positionMap.pop() - 1
            endPos = indexPos + len(TAG_SEARCH) + 1
            
            currentDiv = configString[startPos:endPos]

            # Reviewer Scanner
            tagPosition = currentDiv.find("class=\"header-contents__info header-contents__info--s\"")
            if(tagPosition > 0):
                ratingPos = currentDiv.find("rvwr-nickname fs16")
                ratingPos = currentDiv.find(">", ratingPos) + 1
                ratingEnd = currentDiv.find("<", ratingPos)
                reviewer_name = currentDiv[ratingPos:ratingEnd].strip()

            # Name Scanner
            tagPosition = currentDiv.find("class=\"js-bookmark\"")
            if(tagPosition < 10 and tagPosition > 0):
                i += 1
                restaurant_rating = None
                
                if(restaurant_name is not None):
                    restaurant_tree[restaurant_name] = {}
                    restaurant_tree[restaurant_name][reviewer_name] = {}
                    restaurant_tree[restaurant_name][reviewer_name] = treeItem
                    treeItem = {}

                ratingPos = currentDiv.find("rvw-item__rst-name")
                ratingPos = currentDiv.find(">", ratingPos) + 1
                ratingEnd = currentDiv.find("<", ratingPos)
                restaurant_name = currentDiv[ratingPos:ratingEnd]

            if(restaurant_name is not None and reviewer_name is not None):
                # Time Scanner
                tagPosition = currentDiv.find("class=\"c-rating__time c-rating__time--lunch\"")
                if(tagPosition > 0):
                    treeItem["review_time"] = "lunch"
                else:
                    treeItem["review_time"] = "dinner"
                
                # Rating Scanner
                tagPosition = currentDiv.find("class=\"js-bookmark\"")
                if(tagPosition < 10 and tagPosition > 0):
                    ratingPos = currentDiv.find("c-rating__val")
                    ratingPos = currentDiv.find(">", ratingPos) + 1
                    ratingEnd = currentDiv.find("<", ratingPos)
                    restaurant_rating = currentDiv[ratingPos:ratingEnd]
                    try:
                        treeItem["overall"] = float(restaurant_rating)
                    except:
                        treeItem["overall"] = -1

                # Price Scanner
                tagPosition = currentDiv.find("class=\"js-bookmark\"")
                if(tagPosition < 10 and tagPosition > 0):
                    ratingPos = currentDiv.find("c-rating__val rvw-item__usedprice-price")
                    ratingPos = currentDiv.find(">", ratingPos) + 1
                    ratingEnd = currentDiv.find("<", ratingPos)
                    restaurant_price = currentDiv[ratingPos:ratingEnd]
                    price = restaurant_price.replace("￥", "").replace(",", "").split("～")
                    try:
                        treeItem["price_min"] = int(price[0])
                        try:
                            treeItem["price_max"] = int(price[1])
                        except:
                            treeItem["price_max"] = int(price[0])
                    except:
                        pass

                # Date Scanner - rvw-item__visited-date

                # Rating Scanner
                tagPosition = currentDiv.find("class=\"js-bookmark\"")
                if(tagPosition < 10 and tagPosition > 0):
                    xRatingPos = 0
                    while(True):
                        xRatingPos = currentDiv.find("rvw-item__ratings-dtlscore-line", xRatingPos)
                        if(xRatingPos == -1):
                            break
                        xRatingPos = currentDiv.find(">", xRatingPos) + 1
                        xRatingEnd = currentDiv.find("<", xRatingPos)
                    
                        ratingNameStart = xRatingEnd + 7
                        ratingNameEnd = currentDiv.find("<", ratingNameStart)
                        ratingName = currentDiv[ratingNameStart:ratingNameEnd].strip()
                    
                        ratingPos = currentDiv.find("rvw-item__ratings-dtlscore-score", ratingNameStart)
                        ratingPos = currentDiv.find(">", ratingPos) + 1
                        ratingEnd = currentDiv.find("<", ratingPos)
                        restaurant_subrating = currentDiv[ratingPos:ratingEnd]

                        if(restaurant_rating is not None):
                            try:
                                list.append(str(((page * 20) + i) * 0.02) + " " + currentDiv[ratingPos:ratingEnd] + " 0 0.5 0.5 0 1 255 " + str(int(float(currentDiv[ratingPos:ratingEnd]) * 51)) + " 0 ")
                                treeItem["rating_" + ratingName] = float(currentDiv[ratingPos:ratingEnd])
                            except:
                                pass
            
            pos = endPos
        pos += 1
    return i

def parse(file, args):
    restaurant_tree = {}

    page = 1
    list = ["0 0 0 0.5 0.5 0 1 0 0 0 ", "0 1 0 0.5 0.5 0 1 0 0 0 ", "0 2 0 0.5 0.5 0 1 0 0 0 ", "0 3 0 0.5 0.5 0 1 0 0 0 ", "0 4 0 0.5 0.5 0 1 0 0 0 ", "0 5 0 0.5 0.5 0 1 0 0 0 "]
    while(True):
        r = requests.get("https://tabelog.com/rvwr/" + args.user + "/reviewed_restaurants/list/?bookmark_type=1&sk=&sw=&Srt=D&SrtT=mfav&review_content_exist=0&PG=" + str(page))
        contents = r.text
        
        #file = open(file, 'r', encoding='utf-8')
        #fileContents = file.read()
        result = process(contents, restaurant_tree, list, page)
        page += 1
        print("Page [" + str(page) + "].  Results Found: [" + str(result) + "]")

        if(result < 20):
            break

    writeFile = open("data\\" + args.user + ".json", 'w', encoding="utf-8")
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

dict = parse("tabelog.html", args)