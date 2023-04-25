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
  kernel = np.ones((5,5),np.uint8)
  output= cv.connectedComponentsWithStats(img)
  (nblabel, labels, stats, centroids) = output
  
  # On effectue nb_it erosions sur l'image
  img_erod = cv.erode(img,kernel,iterations = 1)
  for i in range(2,nb_it):
    img_erod = cv.erode(img_erod,kernel,iterations = i)
    output= cv.connectedComponentsWithStats(img_erod)

  # On recupere les stats de l'image erodee  
  (nblabel2, labels2, stats2, centroids2) = output
  label_list = matrix_to_list(labels2)
  # On commence nos nouveaux labels à nblabels2+1 pour des raisons evidentes
  new_label = nblabel + 1

  # On utilise np.where pour determiner les indices des pixels de meme labels
  # Pour chaque labels de l'image errodée
  for label_act in label_list: 
    # Je me créé un compteur de centroids et deux listes de centroids
    nb_cent = 0  
    mes_cents = []
    mes_cents_fin = []
    # Je recupere les indices de tous les pixels contenant le meme label
    pix_mm_labels = np.where(labels == label_act)
    
    # Pour chaque centroids dans l'image erodee
    for cent in centroids2:
      # Si il appartient a ma liste des pixels de meme labels
      if ( (int(cent[0]) in pix_mm_labels[0]) and (int(cent[1]) in pix_mm_labels[1]) ):
        # J'incrémente mon compteur
        nb_cent += 1
        mes_cents.append((int(cent[0]),int(cent[1])))
    
      # Si j'ai trouvé 2 centroids 
      # Je modifie ma matrice avec la methode du milieu
      if (nb_cent == 2):
        mes_cents_fin.append(mes_cents[0])
        mes_cents_fin.append(mes_cents[1])
        milieu = ((mes_cents[0][0] + mes_cents[0][1])/2,(mes_cents[1][0] + mes_cents[1][1])/2)
        for i in pix_mm_labels[0]:
          for j in pix_mm_labels[1]:

            # Si mes cellules sont alignees horizontalement
            if ( mes_cents[0][0] == mes_cents[1][0] ):
              if ( i > milieu[0]):
                # Je change le label de ma deuxieme cellule
                labels[i,j] = new_label

            # Si mes cellules sont alignees verticalement
            elif ( mes_cents[0][1] == mes_cents[1][1] ):
              # Je change le label de ma deuxieme cellule
              if ( j > milieu[j]):
                labels[i,j] = new_label

            # Si mes cellules sont alignees diagonalement
            # cas ou le deuxieme centroid est en bas a droite
            elif ( (mes_cents[0][0] < mes_cents[1][0]) and (mes_cents[0][1] < mes_cents[1][1]) ):
              # Je change le label de ma deuxieme cellule
              if ( (i > milieu[0]) and (j > milieu[1])):
                labels[i,j] = new_label

            # Si mes cellules sont alignees diagonalement
            # cas ou le deuxieme centroid est en bas a gauche
            elif ( (mes_cents[0][0] < mes_cents[1][0]) and (mes_cents[0][1] > mes_cents[1][1]) ):
              # Je change le label de ma deuxieme cellule
              if ( (i > milieu[0]) and (j < milieu[1])):
                labels[i,j] = new_label
      else :
        mes_cents_fin.append(cent)


    new_label+=1
    pix_mm_labels = []
  
  return mes_cents_fin,labels
def labeliser_mask (img):
    (nblabel, labels, stats, centroids)= cv.connectedComponentsWithStats(img) # On veut récupérer le nombre de cellules, les labels, les stats et les centroides
    # print("Nombre de cellules : ", len(centroids) - 1)
    # centroids,labels = detection_newcents(img,3)
    # print("Nombre de cellules après correction : ", len(centroids) - 1)


    ## On veut afficher les centroides sur l'image
    # On veut garder une trace des cellules et de leurs stats
    cells = []
    for i in range(1, nblabel):
        cells.append(Cell(i, centroids[i][0],centroids[i][1], stats[i][4]))
    return cells
