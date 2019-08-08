#encoding=utf-8
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import numpy as np
import cv2

def convert_coords_to_points(bbox):
    points = []
    if isinstance(bbox, str):
        bbox = bbox.split(",")
        coors = map(int, bbox)
    else:
        coors = bbox
    
    for i in range(0, len(coors)-1, 2):
        points.append([coors[i], coors[i+1]])

    points = np.array(points)
    return points

def get_rotated_rect(bbox):
    try:
        points = convert_coords_to_points(bbox)

        rect = cv2.minAreaRect(points)
    except Exception as e:
        print str(e)
        return None
    
    return rect

def rotate_and_crop_img(src_img, rect):
    try:
        (w,h) = rect[1]
        angle = rect[2]

        rotated = False
        if angle < -45.0:
            angle += 90
            rotated = True
        
        box = cv2.boxPoints(rect)
        Xs = [i[0] for i in box]
        Ys = [i[1] for i in box]
        x1 = min(Xs)
        x2 = max(Xs)
        y1 = min(Ys)
        y2 = max(Ys)
        center = (int((x1+x2)/2), int((y1+y2)/2))
        size = (int(x2-x1), int(y2-y1))

        M = cv2.getRotationMatrix2D((size[0]/2, size[1]/2), angle, 1.0)

        cropped = cv2.getRectSubPix(src_img, size, center)
        cropped = cv2.warpAffine(cropped, M, size)

        croppedW = w if not rotated else h
        croppedH = h if not rotated else w

        croppedRotated = cv2.getRectSubPix(cropped, (int(croppedW), int(croppedH)), (size[0]/2, size[1]/2))
    except Exception as e:
        print str(e)
        return None
    
    return croppedRotated

def convert_punctuation_ch2eng(src_str):
    dst_str = ""
    punct_dict = {}
    confuse_path = "./confuse.txt"
    with open(confuse_path, 'r') as f:
        for line in f.readlines():
            line = line.strip("\r\n").strip("\n").decode("utf-8")
            words = line.split(" ")
            punct_dict[words[0]] = words[1]
    for char in src_str:
        if char in punct_dict:
            dst_str += punct_dict[char]
        else:
            dst_str += char

    return dst_str


if __name__ == "__main__":
    # Test...
    # gt_024281.jpg   46,604,86,605,87,617,45,618 garoen  42,627,85,627,84,726,43,726 美甲
    img = "./images/gt_024281.jpg"
    bboxes = ["46,604,86,605,87,617,45,618", "42,627,85,627,84,726,43,726"]

    for bbox in bboxes:
        rect = get_rotated_rect(bbox)
        print type(rect)
        print rect

        box = cv2.boxPoints(rect)
        box = np.int0(box)

        print box
