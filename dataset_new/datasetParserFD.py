import os
import requests
import cv2 as cv


def printRectangles(maxImgs):

    metadata = open('dataset_new\list_bbox_celeba.txt', 'r')
    metadata.readline()
    metadata.readline()

    line = ""

    j = 1

    while line is not None and j < maxImgs:

        line = metadata.readline()

        img, x, y, w, h = line.split()

        x = int(x)
        y = int(y)
        w = int(w)
        h = int(h)

        image = cv.imread("dataset_new\\images\\" + img)

        cv.rectangle(image, (x, y),(x + w, y + h), (0, 255, 0), 2)

        cv.imshow(img, image)
        k = cv.waitKey(0) 

        j += 1


def main():

    printRectangles(100)
    

if __name__ == "__main__":
    main()