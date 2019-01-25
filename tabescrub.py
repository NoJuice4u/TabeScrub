from open3d import *
import json
import time
import re

TAG_SEARCH = "div"
#		self.reNodeName = re.compile('^(?P<nodeName>.*?)\<')
#		self.reDigits = re.compile('[0-9]+')
#		self.contentLength = re.compile('Content-Length:.(?P<contentLength>[0-9]+)')
#		self.valueList = self.reNodeName.match(self.currentResult)
#		self.reMatch = self.contentLength.search(self.dataStream)
#		self.maxSize = int(self.reMatch.group('contentLength')) + self.header + 4
                    
# Go through every byte in the file.  This is to extract the braces to isolate each item
# Creates a dictionary to allow traversal.  Ignore items in blackList due to difficulty of parsing.
def process(configString):
    nodeDictionary = {}
    pos = 0
    commandStartPos = 0
    commandEndPos = 0
    braceCount = 0
    
    indexPos = 0
    positionMap = []
    reviewMap = {}
    
    writeFile = open("output.txt", 'w')
    list = ["0 5 0 0.5 0.5 0 1 0 0 0 ", "0 0 0 0.5 0.5 0 1 0 0 0 "]
    restaurant_tree = {}
    i = 0
    
    while(indexPos >= 0):
        indexPos = configString.find(TAG_SEARCH, pos)
        restaurant_name = None
        restaurant_rating = None
        
        if(configString[indexPos-1] == "<"):
            braceCount += 1
            positionMap.append(indexPos)
        elif(configString[indexPos+len(TAG_SEARCH)] == ">"):
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
                ratingPos = currentDiv.find("rvw-item__rst-name")
                ratingPos = currentDiv.find(">", ratingPos) + 1
                ratingEnd = currentDiv.find("<", ratingPos)
                restaurant_name = currentDiv[ratingPos:ratingEnd]
                restaurant_tree[restaurant_name] = {}
                restaurant_tree[restaurant_name][reviewer_name] = {}
                
            # Rating Scanner
            tagPosition = currentDiv.find("class=\"js-bookmark\"")
            if(tagPosition < 10 and tagPosition > 0):
                ratingPos = currentDiv.find("c-rating__val")
                ratingPos = currentDiv.find(">", ratingPos) + 1
                ratingEnd = currentDiv.find("<", ratingPos)
                restaurant_rating = currentDiv[ratingPos:ratingEnd]
                restaurant_tree[restaurant_name][reviewer_name]["overall"] = float(restaurant_rating)

            # Price Scanner
            tagPosition = currentDiv.find("class=\"js-bookmark\"")
            if(tagPosition < 10 and tagPosition > 0):
                ratingPos = currentDiv.find("c-rating__val rvw-item__usedprice-price")
                ratingPos = currentDiv.find(">", ratingPos) + 1
                ratingEnd = currentDiv.find("<", ratingPos)
                restaurant_price = currentDiv[ratingPos:ratingEnd]
                restaurant_tree[restaurant_name][reviewer_name]["price"] = restaurant_price

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
                            list.append(str(i * 0.002) + " " + currentDiv[ratingPos:ratingEnd] + " 0 0.5 0.5 0 1 255 " + str(int(float(currentDiv[ratingPos:ratingEnd]) * 51)) + " 0 ")
                            restaurant_tree[restaurant_name][reviewer_name]["rating_" + ratingName] = float(currentDiv[ratingPos:ratingEnd])
                        except:
                            pass

        pos = indexPos + 1
        i += 1
    writeFile.write(json.dumps(restaurant_tree, indent=4, separators=(',', ': '), ensure_ascii=False))
    writeFile.close()

    plyFile = open("output.ply", 'w')
    plyFile.write("ply\n")
    plyFile.write("format ascii 1.0\n")
    plyFile.write("element vertex " + str(len(list)) + "\n")
    plyFile.write("property float x\n")
    plyFile.write("property float y\n")
    plyFile.write("property float z\n")
    plyFile.write("property float nx\n")
    plyFile.write("property float ny\n")
    plyFile.write("property float nz\n")
    plyFile.write("property float intensity\n")
    plyFile.write("property uchar red\n")
    plyFile.write("property uchar green\n")
    plyFile.write("property uchar blue\n")
    plyFile.write("end_header\n")
    
    for item in list:
        plyFile.write(item + "\n")
        
    plyFile.close()

def parse(file):
    file = open(file, 'r', encoding='utf-8')
    fileContents = file.read()
    result = process(fileContents)
    return result

dict = parse("tabelog.html")

pcd = read_point_cloud("output.ply")
draw_geometries([pcd])