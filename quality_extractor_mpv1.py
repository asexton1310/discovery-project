# Process 1 contains color, contrast, noise, blur, block, brisque nrqe_metrics
# Process 2 contains flickering metrics
# In 1 second video clip, script runs in approximately 167 seconds.

import block as Blockiness
import blurv3 as Blurriness
import contrastAndColorMetric as CCMetric
import noisev1 as Noise
import nrqe_metrics as NRQEmetrics
import frameExtraction
import os.path
import cv2
import brisque
import numpy as np
import time
import csv
import multiprocessing as mp


def addFrameStats(input_list, out_list):
    out_list.append(np.average(input_list))
    out_list.append(np.max(input_list))
    out_list.append(np.min(input_list))


def flickeringLoop(framesfolder_path, vidname, csv_out):
    csv2 = []
    # flickering_time = time.perf_counter()
    frame_list = os.listdir(framesfolder_path)
    frame_list.sort()
    frame_data = []
    for frame in frame_list:
        full_path = framesfolder_path + frame
        # some metrics require frame to already be read with opencv
        cv_frame = cv2.imread(full_path)
        # some metrics require an array of frame data. So build it
        frame_data.append(cv_frame)
    # FLICKERING
    frame_list = os.listdir(framesfolder_path)
    frame_list.sort()
    # print(f"frame data: {frame_list}")
    np_frame_array = np.array(frame_data)
    # flickering_time = time.perf_counter()
    csv2.append(NRQEmetrics.temporalFlickering(np_frame_array))
    # print("Time Elapsed for flickering: ", time.perf_counter() - flickering_time)
    csv_out.send(csv2) # send the output to p1 Pipe output


def qualityMetricLoop(framesfolder_path, vidname, csv_out):
    brisq = brisque.BRISQUE()
    # lists of each frame's metrics
    blockiness_list = []
    blurriness_list = []
    color_list = [[], [], [], [], [], [], [], []]
    contrast_list = [[], [], [], [], [], [], [], [], []]
    noise_list = []
    brisque_list = []
    csv1 = []
    # list of each frame's pixel values
    frame_data = []

    frame_list = os.listdir(framesfolder_path)
    frame_list.sort()
    frame_prev = -1
    color_prev = [[], [], [], [], [], [], [], []]
    contrast_prev = [[], [], [], [], [], [], [], [], []]
    start_time = time.perf_counter()
    for frame in frame_list:
        full_path = framesfolder_path + frame
        # some metrics require frame to already be read with opencv
        cv_frame = cv2.imread(full_path)
        # some metrics require an array of frame data. So build it
        frame_data.append(cv_frame)
        # Check for freeze frame
        if np.mean(frame_prev) != np.mean(cv_frame):
            blockiness_list.append(Blockiness.block(cv_frame))
            blurriness_list.append(Blurriness.sobel_blur(cv_frame))
            # calculateCS returns a list with 8 values
            color_metrics = CCMetric.calculateCS(full_path)
            for i in range(len(color_metrics)):
                color_list[i].append(color_metrics[i])
            # calculateGD returns a list with 9 values
            contrast_metrics = CCMetric.calculateGD(full_path)
            for i in range(len(contrast_metrics)):
                contrast_list[i].append(contrast_metrics[i])
            noise_list.append(Noise.noise(cv_frame))
            # BRISQUE output is 0-100. Easy to normalize now
            if np.mean(cv_frame) == 0: #Check for any solid color frame
                brisque_list.append(0)
            else:
                brisque_list.append(brisq.get_score(cv_frame) / 100)
            color_prev = color_metrics
            contrast_prev = contrast_metrics
            frame_prev = cv_frame
        else:  # Freeze frame occured
            frame_data.append(cv_frame)
            blockiness_list.append(blockiness_list[len(blockiness_list)-1])
            blurriness_list.append(blurriness_list[len(blurriness_list)-1])
            for i in range(len(color_prev)):
                color_list[i].append(color_prev[i])
            for i in range(len(contrast_prev)):
                contrast_list[i].append(contrast_prev[i])
            noise_list.append(noise_list[len(noise_list)-1])
            brisque_list.append(brisque_list[len(brisque_list)-1])

    # VIDEO NAME
    csv1.append(vidname)
    # BLOCKINESS
    addFrameStats(blockiness_list, csv1)
    # BLURRINESS
    addFrameStats(blurriness_list, csv1)
    # COLOR
    for i in range(len(color_list)):
        addFrameStats(color_list[i], csv1)
    # CONTRAST
    for i in range(len(contrast_list)):
        addFrameStats(contrast_list[i], csv1)
    # NOISE
    addFrameStats(noise_list, csv1)
    # BRISQUE
    addFrameStats(brisque_list, csv1)
    # print("Time Elapsed for blur, block, noise, color, contrast: ", time.perf_counter() - start_time)
    csv_out.send(csv1) # send the output to p1 Pipe output


if __name__ == "__main__":
    input_path = "./live-test/"
    output_path = "./live-frames/"
    sample_rate = 1000  # samples at video's fps if samplerate above fps
    # identify labels for CSV file
    csv_label = ['video_name', 'block_avg', 'block_max', 'block_min', "blur_avg", "blur_max", "blur_min", 'avg_color1', 'max_color1',
                 'min_color1', 'avg_color2', 'max_color2', 'min_color2', 'avg_color3', 'max_color3', 'min_color3', 'avg_color4', 'max_color4', 'min_color4',
                 'avg_color5', 'max_color5', 'min_color5', 'avg_color6', 'max_color6', 'min_color6', 'avg_color7', 'max_color7', 'min_color7', 'avg_color8',
                 'max_color8', 'min_color8', 'avg_contrast1', 'max_contrast1', 'min_contrast1', 'avg_contrast1', 'max_contrast2', 'min_contrast2', 'avg_contrast3',
                 'max_contrast3', 'min_contrast3', 'avg_contrast4', 'max_contrast4', 'min_contrast4', 'avg_contrast5', 'max_contrast5', 'min_contrast5', 'avg_contrast6', 'max_contrast6',
                 'min_contrast6', 'avg_contrast7', 'max_contrast7', 'min_contrast7', 'avg_contrast8', 'max_contrast8', 'min_contrast8', 'avg_contrast9', 'max_contrast9', 'min_contrast9',
                 'avg_noise', 'max_noise', 'min_noise', 'avg_brisque', 'max_brisque', 'min_brisque', 'avg_flicker']

    with open('live-nrqe.csv', 'a', newline='') as csv_file:
        metric_writer = csv.writer(csv_file, delimiter=',')
        metric_writer.writerow(csv_label)
    print("Extracting Frames")
    frameExtraction.extractFrameLoop(input_path, output_path, sample_rate)
    print("Done Extracting Frames")
    start_time = time.perf_counter()
    for frame_folder in os.listdir(output_path):
        prefix, _ = frame_folder.split('-')
        # initialize P1 pipe
        csv_out1in, csv_out1o = mp.Pipe()
        # initialize p2 Pipe
        csv_out2in, csv_out2o = mp.Pipe()
        # p1 (blur, block, contrast, color, BRISQUE)
        p1 = mp.Process(target=qualityMetricLoop, args=(
            output_path + frame_folder + "/", prefix + ".mp4", csv_out1in,))
        # p2 (flickering)
        p2 = mp.Process(target=flickeringLoop, args=(
            output_path + frame_folder + "/", prefix + ".mp4", csv_out2in,))
        p1.start()
        p2.start()
        # Receive output from p1 and p2 PIPE
        csv_out1 = csv_out1o.recv()
        csv_out2 = csv_out2o.recv()
        p1.join()
        p2.join()
        # Kill processes
        p1.terminate()
        p2.terminate()
        # Combine csv outputs from the 2 processes
        csv_out = csv_out1 + csv_out2
        # WRITE TO CSV
        with open('live-nrqe.csv', 'a', newline='') as csvfile:
            metric_writer = csv.writer(csvfile, delimiter=',')
            metric_writer.writerow(csv_out)
    print("Total Time Elapsed: ", time.perf_counter() - start_time)
