"""
Reference: https://ieeexplore.ieee.org/document/6963354
No-Reference Quality Assessment of Contrast-Distorted Images Based on Natural Scene Statistics
By Y. Fang, K. Ma, Z. Wang, W. Lin, Z. Fang and G. Zhai
"""

from signal import sigtimedwait
from cv2 import mean
from skimage import filters
from skimage.filters.rank import entropy
from skimage.morphology import disk
from skimage.color import rgb2hsv, rgb2gray, rgb2yuv
import numpy as np
from skimage.util import img_as_ubyte
import math
import cv2
import warnings


# This function calculate contrast distortion effectively
# on gray-scale
def contrastDistort(frameInput):
    # initialize list of CS - features on HSV color space
    CS = []
    scalePercent = 10
    sigmaM, muM = 26.063, 118.559
    sigmaD, muD = 18.858, 57.274
    sigmaS, muS = 0.632, 0.180
    sigmaK, muK = 19.317, 2.729
    sigmaE, muE = 0.258, 7.540
    pi = 3.14
    # Read the image - Notice that OpenCV reads the images as BRG instead of RGB
    img = cv2.imread(frameInput)
    height = int(img.shape[0] * (scalePercent/100))
    width = int(img.shape[1] * (scalePercent/100))
    warnings.filterwarnings('ignore')
    imageResize = cv2.resize(img, (width, height))
    # calculate 4 features of color moment
    means = np.average(np.mean(imageResize, axis=(0, 1)))
    standDeviation = np.average(
        (np.mean((imageResize - means)**2, axis=(0, 1)))**(1/2))
    skew = np.average(np.cbrt(np.mean((imageResize - means)**3, axis=(0, 1))))
    kurtosis = np.average(
        (np.mean((imageResize - means)**4, axis=(0, 1)))**(1/4) - 3)
    entro = np.mean(entropy(rgb2gray(imageResize), disk(5)))
    pm = (1 / (math.sqrt(2*pi) * sigmaM)) * \
        math.exp(- ((means - muM)**2)/(2*(sigmaM**2)))
    pd = (1 / (math.sqrt(2*pi) * sigmaD)) * \
        math.exp(- ((standDeviation - muD)**2)/(2*(sigmaD**2)))
    ps = (1 / (math.sqrt(2*pi) * sigmaS)) * \
        math.exp(- ((skew - muS)**2)/(2*(sigmaS**2)))
    pk = math.sqrt((sigmaK / (2*pi * (kurtosis**3)))) * \
        math.exp((-sigmaK*(kurtosis - muK)**2)/(2*(muK**2)*kurtosis))
    pe = (1 / (sigmaE)) * \
        math.exp(((entro - muE) / sigmaE) - math.exp((entro - muE) / sigmaE))

    return round(np.average([pm, pd, ps, pk, pe]), 6)


if __name__ == "__main__":
    imageTest = "014.png"
    imageTest2 = '014_O.png'
    print("Contrast Distort: ", contrastDistort(imageTest))
    print("Contrast Original: ", contrastDistort(imageTest2))
