import os
import sys

if __name__ == "__main__":
    print "Start to merge data..."
    path = "./train"

    label_file = open("./tmp/label.txt", 'w')
    for root, dir_names, file_names in os.walk(path):
        for file_name in file_names:
            if file_name.endswith(".jpg"):
                os.system("mv " + os.path.join(root, file_name) + " ./tmp")
            else:
                f = open(os.path.join(root, file_name), 'r')
                for line in f.readlines():
                    label_file.write(line)
                f.close()
    label_file.close()

    print "Merge train finished..."

