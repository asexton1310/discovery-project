from tracemalloc import start
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

def frameQualityLoop(framesfolder_path, vidname):
    brisq = brisque.BRISQUE()

    blockiness_list = []
    blurriness_list = []
    color_list      = [ [], [], [], [], [], [], [], []]
    contrast_list   = [ [], [], [], [], [], [], [], [], []]
    noise_list      = []
    brisque_list    = []

    frame_data = []

    frame_list = os.listdir(framesfolder_path)
    frame_list.sort()
    
    start_time = time.perf_counter()
    j = 1
    for frame in frame_list:
    #    time_elapsed = time.perf_counter() - start_time
    #    if (time_elapsed) > (60 * j):
    #        print("frame: ", frame)
    #        print("time_elapsed: ", time_elapsed)
    #        j += 1
       # start_frame = time.perf_counter()
        full_path = framesfolder_path + frame

        # some metrics require frame to already be read with opencv
        cv_frame = cv2.imread(full_path)
        # some metrics require an array of frame data. So build it
        frame_data.append(cv_frame)
    
        time_metric1 = time.perf_counter()
        blockiness_list.append( Blockiness.block(cv_frame) )
        time_metric2 = time.perf_counter()
        print("Blockiness: ", time_metric2 - time_metric1)

        blurriness_list.append( Blurriness.sobel_blur(cv_frame) )
        time_metric3 = time.perf_counter()
        print("Blurriness: ", time_metric3 - time_metric2)
        
        # calculateCS returns a list with 8 values
        color_metrics = CCMetric.calculateCS(full_path)
        for i in range( len(color_metrics) ):
            color_list[i].append(color_metrics[i])
        time_metric4 = time.perf_counter()
        print("Color: ", time_metric4 - time_metric3)

        noise_list.append( Noise.noise(cv_frame) )
        time_metric5 = time.perf_counter()
        print("Noise: ", time_metric5 - time_metric4)

        # BRISQUE output is 0-100
        brisque_list.append( brisq.get_score(cv_frame) / 100 )
        time_metric6 = time.perf_counter()
        print("BRISQUE: ", time_metric6 - time_metric5)

       # calculateGD returns a list with 9 values
        contrast_metrics = CCMetric.calculateGD(full_path)
        for i in range( len(contrast_metrics) ):
            contrast_list[i].append( contrast_metrics[i] )
        time_metric7 = time.perf_counter()
        print("Contrast: ", time_metric7 - time_metric6)
    
    csv_out = []
    csv_out.append( vidname )

    # BLOCKINESS
    csv_out.append( np.average(blockiness_list) )
    csv_out.append( np.max(blockiness_list) )
    csv_out.append( np.min(blockiness_list) )

    # BLURRINESS
    csv_out.append( np.average(blurriness_list) )
    csv_out.append( np.max(blurriness_list) )
    csv_out.append( np.min(blurriness_list) )

    # COLOR
    for i in range( len(color_list) ):
        csv_out.append( np.average(color_list[i]) )
        csv_out.append( np.max(color_list[i]) )
        csv_out.append( np.min(color_list[i]) )

    # NOISE
    csv_out.append( np.average(noise_list) )
    csv_out.append( np.max(noise_list) )
    csv_out.append( np.min(noise_list) )

    # BRISQUE
    csv_out.append( np.average(brisque_list) )
    csv_out.append( np.max(brisque_list) )
    csv_out.append( np.min(brisque_list) )

    np_frame_array = np.array(frame_data)
    csv_out.append( NRQEmetrics.temporalFlickering(np_frame_array) )

   # CONTRAST
   # for i in range( len(contrast_list) ):
   #     csv_out.append( np.average(contrast_list[i]) )
   #     csv_out.append( np.max(contrast_list[i]) )
   #     csv_out.append( np.min(contrast_list[i]) )

    with open('live-nrqe.csv', 'a', newline='') as csvfile:
        metric_writer = csv.writer(csvfile, delimiter=',')
        metric_writer.writerow( csv_out )

    print( "Time Elapsed: ", time.perf_counter() - start_time )

testvid = "A001.mp4"
fname, ext = os.path.splitext(testvid) # split filename from extension

input_path = "./live-test/"
output_path = "./live-frames/"
sample_rate = 1000 #samples at video's fps if samplerate above fps

#frameExtraction.extractFrameLoop(input_path, output_path, sample_rate)

print("done extracting. program should STOP")

for frame_folder in os.listdir(output_path):
    if frame_folder != "A052-frames":
        break
        continue
    prefix, _ = frame_folder.split('-')
    frameQualityLoop(output_path + frame_folder + "/", prefix + ".mp4")