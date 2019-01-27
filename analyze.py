from os import walk
import argparse
import requests
import math
import json
import time
import re

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
            if(file[-5:] == '.json'):
                readFile = open("data\\" + file, encoding="utf-8")
                
                fileJson = json.loads(readFile.read())
                for shop in fileJson:
                    for reviewer in fileJson[shop]:
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
    for depthId in sorted(SHOP_SORT_ORDER, reverse=True):
        if(depthId == 1):
            break
        for shop in SHOP_SORT_ORDER[depthId]:
            for reviewer in restaurant_tree[shop]:
                priceColor = 0
                greenStr = 0
                if("price_min" in restaurant_tree[shop][reviewer]):
                    if(restaurant_tree[shop][reviewer]["price_min"] >= 0):
                        priceColor = 0
                        greenStr = 128
                    if(restaurant_tree[shop][reviewer]["price_min"] > 2000):
                        priceColor = 0
                        greenStr = 255
                    if(restaurant_tree[shop][reviewer]["price_min"] > 3000):
                        priceColor = 128
                        greenStr = 255
                    if(restaurant_tree[shop][reviewer]["price_min"] > 5000):
                        priceColor = 255
                        greenStr = 255
                    if(restaurant_tree[shop][reviewer]["price_min"] > 10000):
                        priceColor = 255
                        greenStr = 0

                # print(str(len(restaurant_tree[shop])) + " : " + shop + "-" + reviewer + "::" + str(restaurant_tree[shop][reviewer]))
                list.append(str(xPos * X_WIDTH) + " " + str(-1) + " " + str(REVIEWER_INDEX[reviewer] * 0.25) + " 0.5 0.5 0 1 " + str(255) + " " + str(0) + " " + str(0) + " ")

                for rating in restaurant_tree[shop][reviewer]:
                    if(rating not in MAP_TABLE):
                        continue

                    blue = 0
                    overallOffset = 0
                    if(rating == "overall"):
                        blue = 255
                        overallOffset = 0.15

                    value = float(restaurant_tree[shop][reviewer][rating])

                    if(value == -1):
                        value = -0.5
                        color = 0
                    if(value > 5):
                        color = 255

                list.append(str(xPos * X_WIDTH) + " " + str(value) + " " + str((REVIEWER_INDEX[reviewer] * 0.25) + overallOffset) + " 0.5 0.5 0 1 " + str(priceColor) + " " + str(greenStr) + " " + str(blue) + " ")
            # print(shop.ljust(30) + " :: " + str(len(restaurant_tree[shop])))
            xPos += 1
        xPos += GROUP_WIDTH

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