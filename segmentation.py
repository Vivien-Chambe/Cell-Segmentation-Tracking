import cv2 as cv
import numpy as np
from Classes import Cell

def erode (img, kernel_size = 3, iterations = 1):
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    return cv.erode(img, kernel, iterations)

def dilate (img, kernel_size = 3, iterations = 1):
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    return cv.dilate(img, kernel, iterations)

def opening (img, kernel_size = 3, iterations = 1):
    return dilate(erode(img, kernel_size, iterations), kernel_size, iterations)

def closing (img, kernel_size = 3, iterations = 1):
    return erode(dilate(img, kernel_size, iterations), kernel_size, iterations)

def labeliser_mask (img):
    (nblabel, labels, stats, centroids)= cv.connectedComponentsWithStats(img) # On veut récupérer le nombre de cellules, les labels, les stats et les centroides

    ## On veut afficher les centroides sur l'image
    # for i in range(1, nblabel):
    #     cv.circle(self.treshold, (int(centroids[i][0]), int(centroids[i][1])), 2, (0, 0, 255), -1)
    ## Mettre l'image dans le label
    #self.label.setPixmap(convert_cv_qt(self.treshold))
    # On veut garder une trace des cellules et de leurs stats
    cells = []
    for i in range(1, nblabel):
        cells.append(Cell(i, centroids[i][0],centroids[i][1], stats[i][4]))
    return cells
