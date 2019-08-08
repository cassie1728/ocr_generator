import os
import sys
from PIL import Image

from utils import get_rotated_rect, convert_punctuation_ch2eng

#root_path = sys.argv[1]
root_path = './'
print root_path

BBOX_LABEL = os.path.join(root_path, 'rect_label.txt')
UNVALID_BBOX = os.path.join(root_path, './unvalid_bbox.txt')
VERTICAL_BBOX = os.path.join(root_path, "./vertical_bbox.txt")
NORMAL_BBOX = os.path.join(root_path, './normal_bbox.txt')
LONG_STR = os.path.join(root_path, "./long_str.txt")
HEIGHT_MIN_THRES = 5 # Attention! The value is according to the task. 

def is_vertical(bbox):
    rect = get_rotated_rect(bbox)
    if rect is None:
        return 1

    (w, h) = rect[1]
    angle = rect[2]

    if angle >= -90.0 and angle <= -45.0:
        tmp = w
        w = h
        h = tmp

    if h < HEIGHT_MIN_THRES:
        return 1
    elif h*1.0/w > 2.0:
        return 2
    else:
        return 0

def filter_bbox_label():
    with open(os.path.join(root_path, "train_label_fi.txt"), 'r') as f, open(UNVALID_BBOX, 'w') as f_unvalid, open(VERTICAL_BBOX, 'w') as f_vertical, open(NORMAL_BBOX, 'w') as f_normal, open(LONG_STR, 'w') as f_long:
        for line in f.readlines():
            words = line.strip("\r\n").strip("\n").split("\t")
            words_len = len(words)
            if words_len < 3 or (words_len%2 != 1):
                print("Warn: unvalid line! [%s]" %line)
                continue
            file_name = words[0]

            unvalid_str = file_name
            vertical_str = file_name
            normal_str = file_name
            long_str = file_name

            for i in range(1, words_len, 2):
                BBOX_TYPE = 0   # 0: normal bbox; 1: unvalid bbox; 2: vertical bbox; 3: long label(>= 60)
                bbox = words[i]
                label = words[i+1].decode("utf-8")
                if label == "":
                    print "Warn:label is empty!", file_name, bbox
                    continue
                label = convert_punctuation_ch2eng(label)

                if "##" in label:
                    BBOX_TYPE = 1
                else:
                    BBOX_TYPE = is_vertical(bbox)

                # If the length of label is bigger than 60, it's too long for ocr model, set the type to 3
                if len(label) >= 60:
                    BBOX_TYPE = 3

                if BBOX_TYPE == 0:
                    normal_str += ("\t" + bbox + "\t" + label)
                elif BBOX_TYPE == 1:
                    unvalid_str += ("\t" + bbox + "\t" + label)
                elif BBOX_TYPE == 2:
                    vertical_str += ("\t" + bbox + "\t" + label)
                elif BBOX_TYPE == 3:
                    long_str += ("\t" + bbox + "\t" + label)
            
            if unvalid_str != file_name:
                f_unvalid.write(unvalid_str + "\n")
            if vertical_str != file_name:
                f_vertical.write(vertical_str + "\n")
            if normal_str != file_name:
                f_normal.write(normal_str + "\n")
            if long_str != file_name:
                f_long.write(long_str + "\n")

if __name__ == "__main__":
    filter_bbox_label()
