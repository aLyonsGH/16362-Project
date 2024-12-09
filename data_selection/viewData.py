import os
import cv2
import numpy as np
import argparse


def select_images(image_files, num_show):
    inds = [np.floor(i * len(image_files)/num_show) for i in range(num_show)]
    return [image_files[int(i)] for i in inds]

def get_combined(files, num_show):

    images = []
    for file in files:
        images.append(cv2.imread(file))

    h, w, _ = images[0].shape
    dim = int(np.sqrt(num_show))
    combined = np.zeros((h*dim, w*dim, 3))
    for i in range(num_show):
        combined[h*(i//dim):h*((i//dim)+1), w*(i%dim):w*((i%dim)+1)] = images[i]
    combined = combined/255
    return combined


def save_folder(folder_name):
    with open("good_folders.txt", "a") as f:
        f.write(folder_name + "\n")

def run(main_folder, early_start, num_show):
  
    if not os.path.isdir(main_folder):
        print("NOT VALID FOLDER")
        exit()


    subfolders = [main_folder + "/" + d + "/photo" for d in os.listdir(main_folder) if os.path.isdir(main_folder + "/" + d + "/photo")]
    
    subfolders = sorted(subfolders, key=lambda f: int(f.split("/")[-2]))

    for i, subfolder in enumerate(subfolders):

        if i<early_start:
            continue

        #image_files = [os.path.join(subfolder, f) for f in os.listdir(subfolder) if os.path.isdir(os.path.join(subfolder, f))]
        image_files = [os.path.join(subfolder, f) for f in os.listdir(subfolder)]
        selected_images = select_images(image_files, num_show)

        combined = get_combined(selected_images, num_show)

        print(i)
        cv2.destroyAllWindows()
        while True:
            cv2.imshow(str(i),combined)
            k = cv2.waitKey(33)
            if k == ord('n'):    
                break
            elif k == ord('s'):
                save_folder(subfolder)
                break
            elif k == 27:
                exit()


        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--main_folder", type=str)
    parser.add_argument("--early_start", type=int, default=0)
    parser.add_argument("--num_show", type=int, default=25)

    args = parser.parse_args()
    run(args.main_folder, args.early_start, args.num_show)

