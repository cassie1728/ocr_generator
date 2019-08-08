import os
from utils import rotate_and_crop_img, get_rotated_rect, convert_punctuation_ch2eng
import cv2
from multiprocessing import Pool
import sys

#root_path = sys.argv[1]
root_path = './'
TYPE = "normal" # unvalid, vertical, normal

bbox_label = os.path.join(root_path, "%s_bbox.txt" %TYPE)
save_dir = os.path.join(root_path, "%s_titles/" %TYPE)
label_file = os.path.join(root_path, "%s_titles_label.txt" %TYPE)

if TYPE == "normal":
    label_file = os.path.join(root_path, "titles_label.txt")
    save_dir = os.path.join(root_path, "titles/")

os.system("rm -rf %s; mkdir %s" %(save_dir, save_dir))

def process(line):
    words = line.strip("\n").split("\t")
    file_name = words[0]
    file_path = os.path.join('/data/zhangjiaxuan/ali/image_train_fi/', file_name)
    src_img = cv2.imread(file_path, 1)
    if src_img is None:
        print "Unvalid image:", file_path
        return

    for i in range(1, len(words)-1, 2):
        bbox = words[i]
        label = words[i+1]

        rect = get_rotated_rect(bbox)
        cropped_img = rotate_and_crop_img(src_img, rect)
        save_path = save_dir + file_name[:-4] + "_%02d.jpg" %(i/2)
        cv2.imwrite(save_path, cropped_img)

def generate_titles_label(bbox_file):
    with open(bbox_file, 'r') as f_box, open(label_file, 'w') as f:
        for line in f_box.readlines():
            words = line.strip("\n").split("\t")
            file_name = words[0]

            for i in range(1, len(words)-1, 2):
                save_name = file_name[:-4] + "_%02d.jpg" %(i/2)

                f.write(save_name + "\t" + convert_punctuation_ch2eng(words[i+1]) + "\n")

if __name__ == "__main__":
    with open(bbox_label, 'r') as f:
        lines = f.readlines()

        MP = True
        if MP == False:
            for line in lines:
                process(line)
        else:
            pool = Pool(processes=10)
            pool.map_async(process, lines)
            pool.close()
            pool.join()

        generate_titles_label(bbox_label)
    print("Finished!")
