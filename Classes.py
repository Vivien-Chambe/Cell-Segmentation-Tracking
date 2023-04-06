## Class Cell 
## Cette classe permettra de gerer et différencier nos cellules 
class Cell:
    def __init__(self, ID,x, y, surface):
        self.ID = ID
        self.centroid = (x, y)
        self.surface = surface


