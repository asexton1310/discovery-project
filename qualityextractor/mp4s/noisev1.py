# input video file.
# output will be inserted into a text file named "noise_algorithm_output.txt"
# score is between 0 - 1, where 1 is high quality, 0 is low quality (more noise
# will contain a lower score)

import cv2
import numpy as np


def noise(path):
    ddepth = cv2.CV_16S
    kernel_size = 3
    src = cv2.cvtColor(path, cv2.COLOR_RGB2YCrCb)
    src = cv2.Laplacian(src[:, :, 0], ddepth, ksize=kernel_size)
    output = cv2.convertScaleAbs(src)
    score = 1 - ((np.var(output) - 1000) / 8000)
    if score > 1:
        score = 1
    elif score < 0:
        score = 0
    return score

if __name__ == "__main__":

    cap = cv2.VideoCapture('A001.mp4')  # insert video here
    count = 0
    f = open("noise_algorithm_output.txt", "x")
    while cap.isOpened():
        ret, frame = cap.read()
        if ret == 0:
            break
        # (save image to file system)
        # cv2.imwrite(f"video frame {count+1}.jpg", frame)
        f.write(f"Frame: {count+1}, Score: {noise(frame)}\n")
        count = count + 1

    cap.release()
