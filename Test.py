import cv2 as cv
import numpy as np
import scipy as sp
from scipy.ndimage import maximum_filter
from skimage import color

# Normalisation de l'image + grayscale
img = cv.imread("images/puit02/t000.tif")

img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

#cv.imshow('Avant normalisation:',img_gray)

img_norm = cv.normalize(img_gray, None, 0, 255, cv.NORM_MINMAX)

#cv.imshow('Apres normalisation:',img_norm)

# Binarisation

ret, img_bin = cv.threshold( img_norm, 122,255,cv.THRESH_BINARY+cv.THRESH_OTSU)

#cv.imshow('Apres binarisation:',img_bin)

# enlever les bruits dès le debut....

kernel = np.ones((5,5),np.uint8)
img_open = cv.morphologyEx(img_bin,cv.MORPH_OPEN,kernel,iterations=1)

# skimage....
#img_open = sp.clear_border(img_open)

#cv.imshow('Apres opening (- bruits):',img_open)

# on a des trous dans certaines cellules...
# retirons les 

# on utilise d'abord dilate
img_bg = cv.dilate(img_open,np.ones((5,5),np.uint8),iterations = 1)

#cv.imshow('Apres dilation:',img_bg)

# "separation"

img_transform = cv.distanceTransform(img_open,cv.DIST_L2,5)

#cv.imshow('Apres dist transform:',img_transform)
 
ret, img_fg = cv.threshold(img_transform,0.5*img_transform.max(),255,0)

#cv.imshow('Apres separation:',img_fg)

# on a notre foreground et notre background
# on peut determiner les régions ambigues en calculant
img_fg = np.uint8(img_fg)
img_ambigu = cv.subtract(img_bg,img_fg) 

cv.imshow('regions ambigues:',img_ambigu)

# labelisation 
# on utilise connectecComponents qui label un groupe de pixel
# en fct leur connectivité cad meme intensité et contigus

ret, markers = cv.connectedComponents(img_fg)
#cv.imshow('markers:',markers)
markers = markers + 10

markers[img_ambigu==255] = 0

markers = cv.watershed(img,markers)

img[markers==-1]=[0,255,255]

img_fin = color.label2rgb(markers,bg_label=0)

cv.imshow('RESULTAT FINAL ',img_fin)

cv.waitKey(0)

# Labellisation / recherche des centroïdes
## Il nous faut tout  d'abord les centroïdes de chaque cell
## centroïdes = moyenne arithmetique de tous les points de la cell
## = moyenne pondérée de tous les pixels constituant la cell.

#cv.distanceTransform(img_norm, distanceType=2, maskSize=0)

# On calcule les moments de l'image
# moments d'une image = généralement des descripteurs de forme
# -> on les utilise pour obtenir des caractéristiques globale d'une forme

moments = cv.moments(img_bin)

print(moments)

# empirically set neighborhood_size to 20
#neighborhood_size = 2
#maximum_filter(img_norm, neighborhood_size) # ca marche passsssssssssssssssssssss

#cv.imshow('Je suis l\'image avec les centroïdes',img_norm)

#cv.waitKey(0)
