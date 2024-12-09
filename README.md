# 16362-Project

## Data Selection (Optional)
This project uses the SceneNet dataset: https://robotvault.bitbucket.io/scenenet-rgbd.html

The data selection folder contains scripts for choosing good images within the validation dataset. Here is the order for how they were run:
1. viewData.py: Shows preview of images from each scene, and select ones that look good. It produces the good_folders.txt file to put in the "processing" folder
2. choose_photos.py: From the scenes chosen, look at the images in each scene, and select the good images
3. retrieve_photo_info.py: Retrieve the depth and instance maps corresponding to the good images

In the end, the result is the selected data in the "chosen" folder 

## Processing
The "processing" folder preprocesses the images, and gets them ready for DreamGaussian. Here is the order for how to run them:
1. segmentation.py: Gets the bounding boxes and crops the images accordingly, and puts the results in the pickle file "processed_objects.pkl"
2. Save the data from processed_objects.pkl into files and moves them to the correct locations in the folder "processed_images"

## DreamGaussian
The DreamGaussian.ipynb is a Colab Notebook for running DreamGaussian, and also getting the CLIP quantitative metrics. Paths need to be changed in the file. 

## Reconstruction/Evaluation
The evaluation folder contains the script "scene_reconstruction.py" which takes the objects from DreamGuassian and the corresponding scene images/bounding boxes, and creates a 3D model of the room. It also computes the mean squared error between the ground truth depth and reconstructed depth images.
