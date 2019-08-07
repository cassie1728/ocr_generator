import os
from PIL import Image

label_dict = {}
def read_label_dict(dict_file):
    with open(dict_file, 'r') as f:
        lines = f.readlines()
        index = 1
        for line in lines:
            line = line.strip().decode('utf-8')
            label_dict[line] = str(index)
            index = index + 1

def change_label(label):
    label = label.decode('utf-8')
    result = ''
    for ch in label:
        result += label_dict[ch] + ' '
    result.rstrip(' ')
    return result

def write_label(img_file, label, index):
    label_file = "./" + type + "/label" + ".txt"
    with open(label_file, 'a+') as f:
        new_label = change_label(label)
        if len(label.decode('utf-8')) <= 29:
            img_name = os.path.split(img_file)[1]
            content = img_name + "\t" + new_label + "\n"
            f.write(content)
        else:
            print(label)
            print("label's length = ", len(label.decode('utf-8')))

def process_label(root, image_file, GT, index):
    write_label(image_file, GT, index)

def process_image(root, image_file, roi):
    resized_width = 850
    img_path = root + "/" + image_file
    im = Image.open(img_path)
    im_width, im_height = im.size
    words = roi.split(";")

    resized_ratio = im_width * 1.0/resized_width
    left = words[0]
    top = words[1]
    width = words[2]
    height = words[3]
    left = int(left)
    top = int(top)
    width = int(width)
    height = int(height)

    left = int(left * resized_ratio)
    top = int(top * resized_ratio)
    width = int(width * resized_ratio)
    height = int(height * resized_ratio)

    right = left + width
    bottom = top + height

    width_border = 0
    height_border = 0
    left = left - width_border
    right = right + width_border * 2
    top = top - height_border
    bottom = bottom + height_border * 2
    border = 10
    if left < border:
        left = 0
    else:
        left = left - border
    if right > im_width - border:
        right = im_width - 1
    else:
        right = right + border - 1
    crop_im = im.crop((left, top, right, bottom))
    image_name = os.path.split(image_file)[1]
    crop_im.save("./" + type + "/" + image_name)

def process(root, content_list, index):
    for content in content_list:
        name = content["name"]
        GT = content["GT"]
        roi = pos_dict[name]

        process_image(root, name, roi)
        process_label(root, name, GT, index)

def read_content(content_file):
    result_list = []

    f = open(content_file, "r")
    for content in f.readlines():
        result = {}
        words = content.replace("\n", "").split(" ")
        if len(words) != 2:
            continue

        result["name"] = words[0]
        result["GT"] = words[1]

        result_list.append(result)

    f.close()
    return result_list

def read_pos(pos_file):
    result_dict = {}

    f = open(pos_file, 'r')
    for line in f.readlines():
        words = line.replace("\n", "").split(" ")
        if len(words) != 2:
            continue

        result_dict[words[0]] = words[1]

    f.close()
    return result_dict

if __name__ == "__main__":
    read_label_dict("./word_3567.txt")

    root = "/data/heneng/images/generated/"

    type = "val"
    content_file = "content_" + type + ".txt"
    pos_file = "pos_" + type + ".txt"

    content_list = read_content(root + content_file)
    pos_dict = read_pos(root + pos_file)

    index = 0
    process(root, content_list, index)
