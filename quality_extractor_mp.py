import block as Blockiness
import blurv3 as Blurriness
# old contrast/color metrics used for consistency
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
import multiprocessing

def addFrameStats(input_list, out_list):
    out_list.append( np.average(input_list) )
    out_list.append( np.max(input_list) )
    out_list.append( np.min(input_list) )

def frameQualityLoop(framesfolder_path, vidname):
    brisq = brisque.BRISQUE()

    # lists of each frame's metrics
    blockiness_sum = 0
    blurriness_sum = 0
    color_sums     = [ 0, 0, 0, 0, 0, 0, 0, 0]
    color_maxs     = [ 0, 0, 0, 0, 0, 0, 0, 0]
    color_mins     = [ 0, 0, 0, 0, 0, 0, 0, 0]
    contrast_sums  = [ 0, 0, 0, 0, 0, 0, 0, 0, 0]
    contrast_maxs  = [ 0, 0, 0, 0, 0, 0, 0, 0, 0]
    contrast_mins  = [ 0, 0, 0, 0, 0, 0, 0, 0, 0]
    noise_sum      = 0
    brisque_sum    = 0
    flick_sum      = 0

    frame_count = 0

    frame_list = os.listdir(framesfolder_path)
    frame_list.sort()
    
    start_time = time.perf_counter()
    j = 1
    for frame in frame_list:
        frame_count += 1
        time_elapsed = time.perf_counter() - start_time
        if (time_elapsed) > (60 * j):
            print("frame: ", frame)
            print("time_elapsed: ", time_elapsed)
            j += 1
        #start_frame = time.perf_counter()
        full_path = framesfolder_path + frame

        # some metrics require frame to already be read with opencv
        cv_frame = cv2.imread(full_path)
        
        blockiness_val = Blockiness.block(cv_frame)
        blockiness_sum += blockiness_val
        blurriness_val = Blurriness.sobel_blur(cv_frame)  
        blurriness_sum += blurriness_val
        # calculateCS returns a list with 8 values
        color_metrics = CCMetric.calculateCS(full_path)
        for i in range( len(color_metrics) ):
            color_sums[i] += color_metrics[i]

        noise_val = Noise.noise(cv_frame)
        noise_sum += noise_val
        # BRISQUE output is 0-100. Easy to normalize now
        brisque_val = brisq.get_score(cv_frame) / 100 
        brisque_sum += brisque_val
        # calculateGD returns a list with 9 values
        #contrast_metrics = CCMetric.calculateGD(full_path)
        #for i in range( len(contrast_metrics) ):
        #    contrast_sums[i] += contrast_metrics[i]
        if frame_count == 1:
            # set MAX and MIN
            blockiness_max = blockiness_min = blockiness_val
            blurriness_max = blurriness_min = blurriness_val
            for i in range( len(color_metrics) ):
                color_maxs[i] = color_mins[i] = color_metrics[i]
            noise_max = noise_min = noise_val
            brisque_max = brisque_min = brisque_val
            #for i in range( len(contrast_metrics) ):
            #    contrast_maxs[i] = contrast_mins[i] = contrast_metrics[i]
            # temporal flickering
            flick_ratio, prev_temporal, prev_msds = NRQEmetrics.flickRatio(cv_frame)
        else:
            # BLOCK
            if blockiness_val > blockiness_max:
                blockiness_max = blockiness_val
            elif blockiness_val < blockiness_min:
                blockiness_min = blockiness_val
            # BLUR
            if blurriness_val > blurriness_max:
                blurriness_max = blurriness_val
            elif blurriness_val < blurriness_min:
                blurriness_min = blurriness_val
            # COLOR
            for i in range( len(color_metrics) ):
                if color_metrics[i] > color_maxs[i]:
                    color_maxs[i] = color_metrics[i]
                elif color_metrics[i] < color_mins[i]:
                    color_mins[i] = color_metrics[i]
            # NOISE
            if noise_val > noise_max:
                noise_max = noise_val
            elif noise_val < noise_min:
                noise_min = noise_val
            # BRISQUE
            if brisque_val > brisque_max:
                brisque_max = brisque_val
            elif brisque_val < brisque_min:
                brisque_min = brisque_val
            # CONTRAST
            #for i in range( len(contrast_metrics) ):
            #    if contrast_metrics[i] > contrast_maxs[i]:
            #        contrast_maxs[i] = contrast_metrics[i]
            #    elif contrast_metrics[i] < contrast_mins[i]:
            #        contrast_mins[i] = contrast_metrics[i]
            # temporal flickering
            flick_ratio, prev_temporal, prev_msds = NRQEmetrics.flickRatio(cv_frame, prev_temporal, prev_msds)
        flick_sum += flick_ratio
    
    # VIDEO NAME
    csv_out = []
    csv_out.append( vidname )

    # BLOCKINESS
    csv_out.append(blockiness_sum / frame_count)
    csv_out.append(blockiness_max)
    csv_out.append(blockiness_min)

    # BLURRINESS
    csv_out.append(blurriness_sum / frame_count)
    csv_out.append(blurriness_max)
    csv_out.append(blurriness_min)

    # COLOR
    for i in range( len(color_sums) ):
        csv_out.append(color_sums[i] / frame_count)
        csv_out.append(color_maxs[i])
        csv_out.append(color_mins[i])

    # NOISE
    csv_out.append(noise_sum / frame_count)
    csv_out.append(noise_max)
    csv_out.append(noise_min)

    # BRISQUE
    csv_out.append(brisque_sum / frame_count)
    csv_out.append(brisque_max)
    csv_out.append(brisque_min)

    # FLICKERING
    csv_out.append(flick_sum / frame_count)

    # CONTRAST
    #for i in range( len(contrast_sums) ):
    #    csv_out.append(contrast_sums[i] / frame_count)
    #    csv_out.append(contrast_maxs[i])
    #    csv_out.append(contrast_mins[i])

    # WRITE TO CSV
    #with open('live-nrqe.csv', 'a', newline='') as csvfile:
    #    metric_writer = csv.writer(csvfile, delimiter=',')
    #    metric_writer.writerow( csv_out )
    print( "Time Elapsed: ", time.perf_counter() - start_time )
    
    #return output to queue instead of writing it here
    return csv_out

def loopHelper(frame_folder, output_path, q):
    prefix, _ = frame_folder.split('-')
    result = frameQualityLoop(output_path + frame_folder + "/", prefix + ".mp4")
    q.put( result )
    return result

def listener(q):
    # this handles writing to the CSV file since multiple processes writing
    # to the same file is bad
    end_flag = False
    while 1: 
        # outer loop so that the CSV file gets updated in batches while processing.
        # just in case of crashes before saving the CSV
        if end_flag:
            break       
        with open('live-nrqe.csv', 'a', newline='') as csvfile:
            metric_writer = csv.writer(csvfile, delimiter=',')
            for i in range(4):
                m = q.get()
                if m == 'kill':
                    end_flag = True
                    break
                metric_writer.writerow( m )

def mpMain():
    ## This is the multiprocessing code that has been running into memory issues. 
    # may not work if run as function. So copy paste into __main__
    manager = multiprocessing.Manager()
    q = manager.Queue()
    # adjust number of processes based on your system's cores
    pool =  multiprocessing.Pool(processes=3)
    watcher = pool.apply_async(listener, (q,))

    input_path = "./live-test/"
    output_path = "./live-frames/"
    sample_rate = 1000 #samples at video's fps if samplerate above fps

    jobs = []
    #frameExtraction.extractFrameLoop(input_path, output_path, sample_rate)
    for frame_folder in os.listdir(output_path):
        job = pool.apply_async(loopHelper, (frame_folder, output_path, q))
        jobs.append(job)

    #collect results, idk if this is really necesary, but hopefully it frees processes
    for job in jobs:
        job.get()
    q.put('kill')
    pool.close()
    pool.join()

def sequentialMain():
    # this is a copy of the non-parallel code. Can be run as a function inside __main__ safely
    input_path = "./live-test/"
    output_path = "./live-frames/"
    sample_rate = 1000 #samples at video's fps if samplerate above fps

    #frameExtraction.extractFrameLoop(input_path, output_path, sample_rate)

    print("done extracting frames")
    #print(frameQualityLoop("./live-frames/A058-frames/", "A058.mp4"))

    for frame_folder in os.listdir(output_path):
        prefix, _ = frame_folder.split('-')
        frameQualityLoop(output_path + frame_folder + "/", prefix + ".mp4")

if __name__ == '__main__':
    manager = multiprocessing.Manager()
    q = manager.Queue()
    # adjust number of processes based on your system's cores
    pool =  multiprocessing.Pool(processes=5) 
    watcher = pool.apply_async(listener, (q,))

    input_path = "./live-test/"
    output_path = "./live-frames/"
    sample_rate = 1000 #samples at video's fps if samplerate above fps

    jobs = []
    frameExtraction.extractFrameLoop(input_path, output_path, sample_rate)
    for frame_folder in os.listdir(output_path):
        job = pool.apply_async(loopHelper, (frame_folder, output_path, q))
        jobs.append(job)

    #collect results, idk if this is really necesary, but hopefully it frees processes
    for job in jobs:
        job.get()
    q.put('kill')
    pool.close()
    pool.join()

