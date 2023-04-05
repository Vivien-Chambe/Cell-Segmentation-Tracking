import cv2 as cv
import scipy as sp
from scipy.ndimage import maximum_filter

img = cv.imread("images/puit02/t000.tif")

img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

img_norm = cv.normalize(img_gray, None, 0, 255, cv.NORM_MINMAX)

# using L2 distance and use the percise mask
cv.distanceTransform(img_norm, distanceType=2, maskSize=0)

# empirically set neighborhood_size to 20
neighborhood_size = 2
maximum_filter(img_norm, neighborhood_size) # ca marche passsssssssssssssssssssss

cv.imshow('Je suis l\'image avec les centroïdes',img_norm)

cv.waitKey(0)
