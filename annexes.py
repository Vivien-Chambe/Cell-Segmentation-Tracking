import cv2 as cv

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap

from Classes import Cell
import numpy as np


def convert_cv_qt(cv_img):
        """Convertir une image opencv vers une image QPixmap"""
        cv_img = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB)
        height, width, _ = cv_img.shape
        bytes_per_line = 3 * width
        convert_to_Qt_format = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

## Fonction pour obtenur dans une liste les noms de tous les fichiers d'un dossier
def get_files(path):
        import os
        files = []
        for file in os.listdir(path):
                if file.endswith(".tif"):
                        files.append(file)
        return files

def distance (coord1, coord2):
        return ((coord1[0]-coord2[0])**2 + (coord1[1]-coord2[1])**2)**0.5

## Function that solve a linear assignment problem 
# Entrée: deux listes de Cellules (cells1 et cells2)
# Sortie: une liste de tuples (cell1, cell2) qui sont les cellules qui correspondent
def solve_linear_assignment (cells1, cells2):
        from scipy.optimize import linear_sum_assignment
        from numpy import zeros
        # On veut créer une matrice de distance entre les cellules
        matrix = zeros((len(cells1), len(cells2)))
        for i in range(len(cells1)):
                for j in range(len(cells2)):
                        matrix[i][j] = distance(cells1[i].getCentroid(), cells2[j].getCentroid())
        # On veut résoudre le problème d'assignation linéaire
        row_ind, col_ind = linear_sum_assignment(matrix)
        # On veut retourner une liste de tuples (cell1, cell2) qui sont les cellules qui correspondent
        correspondance = []
        for i in range(len(row_ind)):
                correspondance.append((cells1[row_ind[i]].ID, cells2[col_ind[i]].ID))

        ## On mets à jour les ID des cellules de cells2 pour les prochaines itérations
        for corr in correspondance:
                cells2[corr[1]-1].ID = corr[0]
        return correspondance

def cost(ListeT0: list[Cell], ListeT1: list[Cell],marginD=float('inf')):
    """
    Renvoie une liste de paire de taille len(ListeT0), 
    celle ci est l'assignation linéaire des point de ListeT0 avec ceux de Liste T1, 
    les couples étant les indices de chaque cellule dans leur liste respective.
    marginD peut être spécifié pour avoir une ROI autour de la cellule étudié, 
    évitant l'évaluation de cellule trop eloignée, elle est par défaut à +inf mais peut être 
    choisi si besoin (préférables)
    """
    out=[]
    for i in range(0,len(ListeT0)):
        ix,iy=ListeT0[i].centroid
        isurf=ListeT0[i].surface
        max=(-1,0)#couple initalisé aux valeurs de base
        for j in range(0,len(ListeT1)):
            jx,jy=ListeT1[j].centroid
            jsurf=ListeT1[j].surface
            #paramêtres de la note
            dist=np.sqrt(pow(ix-jx,2)+pow(iy-jy,2))
            surf=abs(isurf-jsurf)
            if (dist<marginD):
            #calcul de la note, peut être modulé
                if (surf==0):
                    surf=0.000000000000000000000000001
                if (dist==0):
                    dist=0.000000000000000000000000001
                grade=1/dist + 1/surf#changer le numérateur des fractions pour donner du poids à un paramêtre
                #comparaison avec la note la plus haute
                if (max[1]<grade and ListeT1[j].ID!=-1):
                    max=(j,grade)
        if max[1]>0:#cas où la note obtenue a été modifiée
            ListeT1[max[0]].ID=-1 #on retire la cellule des cellules assignables
            #ajoute l'assignation à la liste
            out.append((i,max[0]))
    for i in range(0,len(ListeT1)):
        ListeT1[i].ID=i+1
    
    return out

print("annexes.py loaded")


