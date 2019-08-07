#!/usr/bin/python
#encoding=utf-8
import os
from PIL import Image
import random
from multiprocessing import Pool
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from utils import rotate_and_crop_img, get_rotated_rect
import cv2

label_dict = {}
def read_label_dict(dict_file):
    with open(dict_file, 'r') as f:
        lines = f.readlines()
        index = 1
        for line in lines:
            line = line.strip("\r\n").strip("\n").decode('utf-8')
            label_dict[line] = str(index)
            index = index + 1

def change_label(label):
    label = label.decode('utf-8')
    result = ''
    for ch in label:
        result += label_dict[ch] + ' '
    result.rstrip(' ') #删除最后一个空格
    return result

def write_label(img_file, label, Type, index, image_index, title_index):
    label_file = "./" + Type + "/label.txt"
    with open(label_file, 'a+') as f:
        try:
            new_label = change_label(label)
            if len(label.decode("utf-8")) <= 73:
                f.write(str(index) + "_" + str(image_index) + "_" + str(title_index) + "_" + img_file + "\t" + change_label(label) + '\n')
                return True
        except:
            print("Error in change_label!", label.decode('utf-8'))
            return False
    return False

def process_label(root, label_file, Type, index):
    if Type == "train":
        Type = Type + "/" + str(index)

    with open(root + "/" + label_file, 'r') as f:
        lines = f.readlines()
        print("len of label file:", len(lines))
        for image_index, line in enumerate(lines):
            #line = line.replace("：", ":")
            #line = line.replace("？", "?")
            #line = line.replace('“', '"')
            #line = line.replace("“", '"')
            #line = line.replace("（", '(')
            #line = line.replace("）", ')')
            #line = line.replace("，", ',')
            #line = line.replace("！", '!')
            words = line.strip('\n').split("\t")
            file_name = words[0]
            for i in range(1, len(words), 2):
                #str_labels = words[2].split(" ")
                #if len(str_labels) == 2:
                #    words[2] = str_labels[1]
                #if len(words) < 3:
                #    print("Warning, the line of label is not suitable. [%s]" %line)
                #    continue
                title_index = i/2
                rect_info = words[i]
                label = words[i+1]

                if len(words[2]) == 0:
                    print("Warning, the length of label is zero. [%s]" %line)
                result = write_label(file_name, label, Type, index, image_index, title_index)
                if result == True:
                    process_image_bbox(root, file_name, rect_info, Type, index, image_index, title_index)
                else:
                    print line

def process_image_bbox(root, image_file, rect_info, Type, index, image_index, title_index):
    img_path = root + "/" + image_file
    im = cv2.imread(img_path, 1)   # cv2.IMREAD_COLOR
    if im is None:
        print("Unvalid image:", img_path)
        return
    # pytorch中，如果数据集中存在一通道的灰度图像，会报错！
    #if im.mode != "RGB":
    #    return

    width, height = im.shape[:2]

    words = rect_info.split(',')
    words = map(int , words)

    # 随机扰动
    for i, word in enumerate(words):
        words[i] += random.randint(-2,5)
        if words[i] < 0: words[i] = 0

    rect = get_rotated_rect(words)

    crop_img = rotate_and_crop_img(im, rect)
    cv2.imwrite("./" + Type + "/" + str(index) + "_" + str(image_index) + "_" + str(title_index) + "_" + image_file, crop_img)

def process_image(root, image_file, rect_info, Type, index, image_index):
    img_path = root + "/" + image_file
    im = Image.open(img_path)

    # pytorch中，如果数据集中存在一通道的灰度图像，会报错！
    if im.mode != "RGB":
        return

    width, height = im.size
    words = rect_info.split(';')
    x_y_w_h = True
    if x_y_w_h == True:
        x, y = words[0].split(',')
        w, h= words[1].split(',')
    else:
        left, top = words[0].split(',')
        right, bottom = words[1].split(',')
        x = int(left)
        y = int(top)
        w = int(right) - int(left)
        h = int(bottom) - int(top)
    x = int(x)
    y = int(y)
    w = int(w)
    h = int(h)

    # SCXW's data is from label system, and the image is resized before labeled.
    SCXW = False
    if SCXW == True:
        resized_width =850
        resized_ratio = width * 1.0 / resized_width
    else:
        resized_ratio = 1.0
    x = int(x * resized_ratio)
    y = int(y*resized_ratio)
    w = int(w*resized_ratio)
    h = int(h*resized_ratio)

    left_border = random.randint(-3, 10)
    right_border = random.randint(-3,10)
    top_border = random.randint(-3,10)
    if top_border < 0:
        bottom_border = random.randint(0,10)
    else:
        bottom_border = random.randint(-3,10)
    x = x - left_border
    y = y - top_border
    w = w + left_border + right_border
    h = h + top_border + bottom_border
    if x < 0: x = 0
    if y < 0: y = 0
    if (x+w) > width -1: w = width - 1 - x
    if (y+h) > height - 1: h = height - 1 - y
    crop_im = im.crop((x, y, x+w, y+h))
    crop_im.save("./" + Type + "/" + str(index) + "_" + str(image_index) + "_" + image_file)

def process_train(index):
    cmd = "mkdir ./train/" + str(index)
    os.system(cmd)
    process_label(path, "normal_bbox.txt", "train", index)

def process_test(index):
    process_label(path, "normal_bbox.txt", "test", index)

if __name__ == "__main__":
    #read_label_dict("./words_list_5623.txt")
    read_label_dict("./words_list_ali.txt")

    path = "/data/zhangjiaxuan/ali/image_train_fi"

    multi_process = True
    if multi_process:
        pool = Pool(processes = 10)
        index = range(0, 10)
        pool.map_async(process_train, index)
        pool.close()
        pool.join()
    else:
        process_train(0)

    for i in range(1):
        process_test(i)

    print "Finished to split data..."
