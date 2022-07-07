from skimage import filters
from skimage.feature import local_binary_pattern
import matplotlib.pyplot as plt
import numpy as np
from sklearn import preprocessing
import cv2

# This function calculate contrast distortion effectively 
# on gray-scale denoted as GD


def calculateGD(frameInput):
    scalePercent = 5
    arrayOfGD = []
    # settings for LBP
    radius = 3
    n_points = 8 * radius
    # image = cv2.imread(frameInput, cv2.IMREAD_GRAYSCALE)
    image = cv2.cvtColor(frameInput, cv2.COLOR_BGR2GRAY)
    height = int(image.shape[0] * (scalePercent / 100))
    width = int(image.shape[1] * (scalePercent / 100))
    imageResize = cv2.resize(image, (width, height))
    # calculate gradient map
    gradientMap = filters.sobel(imageResize)
    # calculate local binary patten
    lbp = local_binary_pattern(imageResize, n_points, radius)
	
    for i in range(0, 9):
        sumOfGLBP = 0
        for m in range(len(gradientMap)):
            for n in range(len(gradientMap[0])):
                resultDeltaFunction = i - lbp[m][n]
                if resultDeltaFunction >= 0:
                    deltaFunction = 1
                else:
                    deltaFunction = 0
                GLBP = gradientMap[m][n] * deltaFunction
                sumOfGLBP = sumOfGLBP + GLBP
        arrayOfGD.append(sumOfGLBP)
    normalized_arrayOfGD= preprocessing.normalize([arrayOfGD]).flatten()

    #average the entire array of contrast GD
    avgArrayOfGD= round(np.average(normalized_arrayOfGD),7)
    return avgArrayOfGD

#This function calculate features on HSV color space 
#denoted as CS
def calculateCS(frameInput):

	# initialize list of CS - features on HSV color space 
    CS = []

	# Read the image - Notice that OpenCV reads the images as BRG instead of RGB
    # img = cv2.imread(frameInput)
    img = frameInput
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    # calculate 4 features of color moment
    meanOfHSV = np.mean(img, axis=(0, 1))
    varianceOfHSV = (np.mean((img - meanOfHSV) ** 2, axis=(0, 1))) ** (1 / 2)
    skewOfHSV = np.cbrt(np.mean((img - meanOfHSV) ** 3, axis=(0, 1)))
    KurtosisOfHSV = (np.mean((img - meanOfHSV) ** 4, axis=(0, 1))) ** (1 / 4)

    for i in range(1, 3):
        CS.append(meanOfHSV[i])
        CS.append(varianceOfHSV[i])
        CS.append(skewOfHSV[i])
        CS.append(KurtosisOfHSV[i])

    normalized_arrayOfCS = preprocessing.normalize([CS]).flatten()

	#average the entire array of features on HSV color space 
    avgArrayOfCS = round(np.average(normalized_arrayOfCS),8)
    return avgArrayOfCS


if __name__=="__main__":
	imageTest=cv2.imread("2.png")
	imageTest2=cv2.imread('3.png')
	print("Contrast 1: ",calculateGD(imageTest))
	print("Contrast 2: ",calculateGD(imageTest2))
	print("Color 1: ", calculateCS(imageTest))
	print("Color 2: ",calculateCS(imageTest2))



