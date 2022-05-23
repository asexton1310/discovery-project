from skimage import filters
from skimage.feature import local_binary_pattern
import matplotlib.pyplot as plt
import numpy as np
from sklearn import preprocessing
import cv2

#This function calculate contrast distortion effectively 
#on gray-scale denoted as GD
def calculateGD(frameInput):
	arrayOfGD=[]
	# settings for LBP
	radius = 3
	n_points = 8 * radius
	image = cv2.imread(frameInput, cv2.IMREAD_GRAYSCALE)
	#calculate gradient map
	gradientMap = filters.sobel(image)
	#calculate local binary patten
	lbp = local_binary_pattern(image,n_points, radius)
	
	for i in range(0,9):
		sumOfGLBP=0
		for m in range(len(gradientMap)):
			for n in range(len(gradientMap[0])):
				resultDeltaFunction = i-lbp[m][n]
				if resultDeltaFunction >= 0:
					deltaFunction = 1
				else:
					deltaFunction = 0
				GLBP = gradientMap[m][n] * deltaFunction
				sumOfGLBP = sumOfGLBP + GLBP
		arrayOfGD.append(sumOfGLBP)
	normalized_arrayOfGD= preprocessing.normalize([arrayOfGD]).flatten()
	return normalized_arrayOfGD
	#x_axis= range(len(arrayOfGD))
	#plt.bar(x_axis, arrayOfGD, color ='blue', width = 0.4)
	#plt.grid(True)
	#plt.show()

#This function calculate features on HSV color space 
#denoted as CS
def calculateCS(frameInput):
	#initialize list of CS - features on HSV color space 
	CS=[]

	# Read the image - Notice that OpenCV reads the images as BRG instead of RGB
	img = cv2.imread(frameInput)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

	#calculate 4 features of color moment
	meanOfHSV = np.mean(img, axis=(0,1))
	varianceOfHSV =(np.mean((img - meanOfHSV)**2,axis=(0,1)))**(1/2)
	skewOfHSV = np.cbrt(np.mean((img - meanOfHSV)**3,axis=(0,1)))
	KurtosisOfHSV = (np.mean((img - meanOfHSV)**4,axis=(0,1)))**(1/4)

	for i in range(1,3):
		CS.append(meanOfHSV[i])
		CS.append(varianceOfHSV[i])
		CS.append(skewOfHSV[i])
		CS.append(KurtosisOfHSV[i])

	normalized_arrayOfCS = preprocessing.normalize([CS]).flatten()
	return normalized_arrayOfCS
	#x_axis= range(len(CS))
	#plt.bar(x_axis, CS, color ='blue', width = 0.4)
	#plt.grid(True)
	#plt.show()

if __name__=="__main__":
	imageTest="test.jpg"
	print(calculateCS(imageTest))




