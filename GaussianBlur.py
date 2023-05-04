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
blurred_img5 = cv.GaussianBlur(img,(5,5),0)
blurred_img9 = cv.GaussianBlur(img,(9,9),0)
cv.imshow('Original', img)
cv.imshow('Blurred ksize=5', blurred_img5)
cv.imshow('Blurred ksize=9', blurred_img9)
cv.waitKey(0)
cv.destroyAllWindows()