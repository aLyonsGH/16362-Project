# 16362-Project

## Data Selection (Optional)
This project uses the SceneNet dataset: https://robotvault.bitbucket.io/scenenet-rgbd.html
The data selection folder contains scripts for choosing good images within the validation dataset. Here is the order for how they were run:
1. viewData.py: Shows preview of images from each scene, and select ones that look good
2. choose_photos.py: From the scenes chosen, look at the images in each scene, and select the good images
3. retrieve_photo_info.py: Retrieve the depth and instance maps corresponding to the good images

In the end, the result is the selected data in the "chosen" folder 
