# Process 1 contains block, blur, contrast, and noise metrics
# Process 2 contains color metric
# Process 2 contains brisque metric
# In 1 second video clip, script runs in approximately 65 seconds.
# For this instance, I will not use Flickering metric

import block as Blockiness
import blurv3 as Blurriness
import contrastAndColorMetric as CCMetric
import noisev1 as Noise
import nrqe_metrics as NRQEmetrics
import frameExtraction
import os.path
from pathlib import Path
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
    csv_out.send(csv2)


def p1MetricsLoop(framesfolder_path, vidname, csv_out):
    # lists of each frame's metrics
    blockiness_list = []
    blurriness_list = []
#    contrast_list = [[], [], [], [], [], [], [], [], []]
#    contrast_prev = [[], [], [], [], [], [], [], [], []]
    noise_list = []
    csv1 = []  # This will be the list I am sending to the output of the Pipe
    # list of each frame's pixel values
    frame_data = []
    frame_list = os.listdir(framesfolder_path)
    frame_list.sort()
    frame_prev = -1
    start_time = time.perf_counter()
    for frame in frame_list:
        full_path = framesfolder_path + frame
        # some metrics require frame to already be read with opencv
        cv_frame = cv2.imread(full_path)
        # some metrics require an array of frame data. So build it
        frame_data.append(cv_frame)
        if np.mean(frame_prev) != np.mean(cv_frame):
            blockiness_list.append(Blockiness.block(cv_frame))
            blurriness_list.append(Blurriness.sobel_blur(cv_frame))
            # calculateGD returns a list with 9 values
        #    contrast_metrics = CCMetric.calculateGD(full_path)
        #    for i in range(len(contrast_metrics)):
        #        contrast_list[i].append(contrast_metrics[i])
            noise_list.append(Noise.noise(cv_frame))
            frame_prev = cv_frame
        #    contrast_prev = contrast_metrics
        else:
            frame_data.append(cv_frame)
            blockiness_list.append(blockiness_list[len(blockiness_list)-1])
            blurriness_list.append(blurriness_list[len(blurriness_list)-1])
        #    for i in range(len(contrast_prev)):
        #        contrast_list[i].append(contrast_prev[i])
            noise_list.append(noise_list[len(noise_list)-1])

    # VIDEO NAME
    csv1.append(vidname)
    # BLOCKINESS
    addFrameStats(blockiness_list, csv1)
    # BLURRINESS
    addFrameStats(blurriness_list, csv1)
    # CONTRAST
#    for i in range(len(contrast_list)):
#        addFrameStats(contrast_list[i], csv1)
    # NOISE
    addFrameStats(noise_list, csv1)
    print("Time Elapsed for blur, block, noise, contrast: ",
          time.perf_counter() - start_time)
    csv_out.send(csv1)  # Send list to output of Pipe


def p2MetricsLoop(framesfolder_path, vidname, csv_out):
    color_list = [[], [], [], [], [], [], [], []]
    csv2 = []  # This will be the list I am sending to the output of the Pipe
    # list of each frame's pixel values
    frame_data = []
    frame_list = os.listdir(framesfolder_path)
    frame_list.sort()
    frame_prev = -1
    color_prev = [[], [], [], [], [], [], [], []]
    start_time = time.perf_counter()
    for frame in frame_list:
        full_path = framesfolder_path + frame
        # some metrics require frame to already be read with opencv
        cv_frame = cv2.imread(full_path)
        # some metrics require an array of frame data. So build it
        frame_data.append(cv_frame)
        # calculateCS returns a list with 8 values
        if np.mean(frame_prev) != np.mean(cv_frame):
            color_metrics = CCMetric.calculateCS(full_path)
            for i in range(len(color_metrics)):
                color_list[i].append(color_metrics[i])
            frame_prev = cv_frame
            color_prev = color_metrics
        else:
            frame_data.append(cv_frame)
            for i in range(len(color_prev)):
                color_list[i].append(color_prev[i])

    for i in range(len(color_list)):
        addFrameStats(color_list[i], csv2)
    print("Time Elapsed for color: ", time.perf_counter() - start_time)
    csv_out.send(csv2)  # Send list to output of Pipe


def p3MetricsLoop(framesfolder_path, vidname, csv_out):
    brisq = brisque.BRISQUE()
    # lists of each frame's metrics
    brisque_list = []
    csv3 = []  # This will be the list I am sending to the output of the Pipe
    # list of each frame's pixel values
    frame_data = []
    frame_list = os.listdir(framesfolder_path)
    frame_list.sort()
    frame_prev = -1

    frame_count = 0
    flick_sum   = 0

    start_time = time.perf_counter()
    for frame in frame_list:
        frame_count += 1
        # some metrics require frame to already be read with opencv
        full_path = framesfolder_path + frame
        cv_frame = cv2.imread(full_path)
        frame_data.append(cv_frame)
        if np.mean(frame_prev) != np.mean(cv_frame):  # check for freeze-frame
            frame_prev = cv_frame
            # if frame is a solid color, brisque will return error, as expected
            if np.mean(cv_frame) == 0:
                brisque_list.append(0)
            else:
                # BRISQUE output is 0-100. Easy to normalize now
                brisque_list.append(brisq.get_score(cv_frame) / 100)
            #TEMPORAL FLICKERING
            if frame_count == 1:
                # temporal flickering
                flick_ratio, prev_temporal, prev_msds = NRQEmetrics.flickRatio(cv_frame)
            else:
                # temporal flickering
                flick_ratio, prev_temporal, prev_msds = NRQEmetrics.flickRatio(cv_frame, prev_temporal, prev_msds)
            flick_sum += flick_ratio
        else:  # freeze frame occured
            frame_data.append(cv_frame)
            brisque_list.append(brisque_list[len(brisque_list)-1])
    # BRISQUE
    addFrameStats(brisque_list, csv3)
    # TEMPORAL FLICKERNG
    csv3.append(flick_sum / frame_count)
    print("Time Elapsed for BRISQUE: ", time.perf_counter() - start_time)
    csv_out.send(csv3)  # Send list to output of Pipe


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
                 'avg_noise', 'max_noise', 'min_noise', 'avg_brisque', 'max_brisque', 'min_brisque']
    # for testing integration ONLY 
    int_csv_label = ['video_name', 'avg_blockiness', 'max_blockiness', 'min_blockiness', "avg_blur", "max_blur", "min_blur", 'avg_color1', 'max_color1',
                 'min_color1', 'avg_color2', 'max_color2', 'min_color2', 'avg_color3', 'max_color3', 'min_color3', 'avg_color4', 'max_color4', 'min_color4',
                 'avg_color5', 'max_color5', 'min_color5', 'avg_color6', 'max_color6', 'min_color6', 'avg_color7', 'max_color7', 'min_color7', 'avg_color8',
                 'max_color8', 'min_color8',
                 'avg_noise', 'max_noise', 'min_noise', 'avg_brisque', 'max_brisque', 'min_brisque', 'avg_flicker']
    path2file = "live-nrqe.csv"
    path = Path(path2file)
    if path.is_file():
        print("File already exists")
    else:
        with open('live-nrqe.csv', 'a', newline='') as csv_file:
            metric_writer = csv.writer(csv_file, delimiter=',')
            metric_writer.writerow(csv_label)
    #frameExtraction.extractFrameLoop(input_path, output_path, sample_rate)
    print("Done extracting frames")
    start_time = time.perf_counter()

    video_num = 0
    for frame_folder in os.listdir(output_path):
        prefix, _ = frame_folder.split('-')
        csv_in1, csv_out1 = mp.Pipe()  # p1 Pipe (noise, blur, block, contrast)
        csv_in2, csv_out2 = mp.Pipe()  # p2 Pipe (color)
        csv_in3, csv_out3 = mp.Pipe()  # p3 Pipe (brisque)
        # Process p1 (noise, blur, block, contrast)
        p1 = mp.Process(target=p1MetricsLoop, args=(
            output_path + frame_folder + "/", prefix + ".mp4", csv_in1,))
        # Process p2 (color)
        p2 = mp.Process(target=p2MetricsLoop, args=(
            output_path + frame_folder + "/", prefix + ".mp4", csv_in2,))
        # Process p3 (brisque)
        p3 = mp.Process(target=p3MetricsLoop, args=(
            output_path + frame_folder + "/", prefix + ".mp4", csv_in3,))
        # Start the processes
        p1.start()
        p2.start()
        p3.start()
        # retreive Pipe output of csv lists
        csv_out1 = csv_out1.recv()  # return list of csv values for p1 metrics
        csv_out2 = csv_out2.recv()  # return list of csv values for p2 metrics
        csv_out3 = csv_out3.recv()  # return list of csv values for p3 metrics
        p1.join()
        p2.join()
        p3.join()
        # kill processes
        p1.terminate()
        p2.terminate()
        p3.terminate()
        # Acheive total CSV list with appropriate outputs
        csv_out = csv_out1 + csv_out2 + csv_out3
        # WRITE TO CSV
    #    if path.is_file():
    #        with open('live-nrqe.csv', 'a', newline='') as csvfile:
    #            metric_writer = csv.writer(csvfile, delimiter=',')
    #            metric_writer.writerow(csv_out)
    #    else:
    #        print("Error: live-nrqe.csv does not exist.")

        # Write to individual CSV
        csv_prefix = "video"
        with open(f'quality-metrics/{csv_prefix}-{video_num}.csv', 'a', newline='') as csvfile:
            metric_writer = csv.writer(csvfile, delimiter=',')
            # metric_writer.writerows()
            metric_writer.writerow(int_csv_label[1:])
            metric_writer.writerow(csv_out[1:])
        video_num += 1
    print("Total Time Elapsed: ", time.perf_counter() - start_time)
