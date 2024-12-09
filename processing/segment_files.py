from PIL import Image
import numpy as np
import pickle
import os
import argparse


with open('processed_objects.pkl', 'rb') as file:
    results = pickle.load(file)

if not os.path.exists("processed_images"):
    os.makedirs("processed_images")

for path, objects in results.items():
    folder_id, img_id = path.split("_")
    objects_list = list(objects.values())
    for i in range(len(objects_list)):
        name = folder_id + "_" + img_id
        file_name = name + "__" + str(i) + ".png"
        mask = objects_list[i][:,:,3]
        img = Image.fromarray(objects_list[i][:,:,:3].astype(np.uint8))
        img = img.convert('RGBA')
        img = np.array(img)
        img[:,:,3] = np.where(mask == 255, img[:,:,3], 0)
        img = Image.fromarray(img)
        img.save(os.path.join("processed_images", file_name))
