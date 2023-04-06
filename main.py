import random
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget,QSlider


import cv2 as cv
import numpy as np

from utils import convert_cv_qt


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Cell Tracker")

        widget = QWidget() # Widget principal
        self.setCentralWidget(widget)  # Définir le widget principal

        layout = QVBoxLayout()
        widget.setLayout(layout)

        

        self.gaussian_val = 5 # Valeur du gaussian blur
        self.treshold = None
        self.cells = [] # Liste des cellules


        self.label = QLabel("Hello") # Label pour afficher l'image
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label) # Ajouter le label au layout
        
        self.gaussianBlurBtn = QPushButton("Gaussian Blur") # Bouton pour appliquer un filtre gaussien
        self.gaussianBlurBtn.pressed.connect(self.gaussian_blur) # Lorsque le bouton est pressé, on appelle la fonction gaussian_blur
        layout.addWidget(self.gaussianBlurBtn) # Ajouter le bouton au layout

        ## Ajouter un slider pour changer la valeur du gaussian blur
        """ self.slider_gaussian = QSlider(Qt.Horizontal)
        self.slider_gaussian.setMinimum(1)
        self.slider_gaussian.setMaximum(10)
        self.slider_gaussian.setValue(5)
        self.slider_gaussian.setTickInterval(1)
        self.slider_gaussian.setTickPosition(QSlider.TicksBelow)
        self.slider_gaussian.valueChanged.connect(self.gaussian_blur)
        layout.addWidget(self.slider_gaussian) """


        ## Bouton pour faire le masque de l'image
        self.maskBtn = QPushButton("Mask")
        self.maskBtn.pressed.connect(self.mask)
        layout.addWidget(self.maskBtn)

        ## Bouton pour faire un opening
        self.openingBtn = QPushButton("Opening")
        self.openingBtn.pressed.connect(self.opening)
        layout.addWidget(self.openingBtn)


        ## Bouton pour faire un closing
        self.closingBtn = QPushButton("Closing")
        self.closingBtn.pressed.connect(self.closing)
        layout.addWidget(self.closingBtn)

        ## Bouton pour faire un erosion
        self.erosionBtn = QPushButton("Erosion")
        self.erosionBtn.pressed.connect(self.erosion)
        layout.addWidget(self.erosionBtn)

        ## Bouton pour faire un dilation
        self.dilationBtn = QPushButton("Dilation")
        self.dilationBtn.pressed.connect(self.dilation)
        layout.addWidget(self.dilationBtn)

        ## ajouter une image 
        self.image = cv.imread("images/puit03/t004.tif") # Charger l'image
        self.label.setPixmap(convert_cv_qt(self.image)) # Afficher l'image
        

    def gaussian_blur(self):
        self.image = cv.GaussianBlur(self.image, (self.gaussian_val,self.gaussian_val), 0)
        self.label.setPixmap(convert_cv_qt(self.image))

    def mask(self):
        ## Créer un masque pour l'image avec treshold

        ## Convertir l'image en niveaux de gris
        gray = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)

        ## Appliquer un treshold
        ret, thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
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

    ## 
        

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()