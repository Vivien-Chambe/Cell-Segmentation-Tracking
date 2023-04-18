import textwrap
import cv2 as cv
import numpy as np
import scipy as sp
from scipy.ndimage import maximum_filter
from skimage import color

# Lecture de l'image + grayscale au cas où
img = cv.imread("images/puit02/t000.tif")

img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# Affichage si besoin
#cv.imshow('Avant normalisation:',img_gray)

# Normalisation de l'image 
img_norm = cv.normalize(img_gray, None, 0, 255, cv.NORM_MINMAX)

# Affichage si besoin
#cv.imshow('Apres normalisation:',img_norm)

# Binarisation ret = valeur du threshold
ret, img_bin = cv.threshold( img_norm, 122,255,cv.THRESH_BINARY+cv.THRESH_OTSU)

# Affichage si besoin
#cv.imshow('Apres binarisation:',img_bin)

# On enleve les bruits dès le debut avec l'opening
kernel = np.ones((5,5),np.uint8)
img_open = cv.morphologyEx(img_bin,cv.MORPH_OPEN,kernel,iterations=1)

# On peut retirer les cellules qui se trouvent au bord de
# l'image avec clear_border mais ce n'est pas ce qui est 
# attendu (?)
#img_open = sp.clear_border(img_open)

# Affichage si besoin
#cv.imshow('Apres opening (- bruits):',img_open)

# On a des trous dans certaines cellules
# On les retire avec la fonction dilate 
img_bg = cv.dilate(img_open,kernel,iterations = 1)

# On appelle l'image obtenu, plus précisément les pixels noirs
# le fond (background) on verra pourquoi dans la suite

# Affichage si besoin
cv.imshow('Apres dilation:',img_bg)

# On veut ensuite
# on utilise distanceTransform qui calcule la distance entre 
# chaque pixel et le pixel non nul le plus proche
# en gros c'est une maniere d'acceder au centre
img_transform = cv.distanceTransform(img_open,cv.DIST_L2,5)

# Affichage si besoin
#cv.imshow('Apres dist transform:',img_transform)
 
# On détermine ensuite le premier plan (foreground) cad nos cellules 
# a l'aide de notre img_transform
# Pour cela on appelle threshold encore une fois
# "comparé au pixel d'intensité max au centre on prend que les pixel > 50% de cette intensité"
# -> cela forme nos cellules 

ret, img_fg = cv.threshold(img_transform,0.40*img_transform.max(),255,0) 
# SOLUTION DU PROBLEME (1)
# ? on perd une cellule... Peut etre que c'est pcq on avance trop dans le img_transform 
# on passe de 0.5 -> 0.40 -> C'EST BON
# on pourrait utiliser erode mais on perdrait trop d'information...

# Affichage si besoin
cv.imshow('Apres separation:',img_fg)

# SOLUTION DU PROBLEME (2)
img_fg = cv.dilate(img_fg,kernel,iterations = 1)
# Pb peut être du au fait que le sure fg de la cellule divisee en deux n'est pas convexe 
# Du coup on dilate -> CA MARCHEEEEEEEEEEEEE 

# On a notre foreground et notre background

# On peut determiner les régions ambigues 
# cad les zones où l'on est pas sûre d'etre sur une cellule
# où sur le fond
img_fg = np.uint8(img_fg) # on cast le foreground car contient des float
# Les zones ambigues sont la soustractions dedu fond et du premier plan
img_ambigu = cv.subtract(img_bg,img_fg) 

# Affichage si besoin
cv.imshow('regions ambigues:',img_ambigu)

# Labelisation 
# On utilise connectecComponentswithStats qui associe a un groupe de pixel
# une intensité de gris en fct leur connectivité (cad meme intensité et contigus)
# Grace à elle on récupère les coordonnées du centre de ces composantes
# soient nos cellules
output= cv.connectedComponentsWithStats(img_fg)
(nblabel, labels, stats, centroids) = output

# Pas sûre de la valeur de chaque val de retour
# nblabels = nb de differents labels
# Mais les centroids sont la dernière valeur de retour
# et labels correspond aux couleurs associé aux composantes
# (cellules)

# Affichage si besoin
#print(nblabel)
#print(labels)
#print(stats)
# ptit print des centroids...
#print(centroids)

# Petit problème le background est d'intensité 0
# Or on veut que seulement nos zônes ambigues soient d'intensite 0
# (pour la fonction watershed cf suite)
# On augmente donc toutes les intensité de 10 par ex 
labels = labels + 10

# On associe nos region ambigue a l'intensité 0
labels[img_ambigu==255] = 0

# Enfin on appelle watershed
# qui va nous permettre de segmenter nos cellules 
# plus particulièrement celles qui se touchent
labels = cv.watershed(img,labels)

# watershed associe -1 aux bords...
# On peut changer ca en lui associant du jaune parn exemple
img[labels==-1]=[255,255,0]

# On converti les labels de notre image en couleurs rgb 
img_fin = color.label2rgb(labels,bg_label=0)

cv.imshow('RESULTAT FINAL ',img_fin)

# Je vois pas quoi changer... on perd une cellule (1) et une des cellules detectees
# et consideree comme deux cellules (2) GSJGUOUZAGBOUBGOU  
# -> probleme (1) reglé cf ligne 64 à 66
# -> probleme (2) reglé cf ligne 71 à 74

# Essai avec les Bounding Box avec SelectRois
# CA MARCHE PAAAAAAAAAAAAAAAASSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
# -> On fait à la main ca marche ? cf dernier plot

print(centroids)
print(labels[10,10])

height = img_fin.shape[0]
width = img_fin.shape[1]
print(height,width)
w_bb = stats[labels[10,10],cv.CC_STAT_WIDTH]
print(w_bb)
h_bb = stats[labels[10,10],cv.CC_STAT_HEIGHT]
print(h_bb)

cent_cell = centroids[10]

x = int(cent_cell[0]-1.5*w_bb)
y = int(cent_cell[0]+1.5*w_bb)
z = int(cent_cell[1]-1.5*h_bb)
t = int(cent_cell[1]+1.5*h_bb)

cv.rectangle(img_fin, (x, z), (y, t), (255,255,255), 2)

#cropped = img[x:y,z:t]

cv.imshow('avec une bb normalement',img_fin)

#hold window
cv.waitKey(0)

