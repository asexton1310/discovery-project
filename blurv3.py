import cv2
import numpy as np


def sobel_blur(path):
    im = cv2.resize(path, (800, 600))
    im = cv2.cvtColor(im, cv2.COLOR_RGB2YCrCb)
    grad_x = cv2.Sobel(im[:, :, 0], cv2.CV_64F, 0, 1)  # horizontal sobel
    grad = np.sqrt(grad_x**2)  # magnitude
    grad_norm_x = (grad * 255 / grad.max()).astype(np.uint8)  # normalizing image
    grad_y = cv2.Sobel(im[:, :, 0], cv2.CV_64F, 1, 0)  # vertical sobel
    grad = np.sqrt(grad_y**2)  # magnitude
    grad_norm_y = (grad * 255 / grad.max()).astype(np.uint8)  # normalizing image
    luma = (grad_norm_x + grad_norm_y)/2
    # print(f"Luma = {np.var(luma)}")
    score = np.var(luma)/380
    if score > 1:
        score = 1
    return score


cap = cv2.VideoCapture('input.mp4')  # insert video here
count = 0 # frame no.
f = open("blur_algorithm_output.txt", "x")
while cap.isOpened():
    ret, frame = cap.read()
    if ret == 0: # if video is complete, break out of loop
        break
    print(f"count = {count}") # frame no.
    # print(f"ret: {ret}  frame: {count+1}   Score: {sobelv2(frame)}")
    # cv2.imwrite(f"video frame {count+1}.jpg", frame)  # save image to file system
    f.write(f"Frame: {count+1}, Score: {sobel_blur(frame)}\n")
    count = count + 1

cap.release()
