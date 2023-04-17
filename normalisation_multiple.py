import numpy as np
import cv2 as cv
import os

def normalize_pic(folder):
    paths=([x for x in os.walk(folder)])
    print(paths)

    for i in paths:
        i[2].sort()
        for filename in i[2]:
                #path=i[0]+"/"+filename
                #print(path)
                img=cv.imread(filename)
                cv.imshow(filename,img)
                img_normalized = cv.normalize(img, None, 0, 255, cv.NORM_MINMAX)
                cv.imwrite('../puit02_clean/'+filename,img_normalized)
                #cv.imshow('puit02_clean/'+filename,img_normalized)
                cv.waitKey(1000)
                cv.destroyAllWindows()


normalize_pic("images/puit02")
