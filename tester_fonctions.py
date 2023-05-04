import numpy as np
import cv2 as cv
import sys
from matplotlib import pyplot as plt

path = 'images/puit02/t004.tif'
img = cv.imread(path, cv.IMREAD_GRAYSCALE)
if img is None:
    sys.exit("Could not read the image.")
#window_name = 'Display window'
blurred_img = cv.GaussianBlur(img,(11,11),0)
th2=cv.adaptiveThreshold(blurred_img,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY_INV,11,1)
th3=cv.adaptiveThreshold(blurred_img,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY_INV,11,8)

kernel = cv.getStructuringElement(cv.MORPH_RECT, (5,5))
closed = cv.morphologyEx(th2, cv.MORPH_CLOSE, kernel)

images = [img,blurred_img,th2,th3]
for i in range(4):
    plt.subplot(2,2,i+1),
    plt.imshow( images[i],'gray')
    plt.xticks([]),plt.yticks([])
plt.show()