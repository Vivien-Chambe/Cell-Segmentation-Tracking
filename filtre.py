import numpy as np
import cv2 as cv
import sys

path = r'Images3/puit03_t000.tif'
img = cv.imread(path)
if img is None:
    sys.exit("Could not read the image.")
window_name = 'Display window'
cv.imshow(window_name, img)
cv.waitKey(0)
cv.destroyAllWindows()