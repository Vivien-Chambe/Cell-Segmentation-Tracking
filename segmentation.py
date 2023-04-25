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


def matrix_to_list(matrix):
  matrix_list = []
  for i in range(matrix.shape[0]):
    for j in range(matrix.shape[1]):
      if((matrix[i,j] != -1) and (matrix[i,j] != 10)):
        if(matrix[i,j] not in matrix_list):
          matrix_list.append(matrix[i,j])
  return matrix_list



def detection_newcents(img,nb_it):
  # On cree un kernel pour les erosions
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

  # On commence nos nouveaux labels à nblabels2+1 pour des raisons evidentes
  new_label = nblabel + 1

  # Je récupère les labels des centroids detecte dans image erodee
  # attention les centroids sont des couples de floats
  centroids2_int = centroids2.astype(int)
  labels_cents = [labels[i,j] for (i,j) in centroids2_int]
  
  # Je recupere les labels presentant 2 centroides ou plus
  labels_uniq, nb_cents = np.unique(labels_cents,return_counts=True)
  
  labels_doubles = labels_uniq[nb_cents>1]

  # Je récupère les centroïdes ... 
  # Je modifie labels avec la méthode des milieux
  
  for label_act in labels_doubles:
     
    indices_labels = np.where(labels_cents == label_act)[0]
    new_centroids = [centroids2_int[id] for id in indices_labels]
    cent1 = new_centroids[0]
    cent2 = new_centroids[1]

    if (len(new_centroids)==2):
      milieu = ((cent1[0] + cent2[0])/2,(cent1[1] + cent2[1])/2)

      pix_mm_labels = np.where(labels == label_act)

      for i,j in zip(pix_mm_labels[0], pix_mm_labels[1]):
          # Si mes cellules sont alignees horizontalement
          if (cent1[0] == cent2[0] ):
            if ( i > milieu[0]):
              # Je change le label de ma deuxieme cellule
              labels[i,j] = new_label

          # Si mes cellules sont alignees verticalement
          elif ( cent1[1] == cent2[1] ):
            # Je change le label de ma deuxieme cellule
            if ( j > milieu[j]):
              labels[i,j] = new_label

          # Si mes cellules sont alignees diagonalement
          # cas ou le deuxieme centroid est en bas a droite
          elif ( (cent1[0] < cent1[0]) and (cent1[1] < cent2[1]) ):
            # Je change le label de ma deuxieme cellule
            if ( (i > milieu[0]) and (j > milieu[1])):
              labels[i,j] = new_label

          # Si mes cellules sont alignees diagonalement
          # cas ou le deuxieme centroid est en bas a gauche
          elif ( (cent1[0] < cent2[0]) and (cent1[1] > cent2[1]) ):
            # Je change le label de ma deuxieme cellule
            if ( (i > milieu[0]) and (j < milieu[1])):
              labels[i,j] = new_label
    
    new_label+=1  

  return labels

def labeliser_mask (img):
    (nblabel, labels, stats, centroids)= cv.connectedComponentsWithStats(img) # On veut récupérer le nombre de cellules, les labels, les stats et les centroides
    print("Nombre de cellules : ", len(centroids) - 1)
    # cv.imshow("tresh",img)
    # # Convertir labels en image
    # labels2 = detection_newcents(img,5)
    # labels2 = labels2.astype(np.uint8)
    # labels2 = cv.cvtColor(labels2, cv.COLOR_GRAY2BGR)
    # ret,labels2 = cv.threshold(labels2, 0, 255, cv.THRESH_BINARY)
    # cv.imshow("Labels", labels2)
    # cv.waitKey(0)
    # cv.destroyAllWindows()

    # (nblabel, labels, stats, centroids)= cv.connectedComponentsWithStats(labels2) # On veut récupérer le nombre de cellules, les labels, les stats et les centroides


    ## On veut afficher les centroides sur l'image
    # On veut garder une trace des cellules et de leurs stats
    cells = []
    for i in range(1, nblabel):
        cells.append(Cell(i, centroids[i][0],centroids[i][1], stats[i][4]))
    return cells
