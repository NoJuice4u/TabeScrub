from os import walk
import argparse
import requests
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
    list = ["0 0 0 0.5 0.5 0 1 0 0 0 ", "0 1 0 0.5 0.5 0 1 0 0 0 ", "0 2 0 0.5 0.5 0 1 0 0 0 ", "0 3 0 0.5 0.5 0 1 0 0 0 ", "0 4 0 0.5 0.5 0 1 0 0 0 ", "0 5 0 0.5 0.5 0 1 0 0 0 "]
    shopIndex = 0
    j = 0
    
    for (dirpath, dirnames, filenames) in walk("data\\"):
    
        for file in filenames:
            if(file[-5:] == '.json'):
                readFile = open("data\\" + file, encoding="utf-8")
                
                fileJson = json.loads(readFile.read())
                for shop in fileJson:
                    for reviewer in fileJson[shop]:
                        for rating in fileJson[shop][reviewer]:
                            if(rating == "price"):
                                continue
                            if(shop not in SHOP_INDEX):
                                SHOP_INDEX[shop] = shopIndex
                                shopIndex += 1
                            value = fileJson[shop][reviewer][rating]
                            color = value * 51
                            if(value == -1):
                                color = 0
                            list.append(str(SHOP_INDEX[shop] * 0.02) + " " + str(value) + " " + str(j * 1) + " 0.5 0.5 0 1 255 " + str(int(float(color))) + " 0 ")
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