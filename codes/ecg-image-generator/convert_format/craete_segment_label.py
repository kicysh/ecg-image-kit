from PIL import Image
import numpy as np
import glob
import os
import random
import json
import sys

LEAD_NAME = "I"

IMAGES_DIR_PATH = ""
LABELS_DIR_PATH = ""
JSON_DIR_PATH = ""
IMAGE_EXT = ".png"  # or ".jpg"

OUTPUT_IMAGES_DIR_PATH = ""
OUTPUT_LABELS_DIR_PATH = ""
OUTPUT_SIZE = (960, 320) # xy

AUG_ROUTATE = 15



def get_basenames(img_dir_path:str, label_dir_path:str, json_dir_path: str, image_ext:str) -> tuple:
    im_names = [os.path.basename(i).replace(image_ext, "") for i in glob.glob(os.path.join(img_dir_path, "*"+image_ext))]
    label_names = [os.path.basename(i).replace(image_ext, "") for i in glob.glob(os.path.join(label_dir_path,"*"+image_ext))]
    json_names = [os.path.basename(i).replace(".json", "") for i in glob.glob(os.path.join(json_dir_path,"*.json"))]
    print("im", len(im_names))
    print("lb", len(label_names))
    print("json", len(json_names))
    print(json_names[0])
    return sorted(list(set(im_names) & set(label_names) & set(json_names)))


def get_bbox(json_dir_path, basename, lead_name):
    path = os.path.join(json_dir_path, basename+".json")
    with open(path, "r") as f:
        j_load = json.load(f)
    for lead in j_load["leads"]:
        if lead["lead_name"]==lead_name:
            y_min, x_min, y_max, x_max = lead["lead_bounding_box"]["0"]+ lead["lead_bounding_box"]["2"]
            return int(x_min), int(y_min), int(x_max), int(y_max)


def swap_black_and_white(im, bbox):
    cut_off = 200
    pad = 2

    im = np.array(im)[:,:,:3]
    im[np.mean(im, 2) <cut_off] = 1
    im[np.mean(im, 2) >= cut_off] = 0
    im[im==1] = 255
    im[:pad] = 0
    im[:,:pad]= 0
    im[-1*pad:] = 0
    im[:,-1*pad:] = 0
    im[:max(bbox[1],0)] = 0
    im[min(bbox[3], im.shape[0]):] = 0
    im[:,:max(bbox[0],0)] = 0
    im[:,min(bbox[2], im.shape[1]):] = 0
    return Image.fromarray(im)


def augmentation(im, lb, bbox, rotate, output_size):
    color = (0,0,0) # black
    r_s = [random.randint(-2,10) for _ in range(4)]

    im = Image.fromarray(np.array(im)[:,:,:3])
    np_lb = np.array(lb)[:,:,:3]
    lb = Image.fromarray(np_lb)

    rotate_ = random.uniform(-1 * rotate, rotate)
    center = (int((bbox[1]+bbox[3])//2), int((bbox[0]+bbox[2])//2))

    im, lb = im.rotate(rotate_ , center=center), lb.rotate(rotate_ , center=center)
    np_lb = np.array(lb)
    x_s = sorted(np.where(np.mean(np_lb, 2)>1)[0])
    y_s = sorted(np.where(np.mean(np_lb, 2)>1)[1])
    if len(y_s)==0 or len(x_s)==0:
        return im, lb
    new_bbox = y_s[0]-2, x_s[0]-2, y_s[-1]+2,  x_s[-1]+2 
    im, lb = im.crop(new_bbox), lb.crop(new_bbox)
    result_im, result_lb = Image.new(im.mode, output_size, color), Image.new(lb.mode, output_size, color)
    left_top = int((output_size[0]-new_bbox[2]+new_bbox[0])//2), int((output_size[1]-new_bbox[3]+new_bbox[1])//2)
    result_im.paste(im, left_top)
    result_lb.paste(lb, left_top)
    return result_im, result_lb

def print_bar(title, now_cnt, max_cnt, view_cnt=20):
    if now_cnt == 0 :
        print("{} : {} start ".format(title, max_cnt), end="")
    elif now_cnt == max_cnt//2:
        print("5" , end="")
    elif now_cnt%(max_cnt//view_cnt)==0:
        print("-" , end="")
    elif now_cnt == max_cnt-1:
        print("> end")
    sys.stdout.flush()


def main(img_dir_path, label_dir_path,json_dir_path, image_ext, lead_name,output_img_dir_path, output_label_dir_path, output_size, aug_rotate):
    os.makedirs(output_img_dir_path, exist_ok=True)
    os.makedirs(output_label_dir_path, exist_ok=True)
    skip_files = []
    basenames = get_basenames(img_dir_path, label_dir_path, json_dir_path, image_ext)
    for _i in range(len(basenames)):
        b_name = basenames[_i]
        bbox = get_bbox(json_dir_path,b_name, lead_name)
        if max(bbox) < 1: 
            skip_files.append([b_name, lead_name,bbox])
            continue
        im = Image.open(os.path.join(img_dir_path, b_name+image_ext))
        lb = Image.open(os.path.join(label_dir_path, b_name+image_ext))
        lb = swap_black_and_white(lb, bbox)
        im,lb = augmentation(im, lb, bbox, aug_rotate, output_size)
        if im.size != output_size:
            print(b_name)
            skip_files.append([b_name, lead_name,bbox])
        else:
            im.save(os.path.join(output_img_dir_path, b_name+lead_name+image_ext))
            lb.save(os.path.join(output_label_dir_path, b_name+lead_name+image_ext))
        print_bar(lead_name, _i, len(basenames))
    print(skip_files)


if __name__ == "main":
    main(IMAGES_DIR_PATH, LABELS_DIR_PATH, JSON_DIR_PATH,
        IMAGE_EXT, LEAD_NAME, 
        OUTPUT_IMAGES_DIR_PATH, OUTPUT_LABELS_DIR_PATH, OUTPUT_SIZE,
        AUG_ROUTATE)    
