class Cell:
    def __init__(self, ID,x, y, surface):
        self.ID = ID
        self.centroid = (x, y)
        self.surface = surface