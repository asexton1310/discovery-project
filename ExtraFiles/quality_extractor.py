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

def addFrameStats(input_list, out_list):
    out_list.append( np.average(input_list) )
    out_list.append( np.max(input_list) )
    out_list.append( np.min(input_list) )

def frameQualityLoop(framesfolder_path, vidname):
    brisq = brisque.BRISQUE()

    # lists of each frame's metrics
    blockiness_list = []
    blurriness_list = []
    color_list      = [ [], [], [], [], [], [], [], []]
    contrast_list   = [ [], [], [], [], [], [], [], [], []]
    noise_list      = []
    brisque_list    = []

    # list of each frame's pixel values
    frame_data = []

    frame_list = os.listdir(framesfolder_path)
    frame_list.sort()
    
    start_time = time.perf_counter()
    j = 1
    for frame in frame_list:
        time_elapsed = time.perf_counter() - start_time
        if (time_elapsed) > (60 * j):
            print("frame: ", frame)
            print("time_elapsed: ", time_elapsed)
            j += 1
        #start_frame = time.perf_counter()
        full_path = framesfolder_path + frame

        # some metrics require frame to already be read with opencv
        cv_frame = cv2.imread(full_path)
        # some metrics require an array of frame data. So build it
        frame_data.append(cv_frame)
        
        blockiness_list.append( Blockiness.block(cv_frame) )
        blurriness_list.append( Blurriness.sobel_blur(cv_frame) )     
        # calculateCS returns a list with 8 values
        color_metrics = CCMetric.calculateCS(full_path)
        for i in range( len(color_metrics) ):
            color_list[i].append(color_metrics[i])
        noise_list.append( Noise.noise(cv_frame) )
        # BRISQUE output is 0-100. Easy to normalize now
        brisque_list.append( brisq.get_score(cv_frame) / 100 )
        # calculateGD returns a list with 9 values
        #contrast_metrics = CCMetric.calculateGD(full_path)
        #for i in range( len(contrast_metrics) ):
        #    contrast_list[i].append( contrast_metrics[i] )
    
    # VIDEO NAME
    csv_out = []
    csv_out.append( vidname )

    # BLOCKINESS
    addFrameStats(blockiness_list, csv_out)

    # BLURRINESS
    addFrameStats(blurriness_list, csv_out)

    # COLOR
    for i in range( len(color_list) ):
        addFrameStats(color_list[i], csv_out)

    # NOISE
    addFrameStats(noise_list, csv_out)

    # BRISQUE
    addFrameStats(brisque_list, csv_out)

    # FLICKERING
    np_frame_array = np.array(frame_data)
    csv_out.append( NRQEmetrics.temporalFlickering(np_frame_array) )

    # CONTRAST
    # for i in range( len(contrast_list) ):
    #    addFrameStats(contrast_list[i], csv_out)

    # WRITE TO CSV
    with open('live-nrqe.csv', 'a', newline='') as csvfile:
        metric_writer = csv.writer(csvfile, delimiter=',')
        metric_writer.writerow( csv_out )

    print( "Time Elapsed: ", time.perf_counter() - start_time )

input_path = "./live-test/"
output_path = "./live-frames/"
sample_rate = 1000 #samples at video's fps if samplerate above fps

#frameExtraction.extractFrameLoop(input_path, output_path, sample_rate)

print("done extracting frames")

for frame_folder in os.listdir(output_path):
    prefix, _ = frame_folder.split('-')
    frameQualityLoop(output_path + frame_folder + "/", prefix + ".mp4")