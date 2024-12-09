import cv2
import numpy as np
import os

#Read foldre names in txt
with open("good_folders.txt", "r") as f:
    folders = f.readlines()
    folders = [f.strip() for f in folders]


for dir in folders:
    files = [os.path.join(dir, f) for f in os.listdir(dir)]
    files = sorted(files, key=lambda f: int(f.split("/")[-1].split(".")[0]))

    images = []
    for file in files:
        images.append(cv2.imread(file))

    for i in range(len(images)):

        id = int(files[i].split("/")[-1].split(".")[0])
        cv2.destroyAllWindows()
        done = False
        while True:
            cv2.imshow(str(i),images[i])
            k = cv2.waitKey(33)
            if k == ord('n'):    
                break
            elif k == ord('s'):
                #copy to folder named "chosen"
                cv2.imwrite("chosen/photo/" + dir.replace("/", "_")[2] + "_" + str(id) + ".jpg", images[i])
                break
            elif k == ord('c'):
                done = True
                break
            elif k == 27:
                exit()
        if done:
            break

