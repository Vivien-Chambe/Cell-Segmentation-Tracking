import random
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSlider, QGridLayout, QLineEdit


import cv2 as cv
import numpy as np
import csv

from utils import convert_cv_qt
from classes import Cell


puits = "puit03"
path = "images/"+puits+"/t004.tif"


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
        self.cells = [] # Liste des cellules pour chaque image (liste de liste)


        self.label = QLabel("Hello") # Label pour afficher l'image
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label,0,1,3,3) # Ajouter le label au layout
        
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

        ## Ajouter un slider pour changer la valeur du gaussian blur
        """ self.slider_gaussian = QSlider(Qt.Horizontal)
        
        self.slider_gaussian.setMinimum(1)
        self.slider_gaussian.setMaximum(10)
        self.slider_gaussian.setValue(5)
        self.slider_gaussian.setTickInterval(1)
        self.slider_gaussian.setTickPosition(QSlider.TicksBelow)
        self.slider_gaussian.valueChanged.connect(self.gaussian_blur)
        layout_gaussian.addWidget(self.slider_gaussian) """

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

        ## Bouton pour faire un dilation
        self.dilationBtn = QPushButton("Dilation")
        self.dilationBtn.pressed.connect(self.dilation)
        layout_edit.addWidget(self.dilationBtn)

        ## Bouton pour labeliser les cellules
        self.labelBtn = QPushButton("Labeliser")
        self.labelBtn.pressed.connect(self.labeliser)
        layout_label.addWidget(self.labelBtn)

        ## Bouton pour exporter les coordonnées des cellules dans un fichier csv
        self.exportBtn = QPushButton("Exporter")
        self.exportBtn.pressed.connect(self.export)
        layout_label.addWidget(self.exportBtn)

        ## ajouter une image 
        self.image = cv.imread(path) # Charger l'image
        self.label.setPixmap(convert_cv_qt(self.image)) # Afficher l'image
        

    def reset_image(self):
        self.image = cv.imread(path)
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
        gray = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)

        ## Appliquer un treshold
        ret, thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
        #C = int(self.input_adaptive.text())
        #thresh = cv.adaptiveThreshold(self.image,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY_INV,11,1)
        self.treshold = thresh
        ## Mettre l'image dans le label
        self.label.setPixmap(convert_cv_qt(thresh))
        
    

    def erosion(self):
        ## Vérifier si l'image a été treshold ou non
        if self.treshold is None: 
            return
        
        ## Appliquer un erosion
        kernel = np.ones((5, 5), np.uint8)
        self.treshold = cv.erode(self.treshold, kernel, iterations=1)

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

    def labeliser(self):
        ## Vérifier si l'image a été treshold ou non
        if self.treshold is None:
            return

        (nblabel, labels, stats, centroids)= cv.connectedComponentsWithStats(self.treshold) # On veut récupérer le nombre de cellules, les labels, les stats et les centroides

        print(nblabel)
        print(centroids)

        ## On veut afficher les centroides sur l'image
        # for i in range(1, nblabel):
        #     cv.circle(self.treshold, (int(centroids[i][0]), int(centroids[i][1])), 2, (0, 0, 255), -1)
        ## Mettre l'image dans le label
        #self.label.setPixmap(convert_cv_qt(self.treshold))

        # On veut garder une trace des cellules et de leurs stats
        cells = []
        for i in range(1, nblabel):
            cells.append(Cell(i, centroids[i][0],centroids[i][1], stats[i][4]))

        self.cells.append(cells)

    def export(self):
        ## Vérifier si l'image a été treshold ou non
        if self.treshold is None:
            return

        ## Vérifier si l'image a été labelisée ou non
        if len(self.cells) == 0:
            return

        ## On veut exporter les coordonnées des cellules dans un fichier csv
        ## On veut exporter le numéro de la cellule, le centre de la cellule
        
        with open(f'{puits}.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Numéro de la cellule", "Centre de la cellule", "Surface"])
            for cells in self.cells:
                for cell in cells:
                    writer.writerow([cell.ID, cell.centroid, cell.surface])


        

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()