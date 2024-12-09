import os
import shutil

dir = "val/0"

for f in os.listdir("chosen/photo"):
    folder_id = f.split("_")[0]
    id = f.split("_")[1].split(".")[0]
    shutil.copy(os.path.join(dir, folder_id, "depth", id + ".png"), os.path.join("chosen", "depth", f.replace(".jpg", ".png")))
    shutil.copy(os.path.join(dir, folder_id, "instance", id + ".png"), os.path.join("chosen", "instance", f.replace(".jpg", ".png")))  

