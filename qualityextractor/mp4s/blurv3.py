# input video file.
# output will be inserted into a text file named "blur_algorithm_output.txt"
# score is between 0 - 1, where 1 is high quality, 0 is low quality (more noise
# will contain a lower score)

import cv2
import numpy as np


def sobel_blur(path):
    if np.mean(path) == 0:  # if frame is a solid color
        return 0
    else:
        im = cv2.resize(path, (800, 600))
        im = cv2.cvtColor(im, cv2.COLOR_RGB2YCrCb)
        grad_x = cv2.Sobel(im[:, :, 0], cv2.CV_64F, 0, 1)  # horizontal sobel
        grad = np.sqrt(grad_x**2)  # magnitude
        grad_norm_x = (grad * 255 / grad.max()
                       ).astype(np.uint8)  # normalizing image
        grad_y = cv2.Sobel(im[:, :, 0], cv2.CV_64F, 1, 0)  # vertical sobel
        grad = np.sqrt(grad_y**2)  # magnitude
        grad_norm_y = (grad * 255 / grad.max()
                       ).astype(np.uint8)  # normalizing image
        luma = (grad_norm_x + grad_norm_y)/2
        score = np.var(luma)/380
        if score > 1:
            score = 1
        return score


if __name__ == "__main__":

    cap = cv2.VideoCapture('A001.mp4')  # insert video here
    count = 0
    f = open("blur_algorithm_output.txt", "x")
    while cap.isOpened():
        ret, frame = cap.read()
        if ret == 0:
            break
        print(f"count = {count}")
        f.write(f"Frame: {count+1}, Score: {sobel_blur(frame)}\n")
        count = count + 1

    cap.release()
