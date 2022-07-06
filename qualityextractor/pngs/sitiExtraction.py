from siti_tools.siti import SiTiCalculator
from matplotlib import image
import numpy as np


# This tool developed by Werner Robitza and Lukas Krasula
# Reference: https://github.com/VQEG/siti-tools

# Function calculate the spatial information and temporal information
# Require input as a set of Frame's name

def calculateSiTi(setOfFrame):
    setOfTi = []
    setOfSi = []
    previousFrame = -1
    for frame in setOfFrame:
        firstFrame = image.imread(frame)
        siValue = SiTiCalculator.si(firstFrame)
        if np.average(previousFrame) != -1:
            tiValue = SiTiCalculator.ti(firstFrame, previousFrame)
            setOfTi.append(tiValue)
        previousFrame = firstFrame
        setOfSi.append(siValue)
    return [setOfSi, setOfTi]


if __name__ == '__main__':
    setOfFrame = ['frame-2.png', 'frame-12.png', 'frame-15.png']
    print(calculateSiTi(setOfFrame))
    metric = calculateSiTi(setOfFrame)
    si = metric[0]
    ti = metric[1]

    print(f"si : {si}\nti : {ti}")
