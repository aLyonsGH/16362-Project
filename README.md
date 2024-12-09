# 16362-Project - Using Generative Priors for 3D Scene Reconstruction

## Data Selection (Optional)
This project uses the SceneNet dataset: https://robotvault.bitbucket.io/scenenet-rgbd.html

The data selection folder contains scripts for choosing good images within the validation dataset. Here is the order for how they were run:
1. viewData.py: Shows preview of images from each scene, and select ones that look good. It produces the good_folders.txt file to put in the "processing" folder
2. choose_photos.py: From the scenes chosen, look at the images in each scene, and select the good images
3. retrieve_photo_info.py: Retrieve the depth and instance maps corresponding to the good images

In the end, the result is the selected data in the "chosen" folder, and 61 scenes were selected.

## Processing
The "processing" folder preprocesses the images, and gets them ready for DreamGaussian. Here is the order for how to run them:
1. segmentation.py: Gets the bounding boxes and crops the images accordingly, and puts the results in the pickle file "processed_objects.pkl"
2. Save the data from processed_objects.pkl into files and moves them to the correct locations in the folder "processed_images"

The output can be viewed and downloaded from this Google Drive link: https://drive.google.com/drive/folders/1dBYcFSrZzKQ-cpbi1Uda0B3cvHLqjN-d?usp=sharing

## DreamGaussian
The DreamGaussian.ipynb is a Colab Notebook for running DreamGaussian, and also getting the CLIP quantitative metrics. Note: After the DreamGaussian repo is cloned in the notebook, the script "my_process.py" needs to be added in. Paths need to be changed in the file. The file takes a long time to run, so here are google drive links to the outputs:
- All the meshes: https://drive.google.com/drive/folders/1i7KWZfLUvPyy4XUi-K4o--vYw0tyHVjp?usp=drive_link
- Video representations of the reconstructed objects: https://drive.google.com/drive/folders/1odHImwP-tZkAwnJMAdaq4S3XJup0UgXD?usp=sharing
The mean CLIP scores between the original image and reconstructed front, left, back, and right views was 0.78, 0.75, 0.77, 0.76 respectively.

## Reconstruction/Evaluation
The evaluation folder contains the script "scene_reconstruction.py" which takes the objects from DreamGuassian and the corresponding scene images/bounding boxes, and creates a 3D model of the room. It also computes the mean squared error between the ground truth depth and reconstructed depth images, which was 1160. Here is a google drive link to the reconstruction results: https://drive.google.com/drive/folders/1E-xZozIeXd7eKF5UlWOgzMCJtdl9QtPC?usp=sharing. Each scene contains the following outputs:
- {scene_id}.obj: The final 3D scene reconstruction
- color_rendered.png: A rendered (black and white) image of the reconstruction
- depth_rendered.png: A rendered depth image of the reconstruction
- depth_true.png: The ground truth depth image
- ROOM_{scene_id}.obj: Only the room in the reconstruction (i.e. no 3D objects)
- Rest: Materials for the meshes

