## Class Cell 
## Cette classe permettra de gerer et différencier nos cellules 
class Cell:
    def __init__(self, x, y, state):
        self.x = x
        self.y = y
        self.state = state
        self.neighbors = []
        self.next_state = None
