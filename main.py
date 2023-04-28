import random
import sys
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSlider, QGridLayout, QLineEdit


import cv2 as cv
import numpy as np
import csv

from segmentation import erode, dilate, opening, closing, labeliser_mask
from annexes import convert_cv_qt, get_files,solve_linear_assignment, Segment,Segment2,updateIDs,getHighestID,OpenTextBox, initT0
from Classes import Cell

from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askdirectory

colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255),(255,128,0),(128,255,0),(0,255,128),(0,128,255),(128,0,255),(255,0,128),(0,255,255),(255,255,0),(255,0,255),(0,255,255),(255,128,0),(128,255,0),(0,255,128),(0,128,255),(128,0,255),(255,0,128),(0,255,255),(255,255,0),(255,0,255),(0,255,255)]



# Pour choisir le dossier où se trouvent les images	
Tk().withdraw()
puits = askdirectory()

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Cell Tracker")

        widget = QWidget() # Widget principal
        self.setCentralWidget(widget)  # Définir le widget principal

        #Layout principal grille
        layout = QGridLayout()
        widget.setLayout(layout)

        self.treshold = None
        self.segmentations = [] # Liste des cellules trouvées pour chaque image (liste de liste)
        self.noms_fichiers = get_files(puits) # Liste des noms de fichiers
        self.index_image = 0 # Index de l'image courante
        self.final = {}    # Dictionnaire des labels pour chaque cellule (clé: label, valeur: cellule) ou alors 
                            # dictionnaire des labels pour chaque cellule (clé: label, valeur: liste de tuples (x,y))


        self.label = QLabel("Hello") # Label pour afficher l'image
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label,0,1,3,3) # Ajouter le label au layout
        
        ############################# Boutons ########################################

        ## Layout pour le nputon gaussian blur et treshold
        layout_gaussian = QVBoxLayout()
        layout.addLayout(layout_gaussian,0,0)
        ## Add border to the layout
        layout_gaussian.setContentsMargins(0,0,0,0)

        ## Layout pour les boutons de traitement d'image
        layout_edit = QVBoxLayout()
        layout.addLayout(layout_edit,1,0,2,1)

        ## Layout labelisation
        layout_label = QVBoxLayout()
        layout.addLayout(layout_label,3,0,2,1)



        self.gaussianBlurBtn = QPushButton("Gaussian Blur") # Bouton pour appliquer un filtre gaussien
        self.gaussianBlurBtn.pressed.connect(self.gaussian_blur) # Lorsque le bouton est pressé, on appelle la fonction gaussian_blur
        layout_gaussian.addWidget(self.gaussianBlurBtn) # Ajouter le bouton au layout

        ## Ajouter un input pour changer la valeur du gaussian blur
        self.input_gaussian = QLineEdit()
        self.input_gaussian.setText(str(5))
        layout_gaussian.addWidget(self.input_gaussian)


        self.reset = QPushButton("Reset")
        self.reset.pressed.connect(self.reset_image)
        layout_gaussian.addWidget(self.reset)

        ## Bouton pour faire le masque de l'image
        self.maskBtn = QPushButton("Mask")
        self.maskBtn.pressed.connect(self.mask)
        layout_edit.addWidget(self.maskBtn)

        ## Input pour le adaptive threshold
        self.input_adaptive = QLineEdit()
        self.input_adaptive.setText(str(5))
        layout_gaussian.addWidget(self.input_adaptive)

        ## Bouton pour faire un opening
        self.openingBtn = QPushButton("Opening")
        self.openingBtn.pressed.connect(self.opening)
        layout_edit.addWidget(self.openingBtn)


        ## Bouton pour faire un closing
        self.closingBtn = QPushButton("Closing")
        self.closingBtn.pressed.connect(self.closing)
        layout_edit.addWidget(self.closingBtn)

        ## Bouton pour faire un erosion
        self.erosionBtn = QPushButton("Erosion")
        self.erosionBtn.pressed.connect(self.erosion)
        layout_edit.addWidget(self.erosionBtn)
        ## Ajouter un input pour changer la valeur de lérosion
        self.input_erosion = QLineEdit()
        self.input_erosion.setText(str(3))
        layout_edit.addWidget(self.input_erosion)

        ## Bouton pour faire un dilation
        self.dilationBtn = QPushButton("Dilation")
        self.dilationBtn.pressed.connect(self.dilation)
        layout_edit.addWidget(self.dilationBtn)

        ## Bouton pour segmenter les cellules sur l'image
        self.segmentationBtn = QPushButton("Segmenter")
        self.segmentationBtn.pressed.connect(self.segmenter)
        layout_label.addWidget(self.segmentationBtn)
        
        ## Bouton pour segmenter TOUTES les images
        self.segmentationAllBtn = QPushButton("Segmenter toutes les images")
        self.segmentationAllBtn.pressed.connect(self.segmenter_all)
        layout_label.addWidget(self.segmentationAllBtn)

        ## Ajouter un input pour changer la valeur de la range 
        self.input_range = QLineEdit()

        self.input_range.setText(str(50))
        layout_edit.addWidget(self.input_range)

        ## Bouton pour faire l'assignation des cellules
        self.assignationBtn = QPushButton("Assigner")
        self.assignationBtn.pressed.connect(self.assigner_all)
        layout_label.addWidget(self.assignationBtn)
        

        ## Bouton pour exporter les coordonnées des cellules dans un fichier csv
        self.exportBtn = QPushButton("Exporter")
        self.exportBtn.pressed.connect(self.export)
        layout_label.addWidget(self.exportBtn)

        ## Bouton pour afficher les trajetoires des cellules
        self.trajectoireBtn = QPushButton("Trajectoires")
        self.trajectoireBtn.pressed.connect(self.trajectoire)
        layout_label.addWidget(self.trajectoireBtn)

        ## ajouter une image 
        self.image = cv.imread(puits + "/" + self.noms_fichiers[0],cv.IMREAD_GRAYSCALE) # Charger l'image
        self.image = cv.normalize(self.image, None, 0, 255, cv.NORM_MINMAX)

        self.label.setPixmap(convert_cv_qt(self.image)) # Afficher l'image
        

    def reset_image(self):
        self.image = cv.imread(puits + "/" +self.noms_fichiers[self.index_image],cv.IMREAD_GRAYSCALE)
        self.image = cv.normalize(self.image, None, 0, 255, cv.NORM_MINMAX)
        self.label.setPixmap(convert_cv_qt(self.image))


    def gaussian_blur(self):
        self.reset_image() # Reset l'image car on fait pas plusieurs fois le gaussian blur à la suite
        gaussian_val = int(self.input_gaussian.text())
        if gaussian_val % 2 == 0: # Vérifier si la valeur est paire ou impaire car la valeur doit être impaire
            gaussian_val += 1
        self.image = cv.GaussianBlur(self.image, (gaussian_val,gaussian_val), 0)
        self.label.setPixmap(convert_cv_qt(self.image))
        
    ## Créer un masque pour l'image avec treshold
    def mask(self):
        ## Convertir l'image en niveaux de gris

        ## Appliquer un treshold
        ret, thresh = cv.threshold(self.image, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
        #C = int(self.input_adaptive.text())
        #thresh = cv.adaptiveThreshold(self.image,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY_INV,21,5)
        self.treshold = thresh
        ## Mettre l'image dans le label
        self.label.setPixmap(convert_cv_qt(thresh))
    
    def erosion(self):
        ## Vérifier si l'image a été treshold ou non
        if self.treshold is None: 
            return
        ## Appliquer un erosion
        kernel = np.ones((5, 5), np.uint8)
        self.treshold = cv.erode(self.treshold, kernel, iterations=int(self.input_erosion.text()))

        ## Mettre l'image dans le label
        self.label.setPixmap(convert_cv_qt(self.treshold))

    def dilation(self):
        ## Vérifier si l'image a été treshold ou non
        if self.treshold is None: 
            return
        
        ## Appliquer un dilation
        kernel = np.ones((5, 5), np.uint8)
        self.treshold = cv.dilate(self.treshold, kernel, iterations=1)

        ## Mettre l'image dans le label
        self.label.setPixmap(convert_cv_qt(self.treshold))

    def opening(self):
        ## Vérifier si l'image a été treshold ou non
        if self.treshold is None: 
            return
        
        ## Appliquer un opening
        kernel = np.ones((5, 5), np.uint8)
        self.treshold = cv.morphologyEx(self.treshold, cv.MORPH_OPEN, kernel, iterations=1)

        ## dilate(erode(img, kernel_size, iterations), kernel_size, iterations) autre façon

        ## Mettre l'image dans le label
        self.label.setPixmap(convert_cv_qt(self.treshold))

    def closing(self):
            ## Vérifier si l'image a été treshold ou non
            if self.treshold is None: 
                return
            
            ## Appliquer un closing
            kernel = np.ones((5, 5), np.uint8)
            self.treshold = cv.morphologyEx(self.treshold, cv.MORPH_CLOSE, kernel, iterations=2)

            ## Mettre l'image dans le label
            self.label.setPixmap(convert_cv_qt(self.treshold))
    ## Fonction pour labelliser les cellules à partir de l'image treshold
    ## On veut que cette fonction soit appelée lorsque l'utilisateur clique sur le bouton "Labeliser"
    ## On veut détecter toutes les cellules et enregistrer les cooordonnées de leurs centroides

    def segmenter(self):
        ## Vérifier si l'image a été treshold ou non
        if self.treshold is None:
            return
        
        cells = labeliser_mask(self.treshold)
        self.segmentations.append(cells)

        ## On passe à l'image suivante
        self.index_image += 1
        if self.index_image < len(self.noms_fichiers):
            self.reset_image()
        else:
            self.index_image = 0
            self.reset_image()

    def segmenter_all(self):
        ## Pour chaque image, on veut appliquer la segmentation et enregistrer les résultats de la segmentation dans un fichier
        ## On veut aussi afficher la progression de la segmentation

        self.segmentations = []

        for nom_fichier in self.noms_fichiers:
            self.image = cv.imread(puits + "/" + nom_fichier,cv.IMREAD_GRAYSCALE)
            self.image = cv.normalize(self.image, None, 0, 255, cv.NORM_MINMAX)
            self.label.setPixmap(convert_cv_qt(self.image))
            self.gaussian_blur()
            self.mask()
            self.erosion()
            self.opening()
            self.closing()
            self.segmenter()

            #On enregistre les résultats de la segmentation dans un fichier jpeg avec les centroids et les ID
            rgb = cv.cvtColor(self.treshold,cv.COLOR_GRAY2RGB)
            for cell in self.segmentations[-1]:
                cv.circle(rgb, (int(cell.centroid[0]),int(cell.centroid[1])), 3, (0,0,255), -1)
                cv.putText(rgb, str(cell.ID), (int(cell.centroid[0]),int(cell.centroid[1])), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv.LINE_AA)

            if not os.path.exists(puits + "/tresholds"):
                os.makedirs(puits + "/tresholds")
            cv.imwrite(puits + "/tresholds/" + nom_fichier[:-4] + "_segmentation.jpg", rgb)
            self.treshold = None

            # je veux une barre de progression
            print(f"Segmentation de l'image {self.index_image + 1}/{len(self.noms_fichiers)} terminée")

        print ("Segmentation terminée")
        print (f"Nombre d'images traités: {len(self.segmentations)}")
        print (f"Nombre max de cellules: {max (len(cells) for cells in self.segmentations)}")
        print (f"Nombre min de cellules: {min (len(cells) for cells in self.segmentations)}")


    ## On veut que cette fonction résolve un problème d'assignation linéaire sur les cellules détectées dans chaque image 
    def assigner_all (self):
        maxIDs = 0
        timeactu = 0
        for cell in self.segmentations[0]:
            self.final[cell.ID] = [cell]
        initT0(self.segmentations[0])
        for i in range(1,len(self.segmentations)):
            #V1
            #res = solve_linear_assignment(self.segmentations[i-1], self.segmentations[i])
            # print (res)
            # for corres in res:
            #     if corres[0] not in self.final.keys():
            #         self.final[corres[0]] = []
            #         self.final[corres[0]].append(self.segmentations[i][corres[1]-1])
            #     else:
            #         self.final[corres[0]].append(self.segmentations[i][corres[1]-1])
            
            #V2
            res = Segment(self.segmentations[i-1], self.segmentations[i],int(self.input_range.text()))
            a=getHighestID(self.segmentations[i-1])
            if  a> maxIDs:
                maxIDs = a
            updateIDs(self.segmentations[i],maxIDs,timeactu)
            
            for corres in self.segmentations[i]:
                if corres.ID not in self.final.keys():
                    self.final[corres.ID] = []
                    self.final[corres.ID].append(corres)
                else:
                    self.final[corres.ID].append(corres)
            timeactu+=1
        print(f"Nombre de cellules détectées: {len(self.final)}")
            
    def trajectoire(self):
        ## On veut afficher les trajectoires des cellules image par image 

        i = 0
        for fichier in self.noms_fichiers:
            
            image = cv.imread(puits + "/" + fichier)
            image = cv.normalize(image, None, 0, 255, cv.NORM_MINMAX)
            for cell in self.final.values():
                for j in range(len(cell)-1):
                    color = colors[cell[0].ID%len(colors)]
                    cv.line(image, (int(cell[j].centroid[0]),int(cell[j].centroid[1])), (int(cell[j+1].centroid[0]),int(cell[j+1].centroid[1])),color, 2)
                    cv.circle(image, (int(cell[j].centroid[0]),int(cell[j].centroid[1])), 3, color, -1)
            # cv.imshow("Trajectoire", image)
            # cv.waitKey(0)
            # cv.destroyAllWindows()
            #enregistrer le résultat
            path = puits + "/trajectoires/trajectoire"+ str(i) + "_" +str(self.input_range.text())+".jpg"
            if not os.path.exists(puits + "/trajectoires"):
                os.makedirs(puits + "/trajectoires")
            
            cv.imwrite(path, image)
            i+=1
        
        ## On veut exporter les images obtenues dans un gif 
        # On crée une liste de toutes les images
        i = 0
        import imageio
        images = []
        for fichier in self.noms_fichiers:
            images.append(imageio.imread(puits + "/trajectoires/trajectoire"+ str(i) + "_" +str(self.input_range.text())+".jpg"))
            os.remove(puits + "/trajectoires/trajectoire"+ str(i) + "_" +str(self.input_range.text())+".jpg")
            i+=1
        # On enregistre le gif
        imageio.mimsave(puits + "/trajectoires/trajectoire_" +str(self.input_range.text())+".gif", images, fps=30)
        print("Gif enregistré")


        self.final = {}
    def export(self):

        ## On veut exporter les coordonnées des cellules dans un fichier csv
        ## On veut exporter le numéro de la cellule, le centre de la cellule 
        path = puits + "/trajectoires/trajectoire_" +str(self.input_range.text())+".csv"
        if not os.path.exists(puits + "/trajectoires"):
            os.makedirs(puits + "/trajectoires")
        #On ouvre un fichier csv
        with open(puits + "/trajectoires/trajectoire_" +str(self.input_range.text())+".csv", 'w', newline='') as csvfile:
            fieldnames = ["cellule", "x", "y", "t"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            #On écrit les coordonnées de chaque cellule à chaque instant
            for cells in self.final.values():
                for j in range(len(cells)):
                    writer.writerow({"cellule": cells[j].ID, "x": cells[j].centroid[0], "y": cells[j].centroid[1], "t": cells[j].time})
        print("Fichier csv enregistré")



    def test(self):
        self.segmenter_all()
        for i in range(30,100,10):
            self.input_range.setText(str(i))
            self.assigner_all()
            self.export()
            self.trajectoire()
            self.final = {}
            print("test range = " + str(i) + " terminé")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    
    headless = OpenTextBox("headless", "headless yes/no")
    if headless == "no":
        window.show()
    else:
        window.test()
        exit()

    app.exec_()