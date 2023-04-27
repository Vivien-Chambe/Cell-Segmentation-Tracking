import cv2 as cv

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap

from Classes import Cell
import numpy as np

## Permets d'ouvrir une fenêtre de dialogue pour choisir une valeur
def OpenTextBox(title,prompt):
    import tkinter as tk
    from tkinter import simpledialog
    root = tk.Tk()
    root.withdraw()
    user_input = simpledialog.askstring(title=str(title), prompt=str(prompt))
    return user_input

# Convertit une image opencv en image QPixmap
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
                #print(file)
                if file.endswith(".tif") or file.endswith(".png") or file.endswith(".jpg"):
                        files.append(file)
        print("Found "+str(len(files))+" files in "+str(path))
        return files

# Retourne la distance entre deux cellules
def distance (coord1, coord2):
        return ((coord1[0]-coord2[0])**2 + (coord1[1]-coord2[1])**2)**0.5

# Fonction pour résoudre le problème d'assignation linéaire à l'aide de la méthode Hongroise
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


def cost(dist:float,surf:float,ver=0):
    match ver:
        case 0:
            return 1.5/dist+1/surf
        case 1:
            if surf<10:
                return 2/dist
            else:
                return 1/dist
        case _ :
            return 0

def Segment(ListeT0: list[Cell], ListeT1: list[Cell],marginD=float('inf')):
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
            if (dist<marginD):
            #calcul de la note, peut être modulé
                surf=abs(isurf-jsurf)
                if (surf==0):
                    surf=0.000000000000000000000000001
                if (dist==0):
                    dist=0.000000000000000000000000001
                grade =cost(dist,surf)
                #comparaison avec la note la plus haute
                if (max[1]<grade and ListeT1[j].ID!=-1):
                    max=(j,grade)
        if max[1]>0:#cas où la note obtenue a été modifiée
            ListeT1[max[0]].ID=-1 #on retire la cellule des cellules assignables
            #ajoute l'assignation à la liste
            #print((i,max[0]))
            out.append((i,max[0]))
    for i in range(0,len(ListeT1)):
        ListeT1[i].ID=0
    for i in out:
        ListeT1[i[1]].ID=ListeT0[i[0]].ID
        ListeT1[i[1]].time=ListeT0[i[0]].time
    return out

def average(Liste:list[Cell]):
    avg=0
    for i in Liste:
        avg+=i.surface
    avg=avg/len(Liste)
    return avg

def Segment2(ListeT0: list[Cell], ListeT1: list[Cell],marginD=float('inf')):
    """
    Renvoie une liste de paire de taille len(ListeT0), 
    celle ci est l'assignation linéaire des point de ListeT0 avec ceux de Liste T1, 
    les couples étant les indices de chaque cellule dans leur liste respective.
    marginD peut être spécifié pour avoir une ROI autour de la cellule étudié, 
    évitant l'évaluation de cellule trop eloignée, elle est par défaut à +inf mais peut être 
    choisi si besoin (préférables)
    """
    out=[]
    marginS=average(ListeT0)/2
    for i in range(0,len(ListeT0)):
        ix,iy=ListeT0[i].centroid
        isurf=ListeT0[i].surface
        max=(-1,0)#couple initalisé aux valeurs de base
        for j in range(0,len(ListeT1)):
            jx,jy=ListeT1[j].centroid
            jsurf=ListeT1[j].surface
            #paramêtres de la note
            dist=np.sqrt(pow(ix-jx,2)+pow(iy-jy,2))
            if (dist<marginD):
            #calcul de la note, peut être modulé
                surf=abs(isurf-jsurf)
                if (surf<marginS):  
                    if (surf==0):
                        surf=0.000000000000000000000000001
                    if (dist==0):
                        dist=0.000000000000000000000000001
                    grade =cost(dist,surf)
                    #comparaison avec la note la plus haute
                    if (max[1]<grade and ListeT1[j].ID!=-1):
                        max=(j,grade)
        if max[1]>0:#cas où la note obtenue a été modifiée
            ListeT1[max[0]].ID=-1 #on retire la cellule des cellules assignables
            #ajoute l'assignation à la liste
            print((i,max[0]))
            out.append((i,max[0]))
    for i in range(0,len(ListeT1)):
        ListeT1[i].ID=0
    for i in out:
        ListeT1[i[1]].ID=ListeT0[i[0]].ID
        ListeT1[i[1]].time=ListeT0[i[0]].time
    return out

def getHighestID(ListeTi:list[Cell]):
    #/!\ Il faut quand même comparer la sortie avec celle du temps précédent 
    out=0
    for i in ListeTi:
        if i.ID>out:
            out=i.ID
    return out

def updateIDs(ListeT1:list[Cell],maxIDs,time):
    it=1
    for i in ListeT1:
        if i.ID==0:
            #on crée un nouveau ID pour les cellules qui n'en ont pas afin de créer un nouveau tracé
            i.ID=maxIDs+it
            it+=1
            i.time=time
            print("time : "+str(i.time))
        #print(i.ID)

def initT0(ListeT0:list[Cell]):
    for i in ListeT0:
        i.time=0

print("annexes.py loaded")


