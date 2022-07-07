
# LTP algorithm based on paper by Pedro Garcia Freitas
# Accesible at https://ieeexplore.ieee.org/abstract/document/7498959

from skimage import filters
import numpy as np
from sklearn.preprocessing import normalize
import cv2

def scaleOutput(number):
    old_value = number
    old_min = 0
    old_max = 1600
    new_min = 0
    new_max = 1
    new_value = ((old_value - old_min) / (old_max - old_min)) * \
        (new_max - new_min) + new_min
    return round(new_value, 8)


def getLTPimage(image):
    scalePercent = 3
    listOfImgLTP = []
    images = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # images = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
    height = int(images.shape[0] * (scalePercent/100))
    width = int(images.shape[1] * (scalePercent/100))
    gray_image = cv2.resize(images, (width, height))
    imgLTP = np.zeros_like(gray_image)
    neighboor = 3
    gradientValue = np.average(filters.sobel(gray_image))
    threshold = gradientValue * (np.log(1 - (1/3)))

    for ih in range(0, gray_image.shape[0] - neighboor):
        for iw in range(0, gray_image.shape[1] - neighboor):
            # Step 1: 3 by 3 pixel
            img = gray_image[ih:ih+neighboor, iw:iw+neighboor]
            center = img[1, 1]

            # set the threshold
            img000 = (img - center >= threshold)*(1.0)
            img001 = (img.all() - center <
                      threshold and img.all() - center > -threshold)*(0.0)
            img002 = (img-center < - (threshold))*(-1.0)
            img01 = img000+img001+img002
            img01_vector = img01.T.flatten()
            img01_vector = np.delete(img01_vector, 4)
            where_img01_vector = np.where(img01_vector)[0]
            if len(where_img01_vector) >= 1:
                num = np.sum(2**where_img01_vector)
            else:
                num = 0
            imgLTP[ih+1, iw+1] = num
    listOfImgLTP.append(np.average(imgLTP))

    return(scaleOutput(np.average(listOfImgLTP)))


if __name__ == "__main__":
    imageTest = cv2.imread("014-o.png")
    imageTest2 = cv2.imread('014-d.png')
    print("Frame 1: ", getLTPimage(imageTest))
    print("Frame 2: ", getLTPimage(imageTest2))

