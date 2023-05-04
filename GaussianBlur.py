import cv2 as cv
import sys

"""
cv.GaussianBlur(src, ksize, sigmaX, sigmaY, borderType) -> dst
src : input image
dst : output image - même taille et type que src
ksize : Gaussian kernel size
sigmaX : Gaussian kernel standard deviation in X direction
sigmaY : same in Y direction
-> if sigmaY = 0, then sigmaY is the same as sigmaX
-> recommended to specify all ksize, sigmaX and sigmaY !
borderType : pixel extrapolation method (?)
"""

img = cv.imread(r'images/puit03/t000.tif')
if img is None:
    sys.exit("Could not read the image.")
blurred_img = cv.GaussianBlur(img,(5,5),0)
cv.imshow('Original', img)
cv.imshow('Blurred', blurred_img)
cv.waitKey(0)
cv.destroyAllWindows()