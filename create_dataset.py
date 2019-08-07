import os
import lmdb # install lmdb by "pip install lmdb"
#import cv2
import numpy as np
import cv2
from PIL import Image
from cStringIO import StringIO

def checkImageIsValid_pil(imageBin):
    if imageBin is None or len(imageBin) == 0:
        return False

    try:
        img_buf = StringIO()
        img_buf.write(imageBin)
        img_buf.seek(0)
        image = Image.open(img_buf)
        w,h = image.size 
        if w == 0 or h == 0:
            return False
        # ???
        resize_img = image.resize((50,50))
    except Exception as e:
        return False

    return True
def checkImageIsValid(imageBin):
    if imageBin is None:
        return False
    if len(imageBin) == 0:
        return False
    imageBuf = np.fromstring(imageBin, dtype=np.uint8)
    img = cv2.imdecode(imageBuf, cv2.IMREAD_GRAYSCALE)
    imgH, imgW = img.shape[0], img.shape[1]
    if imgH * imgW == 0:
        return False
    return True


def writeCache(env, cache):
    with env.begin(write=True) as txn:
        for k, v in cache.iteritems():
            txn.put(k, v)


def createDataset(outputPath, imagePathList, labelList, Type, lexiconList=None, checkValid=True):
    """
    Create LMDB dataset for CRNN training.

    ARGS:
        outputPath    : LMDB output path
        imagePathList : list of image path
        labelList     : list of corresponding groundtruth texts
        lexiconList   : (optional) list of lexicon lists
        checkValid    : if true, check the validity of every image
    """
    assert(len(imagePathList) == len(labelList))
    nSamples = len(imagePathList)
    env = lmdb.open(outputPath, map_size=1099511627776)
    cache = {}
    cnt = 1
    for i in xrange(nSamples):
        imagePath = imagePathList[i]
        imagePath = "./" + Type + "/" + imagePath
        label = labelList[i]
        try:
            if not os.path.exists(imagePath):
                print('%s does not exist' % imagePath)
                continue
        except:
            print "The path is not valid!", imagePath
            continue

        with open(imagePath, 'r') as f:
            imageBin = f.read()
            if checkValid:
                if not checkImageIsValid_pil(imageBin):
                    print('%s is not a valid image' % imagePath)
                    continue

        imageKey = 'image-%09d' % cnt
        labelKey = 'label-%09d' % cnt
        cache[imageKey] = imageBin
        cache[labelKey] = label
        if lexiconList:
            lexiconKey = 'lexicon-%09d' % cnt
            cache[lexiconKey] = ' '.join(lexiconList[i])
        if cnt % 1000 == 0:
            writeCache(env, cache)
            cache = {}
            print('Written %d / %d' % (cnt, nSamples))
        cnt += 1
    nSamples = cnt-1
    cache['num-samples'] = str(nSamples)
    writeCache(env, cache)
    print('Created dataset with %d samples' % nSamples)

def makeDataset(inputPath, Type):
    image_list = []
    label_list = []
    with open(inputPath, 'r') as f:
        lines = f.readlines()
        for line in lines:
            words = line.strip().split('\t')
            if len(words) != 2:
                print line
                continue
            image_file = words[0]
            label = words[1] + " " # Because of the code in the project of crnn, in utilities.lua, the function of split()
            image_list.append(image_file)
            label_list.append(label)
    return image_list, label_list

if __name__ == '__main__':
    Type = "train"
    image_list, label_list = makeDataset("./train/label.txt", Type)
    createDataset("./train_lmdb", image_list, label_list, Type, checkValid = True)

    Type = "test"
    image_list, label_list = makeDataset("./test/label.txt", Type)
    createDataset("./test_lmdb", image_list, label_list, Type, checkValid = True)
