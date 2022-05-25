import cv2
import numpy as np


def iteration(img, row, col):
    cropped_image = img[row:row+50, col:col+50]  # crop image
    kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
    sharpened_block = cv2.filter2D(cropped_image, -1, kernel)  # sharpen image
    blocky_canny = cv2.Canny(sharpened_block, 50, 90)
    return blocky_canny  # new cropped image


def block(img):
    blockyIm = cv2.resize(img, (500, 300))
    blockyIm = cv2.cvtColor(blockyIm, cv2.COLOR_RGB2YCrCb)
    cropped_image = blockyIm[0:50, 0:50]  # crop image
    kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])  # 8 to 9
    sharpened_block = cv2.filter2D(
        cropped_image[:, :, 0], -1, kernel)  # sharping image
    blocky_canny = cv2.Canny(sharpened_block, 50, 90)
    area = np.array([255, 255, 255, 255, 255])  # line of 5 white pixels
    row = 0
    col = 0
    count = 0
    r = 0
    c = 0
    while True:
        # see if there is a line
        if np.array_equal(area, blocky_canny[row:row+5, col]) == 1:
            count = count + 1
        row = row + 5
        if row == 50:
            col = col + 1
            row = 0
            if col == 50:
                r = r + 50
                if r == 300:
                    c = c + 50
                    r = 0
                if c != 500:
                    # create new cropped image
                    blocky_canny = iteration(blockyIm, r, c)
                    row = 0
                    col = 0
                else:
                    break  # the image has been fully cropped
    if count > 300:
        count = count - 300
    score = 1 - (count / 800)
    if score > 1:
        score = 1
    if score < 0:
        score = 0
    return score


if __name__ == "__main__":
    originalIm = cv2.imread("originalimage.jpg")
    blockyIm = cv2.imread("compressedimage.jpg")

    print(f"originalimage.jpg: {block(originalIm)}")
    print(f"compressedimage.jpg: {block(blockyIm)}")
