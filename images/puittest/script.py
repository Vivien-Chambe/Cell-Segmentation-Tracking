import cv2 as cv
import numpy as np
import random as rd

# Je souhaite créer une suite de n images en noir et blanc qui représente la des ronds et qui se déplace

# On supprime les images déjà existantes
import os
import shutil
if os.path.exists("images/puittest/cell_test"):
    shutil.rmtree("images/puittest/cell_test")
os.makedirs("images/puittest/cell_test")
# Je crée une image de 1000x1000 pixels
img = np.zeros((1000, 1000), np.uint8)

# On cree une liste de coordonnées qui suit un sinus
coords1 = []
for j in range(100):
    coords1.append((j*10, int(500+200*np.sin(j/10))))

# On cree une liste de coordonnées qui suit un cosinus
coords2 = []
for j in range(100):
    coords2.append((j*10, int(500+200*np.cos(j/10))))

# Je crée une boucle qui va créer une image par itération
for i in range(100):
    # Je crée une image de 1000x1000 pixels
    img = np.zeros((1000, 1000), np.uint8)
    
    cv.circle(img, (coords1[i][0], coords1[i][1]), 50, (255, 255, 255), -1)
    cv.circle(img, (coords2[i][0], coords2[i][1]), 50, (255, 255, 255), -1)


    
    

    # Je sauvegarde l'image
    if i < 10:
        cv.imwrite("images/puittest/cell_test/img00"+str(i)+".png", img)
    elif i < 100:
        cv.imwrite("images/puittest/cell_test/img0"+str(i)+".png", img)
    else:
        cv.imwrite("images/puittest/cell_test/img"+str(i)+".png", img)