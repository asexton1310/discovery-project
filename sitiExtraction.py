import numpy as np
from siti_tools.siti import SiTiCalculator
from matplotlib import image

#This tool developed by Werner Robitza and Lukas Krasula 
#Reference: https://github.com/VQEG/siti-tools

#Function calculate the spatial information and temporal information
#Require input as a set of Frame's name
def calculateSiTi(setOfFrame):
	setOfTi=[]
	setOfSi=[]
	previousFrame= None
	for frame in setOfFrame:
		firstFrame = image.imread(frame)
		siValue = SiTiCalculator.si(firstFrame)
		tiValue = SiTiCalculator.ti(firstFrame, previousFrame)
		previousFrame = firstFrame
		setOfSi.append(siValue)
		setOfTi.append(tiValue)
	return setOfSi, setOfTi

if __name__ == "__main__":
	setOfFrame = ["098.png", "104.png"]
	print(calculateSiTi(setOfFrame))
