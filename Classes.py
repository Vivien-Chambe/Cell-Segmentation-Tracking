class Cell:
    def __init__(self, ID,x, y, surface,time=-1):
        self.ID = ID
        self.centroid = (x, y)
        self.surface = surface
        self.time = time