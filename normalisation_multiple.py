import numpy as np
import cv2 as cv
import os

# les photos cleans ne sont pas ajoutées au repertoire puitclean
# A revoir

def normalize_pic(folder):
    paths=([x for x in os.walk(folder)])
    #print(paths)

    for i in paths:
        i[2].sort()
        for filename in i[2]:
            path=i[0]+"/"+filename
            path_out=i[0]+"_clean/"
            print(path)
            print(filename)
            img=cv.imread(path)
            #cv.imshow(filename,img)
            img_normalized = cv.normalize(img, None, 0, 255, cv.NORM_MINMAX)
            cv.imwrite(path_out+filename,img_normalized)
            #cv.imshow(path_out+filename,img_normalized)
            #cv.waitKey(1000)
            #cv.destroyAllWindows()


#normalize_pic("images/puit02")
normalize_pic("images/puit01")


