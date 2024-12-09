import cv2
import numpy as np
import sys
import os
#sys.path.append("..")
from PIL import Image
import colorsys
import pickle
import argparse



def valid_object(min_x, min_y, max_x, max_y, img):
    box_width = max_x-min_x
    box_height = max_y-min_y
    img_height, img_width = img.shape[0], img.shape[1]
    if box_width < 20 :
        return False
    if box_height < 20:
        return False
    if box_width/img_width > 0.5:
        return False
    if box_height/img_height > 0.5:
        return False
    area = box_height*box_width
    ratio = area/(img_height*img_width)
    if ratio < 0.001 or ratio > 0.2:
        return False
    return True
    
def get_objects(img, seg):
    objects = {}
    
    labels = np.unique(seg)
    labels = labels[labels!=0]

    img_rgba = np.ones((img.shape[0], img.shape[1], 4)) * 255
    img_rgba[:, :, 0:3] = img
    
    for label in labels:

        mask = (seg == label).astype(np.uint8)
        kernel = np.ones((5,5), np.uint8)
        dilated_mask = cv2.dilate(mask, kernel, iterations=1)

        num_objects, _, info, _ = cv2.connectedComponentsWithStats(dilated_mask)
        for i in range(1, num_objects):
            x, y, w, h, _ = info[i]
            min_x = x
            min_y = y
            max_x = x+w
            max_y = y+h
            
            if valid_object(min_x, min_y, max_x, max_y, img):
                masked_img = img_rgba*np.repeat(mask[:, :, np.newaxis], 4, axis=2)
                cropped = masked_img[min_y:max_y, min_x:max_x]
                objects[(min_x, min_y, max_x, max_y)] = cropped
    
    return objects

def get_selected_paths():
    good_paths = []
    for f in os.listdir("chosen/photo"):
        if f[-4:] != ".jpg":
            continue
        folder_id, id = f.split("_")[0], f.split("_")[1][:-4]
        good_paths.append([int(folder_id), int(id)])
    return good_paths

results = {}
for path in get_selected_paths():
    img_path = os.path.join("chosen", "photo", str(path[0]) + "_" + str(path[1]) + ".jpg")
    img = np.array(Image.open(img_path))
    seg_path = os.path.join("chosen", "instance", str(path[0]) + "_" + str(path[1]) + ".png")
    seg = np.array(Image.open(seg_path))

    res = get_objects(img, seg)
    key = str(path[0]) + "_" + str(path[1])
    results[key] = res

with open('processed_objects.pkl', 'wb') as file:
    pickle.dump(results, file)
