import numpy as np
import os
import trimesh
from PIL import Image
import cv2
import pickle
import shutil
import argparse
from tqdm import tqdm
import pyrender



def load_depth_map(scene_id):
    depth_path = "chosen/depth/" + scene_id + ".png"
    depth_img = np.array(Image.open(depth_path), dtype=np.float64)
    depth_map = depth_img#depth_img/np.max(depth_img)
    return depth_map

#From repo: https://github.com/jmccormac/pySceneNetRGBD/blob/master/camera_pose_and_intrinsics_example.py
def camera_intrinsic_transform(vfov=45,hfov=60,pixel_width=320,pixel_height=240):
    camera_intrinsics = np.zeros((3,3))
    camera_intrinsics[2,2] = 1
    camera_intrinsics[0,0] = (pixel_width/2.0)/np.tan(np.radians(hfov/2.0))
    camera_intrinsics[0,2] = pixel_width/2.0
    camera_intrinsics[1,1] = (pixel_height/2.0)/np.tan(np.radians(vfov/2.0))
    camera_intrinsics[1,2] = pixel_height/2.0
    return camera_intrinsics


def get_point_cloud_old(depth_map):
    H, W = depth_map.shape

    raw_point_cloud = np.ones((H*W, 3))
    raw_point_cloud[:,1] = np.repeat(np.arange(H), W)
    raw_point_cloud[:,0] = np.tile(np.arange(W), H)

    intrinsics = camera_intrinsic_transform()
    
    point_cloud = np.linalg.inv(intrinsics) @ raw_point_cloud.T

    point_cloud *= depth_map.reshape((H*W))
    point_cloud = point_cloud.T 

    return point_cloud

def get_point_cloud(depth_map):
    H, W = depth_map.shape

    raw_point_cloud = np.ones((H*W, 3))
    #point_cloud[:,2] = depth_map.reshape((H*W))
    raw_point_cloud[:,1] = np.repeat(np.arange(H), W)
    raw_point_cloud[:,0] = np.tile(np.arange(W), H)

    intrinsics = camera_intrinsic_transform()
    
    point_cloud = np.linalg.inv(intrinsics) @ raw_point_cloud.T

    point_cloud *= (depth_map.reshape((H*W)) * 0.001)
    point_cloud = point_cloud.T 

    return point_cloud


def pos_to_point(x, y, W, H):
    return (W*y + x)

def valid_triangle(p1, p2, p3, point_cloud, thresh=0.05):
    max = np.max(point_cloud[:,2])
    #Check if any 0 depth
    if point_cloud[p1][2] * point_cloud[p2][2] * point_cloud[p3][2] == 0:
        return False
    if abs(point_cloud[p1][2] - point_cloud[p2][2]) > thresh*max:
        return False
    elif abs(point_cloud[p2][2] - point_cloud[p3][2]) > thresh*max:
        return False
    elif abs(point_cloud[p1][2] - point_cloud[p3][2]) > thresh*max:
        return False
    else:
        return True
    

def gen_room(depth_map):
    H, W = depth_map.shape
    point_cloud = get_point_cloud(depth_map)
    #max_depth = 500
    #point_cloud[:,2] = (point_cloud[:,2]/np.max(point_cloud[:,2]))*max_depth
    vertices = point_cloud
    faces = []
    stride = 1
    for y in range(0, depth_map.shape[0]-stride, stride):
        for x in range(0, depth_map.shape[1]-stride, stride):
            ul = pos_to_point(x, y, W, H)
            ur = pos_to_point(x+stride, y, W, H)
            ll = pos_to_point(x, y+stride, W, H)
            lr = pos_to_point(x+stride, y+stride, W, H)

            if valid_triangle(ul, ur, ll, point_cloud):
                faces.append([ul, ur, ll])
            if valid_triangle(ll, lr, ur, point_cloud):
                faces.append([ll, lr, ur])

    room = trimesh.Trimesh(vertices=vertices, faces=faces)
    return room, point_cloud


def get_objects(scene_id, logdir):
    objects = []
    #prefix = "__".join(name.split("__")[:-1])
    prefix = logdir + "/res__" + scene_id
    i = 0
    curr_name = prefix + "__" + str(i) + ".obj"

    while os.path.exists(curr_name):
        object = trimesh.load(curr_name)
        object.vertices[:,1] *= -1
        objects.append(object)
        i+=1
        curr_name = prefix + "__" + str(i) + ".obj"
    return objects


def scale_object(object, bounding_box, image, room):
    (min_x, min_y, max_x, max_y) = bounding_box

    object.vertices -= np.min(object.vertices,axis=0)

    #The two should be equal, but some error
    H, W = image.shape
    h, w = max_y-min_y, max_x-min_x
    room_H = np.max(room.vertices[:,1])-np.min(room.vertices[:,1])
    room_W = np.max(room.vertices[:,0])-np.min(room.vertices[:,0])

    #desired height when scaling by height
    room_h = h*room_H/H
    #desired width when scaling by width
    room_w = w*room_W/W

    scaled_wrt_w = room_w*np.copy(object.vertices)/(np.max(object.vertices[:,0])-np.min(object.vertices[:,0]))
    scaled_wrt_h = room_h*np.copy(object.vertices)/(np.max(object.vertices[:,1])-np.min(object.vertices[:,1]))
   
    object.vertices = np.mean([scaled_wrt_w, scaled_wrt_h], axis=0)

    object.vertices -= np.mean(object.vertices,axis=0)
    
    return object


def assemble_room(room, depth_map, point_cloud, objects, bounding_box_dict):
    H, W = depth_map.shape

    cropped_boxes = list(bounding_box_dict.values())
    bounding_boxes = list(bounding_box_dict.keys())

    assembled = trimesh.Scene()

    assembled.add_geometry(room)
    for i, object in enumerate(objects):

        object = scale_object(object, bounding_boxes[i], depth_map, room)

        (min_x, min_y, max_x, max_y) = bounding_boxes[i]

        locs = []
        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                if cropped_boxes[i][y-min_y, x-min_x, 3] > 0:
                    point_ind = pos_to_point(x, y, W, H)
                    point = point_cloud[point_ind]
                    locs.append(point)
        new_loc = np.mean(np.array(locs),axis=0)

        object.vertices += new_loc

        assembled.add_geometry(object)

    angle = np.pi
    direction = [1, 0, 0]
    center = [0, 0, 0]
    
    R = trimesh.transformations.rotation_matrix(angle, direction, center)
    for mesh in assembled.geometry.values():
        mesh.apply_transform(R)

    return assembled


def get_bounding_box_dict(scene_id, all_dict):
    box_dict = all_dict[scene_id]
    return box_dict

def render_scene(scene_mesh, save_name):
    K = camera_intrinsic_transform()
    camera = pyrender.IntrinsicsCamera(
        fx=K[0, 0], fy=K[1, 1], 
        cx=K[0, 2], cy=K[1, 2]
    )
    scene = pyrender.Scene()

    for mesh in scene_mesh.geometry.values():
        scene.add(pyrender.Mesh.from_trimesh(trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces)))
      
    camera_pose = np.eye(4)
    scene.add(camera, pose=camera_pose)

    renderer = pyrender.OffscreenRenderer(viewport_width=320, viewport_height=240)
    color, depth = renderer.render(scene)

    cv2.imwrite(save_name + "/depth_rendered.png", 255*depth/np.max(depth))
    cv2.imwrite(save_name + "/color_rendered.png", color)
    return 255*depth/np.max(depth)

with open('processed_objects.pkl', 'rb') as f:
    all_dict = pickle.load(f)

def generate_scenes(scene_ids, log_dir, save_dir):
    mses = []
    for scene_id in tqdm(scene_ids):
        save_name = save_dir + "/" + scene_id

        if os.path.exists(save_name):
            shutil.rmtree(save_name)
        os.makedirs(save_name)

        depth_map = load_depth_map(scene_id)
        cv2.imwrite(save_name + "/depth_true.png", 255*depth_map/np.max(depth_map))

        room, point_cloud = gen_room(depth_map)
        room.export(save_name + "/ROOM_" + scene_id + ".obj")
        objects = get_objects(scene_id, log_dir)
        bounding_box_dict = get_bounding_box_dict(scene_id, all_dict)
        assembled = assemble_room(room, depth_map, point_cloud, objects, bounding_box_dict)

        assembled.export(save_name + "/" + scene_id + ".obj")
        rendered_depth = render_scene(assembled, save_name)
        norm_depth = 255*depth_map/np.max(depth_map)
        mse = np.mean((rendered_depth-norm_depth) ** 2)
        mses.append(mse)
    return mses

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--logdir", type=str)
    parser.add_argument("--save_dir", type=str, default="reconstructions")
    args = parser.parse_args()

    scene_ids = []
    for f in os.listdir(args.logdir):
        if f[-4:] != ".obj":
            continue
        scene_id = f.split("__")[1]
        if scene_id not in scene_ids:
            scene_ids.append(scene_id)

    mses = generate_scenes(scene_ids, args.logdir, args.save_dir)
    np.save("all_mse.npy", mses)


