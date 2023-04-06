import numpy as np
import cv2 as cv
import os

def display_pic(folder):
    paths=([x for x in os.walk(folder)])

    for i in paths:
        i[2].sort()
        for filename in i[2]:
                path=i[0]+"/"+filename
                print(path)
                a=cv.imread(path)
                cv.imshow(path,a)
                cv.waitKey(1000)
                cv.destroyAllWindows()

display_pic("images")