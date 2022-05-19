import cv2
import numpy as np


def noise(path):
    ddepth = cv2.CV_16S
    kernel_size = 3
    src = cv2.cvtColor(path, cv2.COLOR_RGB2YCrCb)
    dst = cv2.Laplacian(src[:, :, 0], ddepth, ksize=kernel_size)
    abs_dst = cv2.convertScaleAbs(dst)
    score = 1 - ((np.var(abs_dst) - 1000) / 8000)
    if score > 1:
        score = 1
    elif score < 0:
        score = 0
    return score


img = 'image.png'  # original image
img = cv2.imread(img)
cv2.imwrite("f.jpg", img)
print(f"image.png: {noise(img)}")


img = 'image_noise1.png'
img = cv2.imread(img)
print(f"image_noise1.png: {noise(img)}")

img = 'image_noise2.png'
img = cv2.imread(img)
print(f"image_noise2.png: {noise(img)}")

img = 'image_noise3.png'
img = cv2.imread(img)
print(f"image_noise3.png: {noise(img)}")
