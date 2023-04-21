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
#cv.imshow('Apres dilation:',img_bg)

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
#cv.imshow('Apres separation:',img_fg)

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
#cv.imshow('regions ambigues:',img_ambigu)

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

#cv.imshow('RESULTAT FINAL ',img_fin)

# Je vois pas quoi changer... on perd une cellule (1) et une des cellules detectees
# et consideree comme deux cellules (2) GSJGUOUZAGBOUBGOU  
# -> probleme (1) reglé cf ligne 64 à 66
# -> probleme (2) reglé cf ligne 71 à 74

# Essai avec les Bounding Box avec SelectRois
# CA MARCHE PAAAAAAAAAAAAAAAASSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
# -> On fait à la main ca marche ? cf dernier plot
# Changer avec un circle!!! 

#print(centroids)

def matrix_to_list(matrix):
  matrix_list = []
  for i in range(matrix.shape[0]):
    for j in range(matrix.shape[1]):
      if((matrix[i,j] != -1) and (matrix[i,j] != 10)):
        if(matrix[i,j] not in matrix_list):
          matrix_list.append(matrix[i,j])
  return matrix_list

label_list = matrix_to_list(labels)

#cv.waitKey(0) 

#print("JE SUIS LABEL",labels)
#print(len(label_list))
"""
for i in range(len(label_list)):
  height = img_fin.shape[0]
  width = img_fin.shape[1]
  #print(height,width)

  w_bb = stats[i,cv.CC_STAT_WIDTH]
  #print(w_bb)

  h_bb = stats[i,cv.CC_STAT_HEIGHT]
  #print(h_bb)

  cent_cell = centroids[i]

  x = int(cent_cell[0]-1.5*w_bb)
  y = int(cent_cell[0]+1.5*w_bb)
  z = int(cent_cell[1]-1.5*h_bb)
  t = int(cent_cell[1]+1.5*h_bb)

  # verifier dans le code de Vivien s'il n'ya pas de fonction qui fait déjà ca 
  cv.rectangle(img_fin, (x, z), (y, t), (255,255,255), 2)
"""

#cropped = img[x:y,z:t]

#cv.imshow('avec une bb normalement',img_fin)

print(label_list)

"""paths=([x for x in os.walk(folder)])
    for i in paths:
        i[2].sort()
        for filename in i[2]:
            path=i[0]+"/"+filename
            path_out=i[0]+"_clean/"
            print(path)
            print(filename)
            img=cv.imread(path)
"""

"""
def detection_discord(img):
            # Nombre max d'iteration est 3
            for i in range(3):
              img_erod = cv.erode(img_open,kernel,iterations = 1)
              output= cv.connectedComponentsWithStats(img_erod)
              (nblabel, labels2, stats, centroids) = output
              label_list2 = matrix_to_list(labels2)
              # Si le nb de labels est different alors on a pls centroids
              if (len(label_list)!=len(label_list2)):
                # On parcours la matrice 
                for i in range(labels.shape[0]):
                  for j in range(labels.shape[1]):
                    # On initialise le nb de centroids et une liste des labels déjà observés
                    nb_cent = 0
                    labels_vus =[]
                    # Si ce qu'on regarde est different du label du fond et des bords
                    if ((labels[i,j]!=-1) and (labels[i,j]!=10)):
                      labeli = labels[i,j]
                      # On regarde les meme pixels de l'autre matrice
                      for k in range(labels.shape[0]):
                        for l in range(labels.shape[1]):
                          # Si c'est bien le meme label
                          if (labels[k,l]==labeli):
                            if(labels2[k,l]!=10 and labels2[k,l] not in labels_vus):
                              labels_vus.append(labels2[k,l])
                              nb_cent +=1
                    # 
                    

              label_list = label_list2
                 
            cv.imwrite(path_out+filename,img_norm)"""

"""
def detection_newcents(img,nb_it):
            output= cv.connectedComponentsWithStats(img)
            # On recupere les stats de l'image sans erosion 
            (nblabel, labels, stats, centroids) = output
            label_list = matrix_to_list(labels)

            # On effectue nb_it erosions sur l'image
            for i in range(nb_it):
              img_erod = cv.erode(img_open,kernel,iterations = i)
              output= cv.connectedComponentsWithStats(img_erod)
            
            # On recupere les stats de l'image erodee  
            (nblabel2, labels2, stats2, centroids2) = output
            label_list2 = matrix_to_list(labels2)
            
            # On cherche les centroids ayant le meme labels dans l'image erodee 
            labels_vus = []
            new_cents = []
            for cent in centroids2:
              cent_int = (int(cent[0]),int(cent[1]))
              for label in labels2:
                if (labels[cent_int[0],cent_int[1]] not in labels_vus):
                  new_cents.append((cent_int[0],cent_int[1]))
                else:
                  labels_vus.append(labels[cent_int[0],cent_int[1]])

            # On associe le centroid dans l'image pas érodée a l'image érodée


            # On cherche un label qui n'existe pas dans la liste des labels et on l'associe a une des deux cellules
            i = len(label_list)+11

            
               

            return new_cents
"""
"""
def detection_newcents(img,nb_it):
  output= cv.connectedComponentsWithStats(img)

  # On recupere les stats de l'image sans erosion 
  (nblabel, labels, stats, centroids) = output
  label_list = matrix_to_list(labels)

  # On effectue nb_it erosions sur l'image

  img_erod = cv.erode(img,kernel,iterations = 1)
  for i in range(2,nb_it):
    img_erod = cv.erode(img_erod,kernel,iterations = i)
    output= cv.connectedComponentsWithStats(img_erod)

  # On recupere les stats de l'image erodee  
  (nblabel2, labels2, stats2, centroids2) = output
  label_list2 = matrix_to_list(labels2)

  # On cherche un label qui n'existe pas dans la liste des labels et on l'associe a une des deux cellules

  # On cherche les centroids ayant le meme labels dans l'image erodee 
  # Methode ou on "copie colle" une partie de l'image
  # On parcourt l'image erodee
  # Comment parcourir 
  new_label = len(label_list) + 11
  for label_act in label_list: # pour tous les labels dans la liste des labels de l'image non erodee
    nb_cents=0 
    cents_trouve = []                
    #while (nb_cents != 2): # tant que le nb de centroids est diff de 2
    for i in range(labels.shape[0]): # On parcours la matrice des labels de l'image non erodee
      for j in range(labels.shape[1]):
        print("Je cherche les centroids et j'en suis a ",(i,j))
        if (labels[i,j]==label_act): # si le label du pixel qu'on regarde est egale au label que l'on etudie  
          if ((i,j) in centroids2): # et si ses coord sont dans la liste de centroids 
            nb_cents+=1 # on ajoute 1 au nb de centroids
            cents_trouve.append((i,j))
    
    # On met le même label pour les deux centroids...
    # On a trouvé deux centroids maintenant on peux modifier l'image avant erosion 
    if (nb_cents == 2):
      for i in range(labels.shape[0]): # On parcours la matrice des labels de l'image non erodee
        for j in range(labels.shape[1]):
          print("Je modifie l'image avant erosion et j'en suis a ",(i,j))
          if (labels2[i,j]==10):
            labels[i,j] = 10
          elif (labels2[i,j]==-1):
            labels[i,j] = -1
          elif (labels2[i,j]==label_act): # Si on est au label actuel on copie le contenu de l'image erodee dans l'image originale
            if (i > int(int((cents_trouve[0][0]) + int(cents_trouve[1][0]))/2) and j > int(int((cents_trouve[0][1]) + int(cents_trouve[1][1]))/2)):
              labels[i,j] = new_label
    
      new_label+=1

      for i in range(labels.shape[0]): # On parcours la matrice des labels et on binarise
        for j in range(labels.shape[1]):
          print("Je binarise l'image obtenue et j'en suis a ",(i,j))
          if (labels2[i,j]==10 or labels2[i,j]==-1):
            labels[i,j] = 1
          else:
            labels[i,j] = 0

  return labels
"""

#cv.imshow('Apres binarisation:',img_bin)
#img_newcents = detection_newcents(img_bin,3)
#cv.imshow('Apres binarisation:',img_newcents)


# modifier juste centroids 
# regarder dans matrice 

# Trouver les centroids de meme labels
# On utilise np.where pour determiner les indices des pixels de meme labels -> j'ai les indices dans labels de meme labels ( une sorte de mask ?)
# Maintenant, je regarde dans ces indices s'il ya deux centroids, si oui ce sont deux cellules qui se touchent... 
# et donc je modifie l'image de base avec la technique du milieu des centroids 

# IMPORTANT:
  # liste = np.where(matrix = n) 
  # renvoie une liste de liste
  # liste[0] les indices i de elt de matrix respectant la cdt
  # liste[1] les indices j __________________________________

def detection_newcents(img,nb_it):

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

