import cv2
import numpy as np


def iteration(img, row, col):
    cropped_image = img[row:row+50, col:col+50]  # crop image
    kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
    sharpened_block = cv2.filter2D(cropped_image, -1, kernel)
    blocky_canny = cv2.Canny(sharpened_block, 50, 90)
    return blocky_canny


def block(img):
    blockyIm = cv2.resize(img, (500, 300))
    blockyIm = cv2.cvtColor(blockyIm, cv2.COLOR_RGB2YCrCb)
    cropped_image = blockyIm[0:50, 0:50]  # crop image
    kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])  # 8 to 9
    sharpened_block = cv2.filter2D(
        cropped_image[:, :, 0], -1, kernel)  # sharping
    blocky_canny = cv2.Canny(sharpened_block, 50, 90)
    area = np.array([255, 255, 255, 255, 255])
    row = 0
    col = 0
    x = 0
    r = 0
    c = 0
    while True:
        if np.array_equal(area, blocky_canny[row:row+5, col]) == 1:
            x = x + 1
        row = row + 5
        if row == 50:
            col = col + 1
            row = 0
            if col == 50:
                r = r + 50
                if r == 300:
                    c = c + 50
                    r = 0
                #print(f"r = {r}, c = {c}")
                if c != 500:
                    blocky_canny = iteration(blockyIm, r, c)
                    row = 0
                    col = 0
                else:
                    break

    print(f"number of 'yes': {x}")


originalIm = cv2.imread("originalimage.jpg")
blockyIm = cv2.imread("compressedimage.jpg")

og = cv2.imread("frame463.jpg")
block(og)
og1 = cv2.imread("frame463_block1.jpg")
block(og1)

og2 = cv2.imread("frame463_block2.jpg")
block(og2)
og3 = cv2.imread("frame463_block3.jpg")
block(og3)
