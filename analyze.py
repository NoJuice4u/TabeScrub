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

SHOP_INDEX = {}

def parse(args):
    restaurant_tree = {}
    list = []
    shopIndex = 0
    j = 0
    
    for (dirpath, dirnames, filenames) in walk("data\\"):
    
        for file in filenames:
            if(file[-5:] == '.json'):
                readFile = open("data\\" + file, encoding="utf-8")
                
                fileJson = json.loads(readFile.read())
                for shop in fileJson:
                    for reviewer in fileJson[shop]:
                        priceColor = 0
                        if("price_min" in fileJson[shop][reviewer]):
                            if(fileJson[shop][reviewer]["price_min"] >= 0):
                                priceColor = 0
                                greenStr = 128
                            if(fileJson[shop][reviewer]["price_min"] > 2000):
                                priceColor = 0
                                greenStr = 255
                            if(fileJson[shop][reviewer]["price_min"] > 3000):
                                priceColor = 128
                                greenStr = 255
                            if(fileJson[shop][reviewer]["price_min"] > 5000):
                                priceColor = 255
                                greenStr = 255
                            if(fileJson[shop][reviewer]["price_min"] > 10000):
                                priceColor = 255
                                greenStr = 0

                        for rating in fileJson[shop][reviewer]:
                            if(rating not in MAP_TABLE):
                                continue
                            if(shop not in SHOP_INDEX):
                                SHOP_INDEX[shop] = shopIndex
                                shopIndex += 1
                            value = float(fileJson[shop][reviewer][rating])

                            if(value == -1):
                                color = 0
                            if(value > 5):
                                color = 255
                            list.append(str(SHOP_INDEX[shop] * 0.002) + " " + str(value) + " " + str(j * 0.25) + " 0.5 0.5 0 1 " + str(priceColor) + " " + str(greenStr) + " " + str(0) + " ")
            list.append("0 0 " + str(j * 0.25) + " 0.5 0.5 0 1 0 128 255 ")
            list.append("0 1 " + str(j * 0.25) + " 0.5 0.5 0 1 0 128 255 ")
            list.append("0 2 " + str(j * 0.25) + " 0.5 0.5 0 1 0 128 255 ")
            list.append("0 3 " + str(j * 0.25) + " 0.5 0.5 0 1 0 128 255 ")
            list.append("0 4 " + str(j * 0.25) + " 0.5 0.5 0 1 0 128 255 ")
            list.append("0 5 " + str(j * 0.25) + " 0.5 0.5 0 1 0 128 255 ")
            j += 1

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