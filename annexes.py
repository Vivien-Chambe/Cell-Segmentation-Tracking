import cv2 as cv

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap


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


