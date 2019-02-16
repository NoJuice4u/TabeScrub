import os
import argparse
import math
import requests
import math
import json
import time
import re
from . import parser_restaurant
from . import scan

MEALTIME_TABLE = {"lunch", "dinner"}
MAP_TABLE = {
"overall": 0,
"rating_サービス": 1,
"rating_雰囲気": 2,
"rating_CP": 3,
"rating_酒・ドリンク": 4
}

COORDINATES = {"longitude": 35.6863146, "latitude": 139.6877746}

X_WIDTH = 0.02
GROUP_WIDTH = 50

def parse(args, coords, userList, tabebot):
    SHOP_INDEX = {}
    SHOP_SORT_ORDER = {}
    REVIEWER_INDEX = {}
    distanceIndex = {}

    restaurant_tree = {}
    reviewerIndex = 0
    list = []
    
    for reviewer in userList:
        fName = "data\\" + reviewer + ".json"
        
        if not os.path.exists(fName):
            tabebot.announce("Processing: " + fName)
            print("Process Reviewer")
            scan.parseReviewer("", reviewer)
        print("ReviewerDone: " + reviewer)

        readFile = open(fName, encoding="utf-8") 
        fileJson = json.loads(readFile.read())
        for shop in fileJson:
            for reviewer in fileJson[shop]:
                for mealTime in fileJson[shop][reviewer]:
                    if(reviewer not in REVIEWER_INDEX):
                        REVIEWER_INDEX[reviewer] = reviewerIndex

                        list.append("-1 0 " + str(reviewerIndex * 0.25) + " 0.5 0.5 0 1 0 128 255 ")
                        list.append("-1 1 " + str(reviewerIndex * 0.25) + " 0.5 0.5 0 1 0 128 255 ")
                        list.append("-1 2 " + str(reviewerIndex * 0.25) + " 0.5 0.5 0 1 0 128 255 ")
                        list.append("-1 3 " + str(reviewerIndex * 0.25) + " 0.5 0.5 0 1 0 128 255 ")
                        list.append("-1 4 " + str(reviewerIndex * 0.25) + " 0.5 0.5 0 1 0 128 255 ")
                        list.append("-1 5 " + str(reviewerIndex * 0.25) + " 0.5 0.5 0 1 0 128 255 ")

                        reviewerIndex += 1

                    try:
                        restaurant_tree[shop]
                    except:
                        restaurant_tree[shop] = {}

                    try:
                        restaurant_tree[shop][reviewer]
                    except:
                        restaurant_tree[shop][reviewer] = fileJson[shop][reviewer]

            if(shop not in SHOP_INDEX):
                SHOP_INDEX[shop] = 1
            else:
                SHOP_INDEX[shop] += 1

    for shop in SHOP_INDEX:
        try:
            SHOP_SORT_ORDER[SHOP_INDEX[shop]].append(shop)
        except:
            SHOP_SORT_ORDER[SHOP_INDEX[shop]] = [shop]

    xPos = 0

    restaurantInfo = open("data\\restaurantInfo.json", "a+", encoding="utf-8")
    restaurantInfo.seek(0)
    restaurantInfoJson = json.loads(restaurantInfo.read())
    incr = 0

    try:
        total = 0
        for depthId in sorted(SHOP_SORT_ORDER, reverse=True):
            if(depthId <= 1):
                break
            total += len(SHOP_SORT_ORDER[depthId])
        for depthId in sorted(SHOP_SORT_ORDER, reverse=True):
            if(depthId <= 1):
                break
            for shop in SHOP_SORT_ORDER[depthId]:
                incr += 1
                for reviewer in restaurant_tree[shop]:
                    if shop not in restaurantInfoJson:
                        print(str(incr) + " - " + str(total))
                        result = parser_restaurant.parseRestaurantURL(restaurant_tree[shop][reviewer]['url'])
                        restaurantInfoJson[shop] = result
                        time.sleep(1)
                    priceColor = 0
                    greenStr = 0

                    # print(str(len(restaurant_tree[shop])) + " : " + shop + "-" + reviewer + "::" + str(restaurant_tree[shop][reviewer]))
                    list.append(str(xPos * X_WIDTH) + " " + str(-1) + " " + str(REVIEWER_INDEX[reviewer] * 0.25) + " 0.5 0.5 0 1 " + str(255) + " " + str(0) + " " + str(0) + " ")

                    for mealTime in MEALTIME_TABLE:
                        if(mealTime not in restaurant_tree[shop][reviewer]):
                            continue

                        if("price_min" in restaurant_tree[shop][reviewer][mealTime]):
                            if(restaurant_tree[shop][reviewer][mealTime]["price_min"] >= 0):
                                priceColor = 0
                                greenStr = 128
                            if(restaurant_tree[shop][reviewer][mealTime]["price_min"] > 2000):
                                priceColor = 0
                                greenStr = 255
                            if(restaurant_tree[shop][reviewer][mealTime]["price_min"] > 3000):
                                priceColor = 128
                                greenStr = 255
                            if(restaurant_tree[shop][reviewer][mealTime]["price_min"] > 5000):
                                priceColor = 255
                                greenStr = 255
                            if(restaurant_tree[shop][reviewer][mealTime]["price_min"] > 10000):
                                priceColor = 255
                                greenStr = 0

                        for rating in restaurant_tree[shop][reviewer][mealTime]:
                            if(rating not in MAP_TABLE):
                                continue

                            blue = 0
                            overallOffset = 0
                            if(rating == "overall"):
                                overallOffset = 0.15

                            value = float(restaurant_tree[shop][reviewer][mealTime][rating])

                            if(value == -1):
                                value = -0.5
                                color = 0
                            if(value > 5):
                                color = 255

                            list.append(str(xPos * X_WIDTH) + " " + str(value) + " " + str((REVIEWER_INDEX[reviewer] * 0.25) + overallOffset) + " 0.5 0.5 0 1 " + str(priceColor) + " " + str(greenStr) + " " + str(blue) + " ")
                # print(shop.ljust(30) + " :: " + str(len(restaurant_tree[shop])))

                distance = getVectorDistance(restaurantInfoJson[shop], coords)
                reviewer = next(iter(restaurant_tree[shop].keys()))
                distanceIndex[distance] = { "url": restaurant_tree[shop][reviewer]['url'], "name": shop}
                xPos += 1
            xPos += GROUP_WIDTH
        
        for x in sorted(distanceIndex):
            lunch_review = []
            lunch_price_min = []
            lunch_price_max = []
            dinner_review = []
            dinner_price_min = []
            dinner_price_max = []
            categories = set()

            shop = distanceIndex[x]['name']
            for rvwr in restaurant_tree[shop]:
                try:
                    if("lunch" in restaurant_tree[shop][rvwr]):
                        lunch_review.append(restaurant_tree[shop][rvwr]['lunch']['overall'])
                        lunch_price_min.append(restaurant_tree[shop][rvwr]['lunch']['price_min'])
                        lunch_price_max.append(restaurant_tree[shop][rvwr]['lunch']['price_max'])
                        for cat in restaurant_tree[shop][rvwr]['categories']:
                            categories.add(cat)
                    elif("dinner" in restaurant_tree[shop][rvwr]):
                        dinner_review.append(restaurant_tree[shop][rvwr]['dinner']['overall'])
                        dinner_price_min.append(restaurant_tree[shop][rvwr]['dinner']['price_min'])
                        dinner_price_max.append(restaurant_tree[shop][rvwr]['dinner']['price_max'])
                        for cat in restaurant_tree[shop][rvwr]['categories']:
                            categories.add(cat)
                    else:
                        pass
                except:
                    pass
            distanceIndex[x]['lunch'] = lunch_review
            distanceIndex[x]['dinner'] = dinner_review
            distanceIndex[x]['lmax'] = lunch_price_max
            distanceIndex[x]['dmax'] = dinner_price_max
            distanceIndex[x]['categories'] = categories
            
            # print(str(x) + " :: " + distanceIndex[x]['url'] + " :: " + str(distanceIndex[x]['lunch']) + ", " + str(distanceIndex[x]['dinner']) + " $$ " + str(distanceIndex[x]['lmax']) + ", " + str(distanceIndex[x]['dmax']))
        
    finally:
        restaurantInfo.truncate(0)
        restaurantInfo.write(json.dumps(restaurantInfoJson, indent=4, separators=(',', ': '), ensure_ascii=False))

        plyFile = open("data\\output.ply", 'w')
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
    return distanceIndex

def getVectorDistance(a, b):
    lon = float(a["longitude"]) - float(b["longitude"])
    lat = float(a["latitude"]) - float(b["latitude"])

    return math.sqrt((lon * lon) + (lat * lat))

# dict = parse(0, COORDINATES)