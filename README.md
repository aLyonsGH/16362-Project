# 16362-Project - Using Generative Priors for 3D Scene Reconstruction

## Intro
The goal of this project was given an image of a scene, to use DreamGaussian as a 3D prior to reconstruct the scene. More details for this project are in the presentation file "Project Presentation.pdf". Unfortunately, many of the scripts take a long time to run, and since the workload has to be split locally and on Google Colab, it would require a long time to setup and run the scripts oneself. Therefore, I included folders of every intermediate results (as well as the final results).

## Data Selection
This project uses the SceneNet dataset: https://robotvault.bitbucket.io/scenenet-rgbd.html

The data selection folder contains scripts for choosing good images within the validation dataset. Here is the order for how they were run:
1. viewData.py: Shows preview of images from each scene, and select ones that look good. It produces the good_folders.txt file to put in the "processing" folder
2. choose_photos.py: From the scenes chosen, look at the images in each scene, and select the good images
3. retrieve_photo_info.py: Retrieve the depth and instance maps corresponding to the good images

In the end, the result is the selected data in the "chosen" folder, and 61 scenes were selected.

## Processing

The "processing" folder preprocesses the images, and gets them ready for DreamGaussian. Here is a summary of the algorithm:
1. For each selected scene, load the bounding boxes
2. Select the objects with reasonably sized bounding boxes, and save the bounding boxes and corresponding cropped images in a dictionary
3. Convert the cropped images to rgba, and saved them in separate file to be inputted into DreamGaussian.

Here is the order for how to run the scripts:
1. segmentation.py: Gets the bounding boxes and crops the images accordingly, and puts the results in the pickle file "processed_objects.pkl"
2. Save the data from processed_objects.pkl into files and moves them to the correct locations in the folder "processed_images"

The output can be viewed and downloaded from this Google Drive link: https://drive.google.com/drive/folders/1dBYcFSrZzKQ-cpbi1Uda0B3cvHLqjN-d?usp=sharing

## DreamGaussian
The DreamGaussian.ipynb is a Colab Notebook for running DreamGaussian, and also getting the CLIP quantitative metrics. 
Here is a summary of the code:
1. Clone and setup the DreamGaussian repo
2. Preprocess all of the images according to DreamGaussian
3. Run all the images into the model to create the 3D models
4. Create rotating videos of the 3D objects
5. Compute CLIP scores between different views of the objects and the corresponding reference images

Note: After the DreamGaussian repo is cloned in the notebook, the script "my_process.py" needs to be added in. Paths need to be changed in the file. The file takes a long time to run, so here are google drive links to the outputs:
- All the meshes: https://drive.google.com/drive/folders/1i7KWZfLUvPyy4XUi-K4o--vYw0tyHVjp?usp=drive_link
- Video representations of the reconstructed objects: https://drive.google.com/drive/folders/1odHImwP-tZkAwnJMAdaq4S3XJup0UgXD?usp=sharing
The mean CLIP scores between the original image and reconstructed front, left, back, and right views was 0.78, 0.75, 0.77, 0.76 respectively.

## Reconstruction/Evaluation
The evaluation folder contains the script "scene_reconstruction.py" which takes the objects from DreamGuassian and the corresponding scene images/bounding boxes, and creates a 3D model of the room. It also computes the mean squared error between the ground truth depth and reconstructed depth images, which was 1160. Here is a summary of the algorithm for reconstructing each scene:
1. Load the depth map, and use loaded Camera Intrinsics to convert the depth map into a 3D point cloud
2. Connect nearby points in the point cloud to create a 3D mesh of the room
3. For each bounding box, get the depths of all the points in the box to estimate how deep in the room the object should go
4. Rescale the object meshes so the ratio of the object to the room is the same as the ratio of the bounding box to the image.
5. Add the objects to the scene, save the full model, and create the image and depth renderings
6. Compute the mean squared error between the true and reconstructed depth renderings

Here is a google drive link to the reconstruction results: https://drive.google.com/drive/folders/1E-xZozIeXd7eKF5UlWOgzMCJtdl9QtPC?usp=sharing. Each scene contains the following outputs:
- {scene_id}.obj: The final 3D scene reconstruction
- color_rendered.png: A rendered (black and white) image of the reconstruction
- depth_rendered.png: A rendered depth image of the reconstruction
- depth_true.png: The ground truth depth image
- ROOM_{scene_id}.obj: Only the room in the reconstruction (i.e. no 3D objects)
- Rest: Materials for the meshes

