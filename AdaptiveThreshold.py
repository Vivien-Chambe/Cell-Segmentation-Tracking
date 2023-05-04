import cv2 as cv
import sys
from matplotlib import pyplot as plt
import numpy as np

img = cv.imread(r'images/puit03/t000.tif', cv.IMREAD_GRAYSCALE)
if img is None:
    sys.exit("Could not read the image.")
blurred_img = cv.GaussianBlur(img,(5,5),0)
cv.imshow('Blurred image', blurred_img)

binary_img = cv.adaptiveThreshold(blurred_img, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV, 11, 2)

cv.imshow('Adaptive threshold', binary_img)
cv.waitKey(0)

"""
kernel = np.ones((5,5), np.uint8)
img_dilate = cv.dilate(binary_img, kernel, iterations=1)
img_erosion = cv.erode(img_dilate, kernel, iterations=1)
cv.imshow('Dilation/Erosion', img_erosion)


closing = cv.morphologyEx(binary_img, cv.MORPH_CLOSE, kernel)
opening = cv.morphologyEx(closing, cv.MORPH_OPEN, kernel)

cv.imshow('Opening/Closing', opening)

cv.imshow('Binary image', binary_img)
cv.waitKey(0)
"""
"""
ret, th1 = cv.threshold(img, 127, 255, cv.THRESH_BINARY)
th2 = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)
th3 = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
titles = ['Original', 'Threshold', 'Adaptive mean threshold', 'Adaptive gaussian threshold']

images = [img, th1, th2, th3]

for i in xrange(4):
    plt.subplot(2,2,i+1),plt.imshow(images[i],'gray')
    plt.title(titles[i])
    plt.xticks([]),plt.yticks([])
plt.show()
"""