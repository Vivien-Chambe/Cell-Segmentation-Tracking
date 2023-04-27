import cv2 as cv
import numpy as np
from Classes import Cell
import math


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


def matrix_to_list(matrix):
  matrix_list = []
  for i in range(matrix.shape[0]):
    for j in range(matrix.shape[1]):
      if((matrix[i,j] != -1) and (matrix[i,j] != 10)):
        if(matrix[i,j] not in matrix_list):
          matrix_list.append(matrix[i,j])
  return matrix_list

def getPerpCoord(aX, aY, bX, bY, length):
    vX = bX-aX
    vY = bY-aY
    #print(str(vX)+" "+str(vY))
    if(vX == 0 or vY == 0):
        return 0, 0, 0, 0
    mag = math.sqrt(vX*vX + vY*vY)
    vX = vX / mag
    vY = vY / mag
    temp = vX
    vX = 0-vY
    vY = temp
    cX = bX + vX * length
    cY = bY + vY * length
    dX = bX - vX * length
    dY = bY - vY * length
    return int(cX), int(cY), int(dX), int(dY)


def detection_newcents2(img,nb_it):
  
  kernel = np.ones((5,5),np.uint8)
  output = cv.connectedComponentsWithStats(img)
  (nblabel, labels, stats, centroids) = output
  
  # On effectue nb_it erosions sur l'image
  img_erod = cv.erode(img,kernel,iterations = 1)
  for i in range(2,nb_it):
    img_erod = cv.erode(img_erod,kernel,iterations = i)
    output= cv.connectedComponentsWithStats(img_erod)

  # On recupere les stats de l'image erodee  
  (nblabel2, labels2, stats2, centroids2) = output

  # Je récupère les labels des centroids detecte dans image erodee
  # attention les centroids sont des couples de floats
  centroids2_int = centroids2.astype(int)
  labels_cents = [labels[i,j] for (i,j) in centroids2_int]
  
  # Je recupere les labels presentant 2 centroides ou plus
  labels_uniq, nb_cents = np.unique(labels_cents,return_counts=True)
  
  labels_doubles = labels_uniq[nb_cents>1]
  print(labels_doubles)
  # Je récupère les centroïdes ... 
  # Je modifie labels avec la méthode des milieux
  
  for label_act in labels_doubles:
     
    indices_labels = np.where(labels_cents == label_act)[0]
    new_centroids = [centroids2_int[id] for id in indices_labels]

    # Si je trouve 2 centroides je les recupère et je calcule la perpendiculaire en leur milieu 
    # et je la trace
    
    if (len(new_centroids)==2):      
      cent1 = new_centroids[0]
      cent2 = new_centroids[1]

      print("cent1 : "+str(cent1))
      print("cent2 : "+str(cent2))



      x1 = int(cent1[0])
      y1 = int(cent1[1])
      x2 = int(cent2[0])
      y2 = int(cent2[1])


      cv.line(img,(x1,y1),(x2,y2),(255,255,255),5)

      midX = (x1+x2)/2
      midY = (y1+y2)/2

      aX, aY, bX, bY = getPerpCoord(x1,y1,int(midX),int(midY),50)

      #tracer une ligne entre les deux cercles
      cv.line(img,(aX,aY),(bX,bY),(255,255,255),5)

  
  return img


def labeliser_mask (img):
    # cv.imshow("img",img)
    # cv.imshow("return img",detection_newcents2(img,5))
    # cv.imshow("modified img",img)

    # cv.waitKey(0)
    (nblabel, labels, stats, centroids)= cv.connectedComponentsWithStats(img) # On veut récupérer le nombre de cellules, les labels, les stats et les centroides
    #print("Nombre de cellules : ", len(centroids) - 1)
    

    ## On veut afficher les centroides sur l'image
    # On veut garder une trace des cellules et de leurs stats
    cells = []
    for i in range(1, nblabel):
        cells.append(Cell(i, centroids[i][0],centroids[i][1], stats[i][4]))
    return cells
