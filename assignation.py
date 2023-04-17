from Classes import Cell
import numpy as np

a1=Cell(1,57.78827361563518, 39.42410423452769,1535)
a2=Cell(1,56.4470509383378, 37.75201072386059,1492)
b1=Cell(2,138.30181979582778, 66.41455836662229,2253)
b2=Cell(2,138.75902004454343, 67.55723830734966,2245)
z1=Cell(37,19.938091769847052, 980.8237436270939,1373)

def cost(a, b):
    coeffD=0.000001
    coeffS=0.000009
    ax,ay=a.centroid
    bx,by=b.centroid
    distance=np.sqrt(pow(bx-ax,2)+pow(by-ay,2))
    s=abs(a.surface-b.surface)
    return 1-(coeffD*distance+coeffS*s)

print(cost(a1,b2),cost(a1,a2),cost(a1,b2)<cost(a1,a2))
print(cost(a1,z1),cost(a1,z1)<cost(a1,a2))
