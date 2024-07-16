import json
import os
import glob

ROOT_PATH = "" # Root_path, makedir labels
JSON_DIR_PATH = "" # absolute path where json file exists
NAMES = {"lead":0,
         "I_text":1,"II_text":2,"III_text":3,"aVF_text":4,"aVR_text":5,"aVL_text":6,
         "V1_text":7,"V2_text":8,"V3_text":9,"V4_text":10,"V5_text":11,"V6_text":12}  # names list

def clip(x, _min, _max):
    return min(max(_min,x), _max)

def convert_label(x_min, y_min, x_max, y_max, width, height):
    # x_min, y_min, x_max, y_max: bbox
    # width: image_width, height: image height
    x_min, x_max = clip(x_min, 0, width), clip(x_max, 0, width)
    y_min, y_max = clip(y_min, 0, height), clip(y_max, 0, height)
    x1, y1 =  (x_max+x_min)/(2*width), (y_max+y_min)/(2*height) # bbox centor
    x2, y2 = (x_max - x_min)/width, (y_max - y_min)/ height     # bbox width, height
    return x1, y1, x2, y2


def convert_yolo(json_path,label_path, names:dict):
    with open(json_path, "r") as f:
        json_load = json.load(f)
    width, height = json_load["width"],json_load["height"]
    write_list = []

    for lead in json_load["leads"]:
        name_format = lead["lead_name"]+ "_{}"
        for _type in ["text","lead"]:
            x_min, y_min, x_max, y_max = lead[_type+"_bounding_box"]["0"] + lead[_type+"_bounding_box"]["2"]
            x1, y1, x2, y2 = convert_label(x_min,y_min, x_max, y_max, width, height)
            name_key = name_format.format(_type) if _type == "text" else _type
            name_v = names[name_key]
            write_list.append("{} {} {} {} {}".format(name_v, x1, y1, x2, y2))

    with open(label_path ,"w") as f:
        write_list.append("\n")
        f.write("\n".join(write_list))


def main(root_path, json_dir_path, names):
    json_paths = glob.glob(os.path.join(json_dir_path,'*.json'))
    label_dir_path = os.path.join(root_path,"labels/{}")
    print(len(json_paths))
    for j_p in json_paths:
        file_name = os.path.basename(j_p)
        id = file_name[:file_name.rfind(".")]
        label_path = label_dir_path.format(id+".txt")
        convert_yolo(j_p, label_path, names)
        
main(ROOT_PATH,JSON_DIR_PATH, NAMES)
