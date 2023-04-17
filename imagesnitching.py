import numpy as np
import cv2 as cv
import os

def display_pic(folder,time=-1):
    """Affiche toutes les images d'un dossier et de ses sous dossiers"""
    paths=([x for x in os.walk(folder)])

    for i in paths:
        i[2].sort()
        for filename in i[2]:
                split=filename.split(".")
                if (split[-1]=="tif"):
                    path=i[0]+"/"+filename
                    print(path)
                    a=cv.imread(path)
                    cv.imshow(path,a)
                    cv.waitKey(time)
                    cv.destroyAllWindows()


display_pic("images/puit03")