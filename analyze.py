from os import walk
import argparse
import requests
import math
import json
import time
import re

MEALTIME_TABLE = {"lunch", "dinner"}
MAP_TABLE = {
"overall": 0,
"rating_サービス": 1,
"rating_雰囲気": 2,
"rating_CP": 3,
"rating_酒・ドリンク": 4
}

X_WIDTH = 0.02
GROUP_WIDTH = 50

SHOP_INDEX = {}
SHOP_SORT_ORDER = {}
REVIEWER_INDEX = {}

def parse(args):
    restaurant_tree = {}
    reviewerIndex = 0
    list = []
    j = 0
    
    for (dirpath, dirnames, filenames) in walk("data\\"):
    
        for file in filenames:
            if(file == "restaurantInfo.json"):
                continue
            if(file[-5:] == '.json'):
                readFile = open("data\\" + file, encoding="utf-8")
                
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
            j += 1

    for shop in SHOP_INDEX:
        try:
            SHOP_SORT_ORDER[SHOP_INDEX[shop]].append(shop)
        except:
            SHOP_SORT_ORDER[SHOP_INDEX[shop]] = [shop]

    xPos = 0

    restaurantInfo = open("data\\restaurantInfo.json", "a+", encoding="utf-8")
    restaurantInfo.seek(0)
    restaurantInfoJson = json.loads(restaurantInfo.read())
    for depthId in sorted(SHOP_SORT_ORDER, reverse=True):
        if(depthId == 1):
            break
        for shop in SHOP_SORT_ORDER[depthId]:
            #r = requests.get("https://tabelog.com/rvwr/" + args.user + "/reviewed_restaurants/list/?bookmark_type=1&sk=&sw=&Srt=D&SrtT=mfav&review_content_exist=0&PG=" + str(page))
            #contents = r.text
        
            if shop not in restaurantInfoJson:
                restaurantInfoJson[shop] = True
                # IND
            for reviewer in restaurant_tree[shop]:
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
                            blue = 255
                            overallOffset = 0.15

                        value = float(restaurant_tree[shop][reviewer][mealTime][rating])

                        if(value == -1):
                            value = -0.5
                            color = 0
                        if(value > 5):
                            color = 255

                        list.append(str(xPos * X_WIDTH) + " " + str(value) + " " + str((REVIEWER_INDEX[reviewer] * 0.25) + overallOffset) + " 0.5 0.5 0 1 " + str(priceColor) + " " + str(greenStr) + " " + str(blue) + " ")
            # print(shop.ljust(30) + " :: " + str(len(restaurant_tree[shop])))
            xPos += 1
        xPos += GROUP_WIDTH

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

dict = parse(0)