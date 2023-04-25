## Class Cell 
## Cette classe permettra de gerer et différencier nos cellules 

# Une cellule contient les informations suivantes:
# - ID: un identifiant unique pour chaque cellule
# - centroid: le centre de la cellule
# - surface: la surface de la cellule


class Cell:
    def __init__(self, ID,x, y, surface):
        self.ID = ID
        self.centroid = (x, y)
        self.surface = surface
        self.time = 0

    def getID(self):
        return self.ID
    
    def getCentroid(self):
        return self.centroid
    
    def getSurface(self):
        return self.surface
    
    def setID(self, ID):
        self.ID = ID

    def setCentroid(self, x, y):
        self.centroid = (x, y)
    
    def setSurface(self, surface):
        self.surface = surface
        


        

    


