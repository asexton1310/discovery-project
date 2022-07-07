from distutils.command.build import build
import os
import sys

script_dir = os.path.dirname( __file__ )
mymodule_dir = os.path.join( script_dir, '..', '..', )
sys.path.append( mymodule_dir )

import block as Blockiness
import blurv3 as Blurriness
import contrastAndColorMetric as CCMetric
import noisev1 as Noise
import nrqe_metrics as NRQEmetrics
import frameExtraction
import sitiExtraction
import LTPExtractionMetric
import bitstream as BSmetrics
import shutil
from Calculate_AGH_Metrics import extractMetricsFromAGHTool
from pathlib import Path
import cv2
import brisque
import numpy as np
import time
import csv
import multiprocessing as mp
import logging
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class NewFrameEventHandler(PatternMatchingEventHandler):
    # filesystem watchdog for integrating frame extractor with quality
    # metric extractor subsystem.
    # based on examples from python watchdog library available at:
    # https://github.com/gorakhargosh/watchdog/

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_any_event(self, event):
        # for testing purposes, log every event
        logging.info(event)

    def on_moved(self, event):
        self.on_created(event)

    def on_created(self, event):
        filename = event.src_path
        print("filename: ", filename)
        prefix, sample_num = filename.rsplit("-", 1)
        sample_num, postfix = sample_num.rsplit(".", 1)
        print("sample num: ", sample_num)

        # get the previous PNG file's number
        target_num = int(sample_num) - 1
        if target_num < 0:
            print(f"No target, fnum too low")
            return

        # reconstruct path to previous png file (target file)
        target_file = f"{prefix}-{target_num}.{postfix}"
        print(f"Target File: {target_file}")
        print("begin metrics")
        ####  CODE TO RUN PER-FRAME GOES HERE  ####
        buildDeploymentCSV(target_file)
        ####  CODE TO RUN PER-FRAME GOES HERE  ####
        # delete the previous mp4 video
        os.remove(target_file)
        print("delete sucessful")


def getFrames(path):
    # Function that repeatedly polls a directory looking for
    # new frame folders (of extracted frame pngs) and uses an observer to
    # make predictions and delete them when the next frame folder is
    # available.  Modified from quickstart example in
    # Python watchdog library documentation
    # https://github.com/gorakhargosh/watchdog
    #
    # path - folder to watch for new frame folders
    # set up logging for debugging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # set up the event handler we want the watchdog observer to use
    event_handler = NewFrameEventHandler(
        patterns=["*video-*.mp4"], ignore_directories=False
    )
    # Create, configure, and start the observer
    observer = Observer()
    observer.schedule(event_handler, path)
    observer.start()
    print("Looking for folder...")
    # while loop with exception so the user is able to interrupt execution
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def buildTrainingCSV():
    input_path = "./live-test/"
    output_path = "./live-frames/"
    sample_rate = 1000  # samples at video's fps if samplerate above fps

    # identify labels for CSV file
    csv_label = [
        "video_name",
        "block_avg",
        "block_max",
        "block_min",
        "blur_avg",
        "blur_max",
        "blur_min",
        "avg_color1",
        "max_color1",
        "min_color1",
        "avg_color2",
        "max_color2",
        "min_color2",
        "avg_color3",
        "max_color3",
        "min_color3",
        "avg_color4",
        "max_color4",
        "min_color4",
        "avg_color5",
        "max_color5",
        "min_color5",
        "avg_color6",
        "max_color6",
        "min_color6",
        "avg_color7",
        "max_color7",
        "min_color7",
        "avg_color8",
        "max_color8",
        "min_color8",
        "avg_contrast1",
        "max_contrast1",
        "min_contrast1",
        "avg_contrast1",
        "max_contrast2",
        "min_contrast2",
        "avg_contrast3",
        "max_contrast3",
        "min_contrast3",
        "avg_contrast4",
        "max_contrast4",
        "min_contrast4",
        "avg_contrast5",
        "max_contrast5",
        "min_contrast5",
        "avg_contrast6",
        "max_contrast6",
        "min_contrast6",
        "avg_contrast7",
        "max_contrast7",
        "min_contrast7",
        "avg_contrast8",
        "max_contrast8",
        "min_contrast8",
        "avg_contrast9",
        "max_contrast9",
        "min_contrast9",
        "avg_noise",
        "max_noise",
        "min_noise",
        "avg_brisque",
        "max_brisque",
        "min_brisque",
    ]
    # for testing integration ONLY
    int_csv_label = [
        "video",
        "avg_blockiness",
        "max_blockiness",
        "min_blockiness",
        "avg_blur",
        "max_blur",
        "min_blur",
        "avg_contrast1",
        "max_contrast1",
        "min_contrast1",
        "avg_contrast1",
        "max_contrast2",
        "min_contrast2",
        "avg_contrast3",
        "max_contrast3",
        "min_contrast3",
        "avg_contrast4",
        "max_contrast4",
        "min_contrast4",
        "avg_contrast5",
        "max_contrast5",
        "min_contrast5",
        "avg_contrast6",
        "max_contrast6",
        "min_contrast6",
        "avg_contrast7",
        "max_contrast7",
        "min_contrast7",
        "avg_contrast8",
        "max_contrast8",
        "min_contrast8",
        "avg_contrast9",
        "max_contrast9",
        "min_contrast9",
        "avg_color1",
        "max_color1",
        "min_color1",
        "avg_color2",
        "max_color2",
        "min_color2",
        "avg_color3",
        "max_color3",
        "min_color3",
        "avg_color4",
        "max_color4",
        "min_color4",
        "avg_color5",
        "max_color5",
        "min_color5",
        "avg_color6",
        "max_color6",
        "min_color6",
        "avg_color7",
        "max_color7",
        "min_color7",
        "avg_color8",
        "max_color8",
        "min_color8",
        "avg_ltp",
        "max_ltp",
        "min_ltp",
        "avg_noise",
        "max_noise",
        "min_noise",
        "avg_brisque",
        "max_brisque",
        "min_brisque",
        "avg_flicker",
    ]

    path2file = "live-nrqe2.csv"

    path = Path(path2file)
    if path.is_file():
        print("File already exists")
    else:
        with open(path2file, "a", newline="") as csv_file:
            metric_writer = csv.writer(csv_file, delimiter=",")
            metric_writer.writerow(csv_label)
    frameExtraction.extractFrameLoop(input_path, output_path, sample_rate)
    print("Done extracting frames")
    start_time = time.perf_counter()

    for frame_folder in os.listdir(output_path):
        prefix, _ = frame_folder.split("-")
        csv_in1, csv_out1 = mp.Pipe()  # p1 Pipe (noise, blur, block, contrast)
        csv_in2, csv_out2 = mp.Pipe()  # p2 Pipe (color)
        csv_in3, csv_out3 = mp.Pipe()  # p3 Pipe (brisque)
        # Process p1 (noise, blur, block, contrast)
        p1 = mp.Process(
            target=p1MetricsLoop,
            args=(
                output_path + frame_folder + "/",
                prefix + ".mp4",
                csv_in1,
            ),
        )
        # Process p2 (color)
        p2 = mp.Process(
            target=p2MetricsLoop,
            args=(
                output_path + frame_folder + "/",
                prefix + ".mp4",
                csv_in2,
            ),
        )
        # Process p3 (brisque)
        p3 = mp.Process(
            target=p3MetricsLoop,
            args=(
                output_path + frame_folder + "/",
                prefix + ".mp4",
                csv_in3,
            ),
        )
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
        if path.is_file():
            with open(path2file, "a", newline="") as csvfile:
                metric_writer = csv.writer(csvfile, delimiter=",")
                metric_writer.writerow(csv_out)
        else:
            print(f"Error: {path2file} does not exist.")
    print("Total Time Elapsed: ", time.perf_counter() - start_time)


def buildDeploymentCSV(path):
    prefix, sample_num = path.rsplit("-", 1)
    sample_num, postfix = sample_num.rsplit(".", 1)
    frame_list = create_framelist(path)
    print("frame_list length: ", len(frame_list))
    # identify labels for CSV file
    csv_label = [
        "video",
        "avg_blockiness",
        "max_blockiness",
        "min_blockiness",
        "avg_blur",
        "max_blur",
        "min_blur",
        "avg_contrast",
        "max_contrast",
        "min_contrast",
        "avg_color",
        "max_color",
        "min_color",
        "avg_ltp",
        "max_ltp",
        "min_ltp",
        "avg_noise",
        "max_noise",
        "min_noise",
        "avg_brisque",
        "max_brisque",
        "min_brisque",
        # "avg_flicker",
        "bitrate",
        "framerate",
        "resolution",
        "avg_flickering_agh",
        "avg_blockiness_agh",
        "avg_letterBox_agh", 										
        "avg_pillarBox_agh",
        "avg_blockloss_agh",
        "avg_blur_agh",
        "avg_blackout_agh",
        "avg_freezing_agh",
        "avg_exposure_agh",
        "avg_contrast_agh",
        "avg_interlace_agh",
        "avg_noise_agh",
        "avg_si_agh",
        "avg_ti_agh",
    ]
    
    start_time = time.perf_counter()
    vidname = sample_num
    csv_in1, csv_out1 = mp.Pipe()  # p1 Pipe (noise, blur, block, contrast)
    csv_in2, csv_out2 = mp.Pipe()  # p2 Pipe (color)
    csv_in3, csv_out3 = mp.Pipe()  # p3 Pipe (brisque)
    csv_in4, csv_out4 = mp.Pipe()  # p4_AGH Pipe (AGH TOOL metrics)
    csv_in5, csv_out5 = mp.Pipe()  # p5_siti Pipe (SI, TI TOOL metrics)
    # Process p1 (noise, blur, block, contrast)
    p1 = mp.Process(
        target=p1MetricsLoop,
        args=(path + "/", vidname + ".mp4", frame_list, csv_in1),
    )
    # Process p2 (color)
    p2 = mp.Process(
        target=p2MetricsLoop,
        args=(path + "/", vidname + ".mp4", frame_list, csv_in2),
    )
    # Process p3 (bitrate, framerate, resolution)
    p3 = mp.Process(
        target=p3_bitstream_metrics,
        args=(path, csv_in3),
    )
    # Process p4, AGH metrics
    p4_AGH = mp.Process(target=p4_AGH_tool, args=(path, csv_in4))
    # Process p5, SI, TI metrics
    p5_siti = mp.Process(target=p5_si_ti, args=(path, csv_in5))
    # Start the processes
    p1.start()
    p2.start()
    p3.start()
    p4_AGH.start()
    p5_siti.start()
    # retreive Pipe output of csv lists
    csv_out1 = csv_out1.recv()  # return list of csv values for p1 metrics
    csv_out2 = csv_out2.recv()  # return list of csv values for p2 metrics
    csv_out3 = csv_out3.recv()  # return list of csv values for p3 metrics
    csv_out4 = csv_out4.recv()  # return list of csv values for p4 metrics (AGH)
    csv_out5 = csv_out5.recv()  # return list of csv values for p5 metrics(SI, TI)
    p1.join()
    p2.join()
    p3.join()
    p4_AGH.join()
    p5_siti.join()
    # kill processes
    p1.terminate()
    p2.terminate()
    p3.terminate()
    p4_AGH.terminate()
    p5_siti.terminate()
    # Acheive total CSV list with appropriate outputs
    csv_out = (
        csv_out1 + csv_out2 + csv_out3 + csv_out4 + csv_out5
    )
    # Write to individual CSV
    csv_prefix = "video"
    with open(
        f"quality-metrics/{csv_prefix}-{sample_num}.csv", "a", newline=""
    ) as csvfile:
        metric_writer = csv.writer(csvfile, delimiter=",")
        # metric_writer.writerows()
        metric_writer.writerow(csv_label[1:])
        metric_writer.writerow(csv_out[1:])
    print("Total Time Elapsed: ", time.perf_counter() - start_time)


def create_framelist(path):
    cap = cv2.VideoCapture(path)
    frame_list = []
    while cap.isOpened():
        ret, frame = cap.read()
        if ret == 0:
            break
        frame_list.append(frame)
    cap.release()
    return frame_list


def addFrameStats(input_list, out_list):
    out_list.append(np.average(input_list))
    out_list.append(np.max(input_list))
    out_list.append(np.min(input_list))


def flickeringLoop(framesfolder_path, vidname, frame_list, csv_out):
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


def p1MetricsLoop(framesfolder_path, vidname, frame_list, csv_out):
    # lists of each frame's metrics
    blockiness_sum = 0
    blockiness_prev = 0
    blurriness_sum = 0
    blurriness_prev = 0
    contrast_sum = 0
    contrast_prev = 0
    color_sum = 0
    color_prev = 0

    #    noise_list = []
    csv1 = []  # This will be the list I am sending to the output of the Pipe
    # list of each frame's pixel values
    frame_prev = -1
    frame_count = 0
    start_time = time.perf_counter()
    for frame in frame_list:
        # full_path = framesfolder_path + frame
        # some metrics require frame to already be read with opencv
        cv_frame = frame
        # some metrics require an array of frame data. So build it
        frame_count += 1
        if np.mean(frame_prev) != np.mean(cv_frame):
            blockiness_prev = blockiness_val = Blockiness.block(cv_frame)
            blockiness_sum += blockiness_val

            blurriness_prev = blurriness_val = Blurriness.sobel_blur(cv_frame)
            blurriness_sum += blurriness_val
            
            contrast_prev = contrast_val = CCMetric.calculateGD(cv_frame)
            contrast_sum += contrast_val

            color_prev = color_val = CCMetric.calculateCS(cv_frame)
            color_sum += color_val

            frame_prev = cv_frame

            if frame_count == 1:
                # set MAX and MIN
                blockiness_max = blockiness_min = blockiness_val
                blurriness_max = blurriness_min = blurriness_val
                contrast_max = contrast_min = contrast_val
                color_max = color_min = color_val
            else:
                # BLOCKINESS
                if blockiness_val > blockiness_max:
                    blockiness_max = blockiness_val
                elif blockiness_val < blockiness_min:
                    blockiness_min = blockiness_val
                # BLURRINESS
                if blurriness_val > blurriness_max:
                    blurriness_max = blurriness_val
                elif blurriness_val < blurriness_min:
                    blurriness_min = blurriness_val
                # CONTRAST
                if contrast_val > contrast_max:
                    contrast_max = contrast_val
                elif contrast_val < contrast_min:
                    contrast_min = contrast_val
                # COLOR
                if color_val > color_max:
                    color_max = color_val
                elif color_val < color_min:
                    color_min = color_val
        else:
            blockiness_sum += blockiness_prev
            blurriness_sum += blurriness_prev
            contrast_sum += contrast_prev
            color_sum += color_prev
        #    noise_list.append(noise_list[len(noise_list)-1])

    # VIDEO NAME
    csv1.append(vidname)

    # BLOCKINESS
    csv1.append(blockiness_sum / frame_count)
    csv1.append(blockiness_max)
    csv1.append(blockiness_min)
    # BLURRINESS
    csv1.append(blurriness_sum / frame_count)
    csv1.append(blurriness_max)
    csv1.append(blurriness_min)
    # CONTRAST
    csv1.append(contrast_sum / frame_count)
    csv1.append(contrast_max)
    csv1.append(contrast_min)
    # COLOR
    csv1.append(color_sum / frame_count)
    csv1.append(color_max)
    csv1.append(color_min)
    # NOISE
    #    addFrameStats(noise_list, csv1)
    print(
        "Time Elapsed for block, blur, contrast, color: ",
        time.perf_counter() - start_time,
    )
    csv_out.send(csv1)  # Send list to output of Pipe


def p2MetricsLoop(framesfolder_path, vidname, frame_list, csv_out):
    brisq = brisque.BRISQUE()
    # lists of each frame's metrics
    brisque_sum = 0
    ltp_sum = 0
    noise_sum = 0

    ltp_prev = 0
    noise_prev = 0
    brisque_prev = 0
    csv2 = []  # This will be the list I am sending to the output of the Pipe
    # list of each frame's pixel values
    frame_prev = -1
    frame_count = 0
    start_time = time.perf_counter()
    for frame in frame_list:
        # some metrics require frame to already be read with opencv
        cv_frame = frame
        # some metrics require an array of frame data. So build it
        frame_count += 1
        if np.mean(frame_prev) != np.mean(cv_frame):
            ltp_prev = ltp_val = LTPExtractionMetric.getLTPimage(cv_frame)
            ltp_sum += ltp_val

            noise_prev = noise_val = Noise.noise(cv_frame)
            noise_sum += noise_val

            # BRISQUE
            # if frame is a solid color, brisque will return error, as expected
            if np.mean(cv_frame) != 0:
                # BRISQUE output is 0-100. Easy to normalize now
                brisque_prev = brisque_val = brisq.get_score(cv_frame) / 100
                brisque_sum += brisque_val

            if frame_count == 1:
                # set MAX and MIN
                ltp_max = ltp_min = ltp_val
                noise_max = noise_min = noise_val
                brisque_max = brisque_min = brisque_val
            else:
                # LTP
                if ltp_val > ltp_max:
                    ltp_max = ltp_val
                elif ltp_val < ltp_min:
                    ltp_min = ltp_val
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
        else:
            ltp_sum += ltp_prev
            noise_sum += noise_prev
            brisque_sum += brisque_prev

    # LTP
    csv2.append(ltp_sum / frame_count)
    csv2.append(ltp_max)
    csv2.append(ltp_min)

    # NOISE
    csv2.append(noise_sum / frame_count)
    csv2.append(noise_max)
    csv2.append(noise_min)

    # BRISQUE
    csv2.append(brisque_sum / frame_count)
    csv2.append(brisque_max)
    csv2.append(brisque_min)

    print("Time Elapsed for ltp, noise, BRISQUE: ", time.perf_counter() - start_time)
    csv_out.send(csv2)  # Send list to output of Pipe


def p3MetricsLoop(framesfolder_path, vidname, frame_list, csv_out):
    flick_sum = 0

    flick_prev = 0
    csv3 = []  # This will be the list I am sending to the output of the Pipe
    # list of each frame's pixel values
    frame_prev = -1

    frame_count = 0
    flick_sum = 0

    start_time = time.perf_counter()
    for frame in frame_list:
        frame_count += 1
        # some metrics require frame to already be read with opencv
        # full_path = framesfolder_path + frame
        cv_frame = frame
        if np.mean(frame_prev) != np.mean(cv_frame):  # check for freeze-frame
            frame_prev = cv_frame

            if frame_count == 1:
                # set MAX and MIN
                # temporal flickering
                flick_ratio, prev_temporal, prev_msds = NRQEmetrics.flickRatio(cv_frame)
            else:
                # temporal flickering
                flick_ratio, prev_temporal, prev_msds = NRQEmetrics.flickRatio(
                    cv_frame, prev_temporal, prev_msds
                )
            flick_prev = flick_ratio
            flick_sum += flick_ratio
        else:  # freeze frame occured
            flick_sum += flick_prev

    # TEMPORAL FLICKERNG
    csv3.append(flick_sum / frame_count)

    print("Time Elapsed for flickering: ", time.perf_counter() - start_time)
    csv_out.send(csv3)  # Send list to output of Pipe


def AGH_getResutls(path):
    print("getresultspath: ",path)
    if "win" in sys.platform:
        # assume windows
        inputScript = os.path.abspath("Calculate_AGH_Metrics/mitsuWin64.exe")
    else:
        #assume linux
        inputScript = "mitsuLinuxMultithread"
    csv_out = extractMetricsFromAGHTool.extractMetrics(path, inputScript)
    # final metric is slicing, remove it with pop() since this is broken
    csv_out.pop()

    return csv_out


def p4_AGH_tool(path, csv_out):
    absolute_path = os.path.abspath(path)

    start_time = time.perf_counter()
    agh_list = AGH_getResutls(absolute_path)

    csv_out.send(agh_list)  # Send list to output of Pipe
    print("Time Elapsed for AGH Metrics: ", time.perf_counter() - start_time)


def p5_si_ti(path, csv_out):
    start_time = time.perf_counter()
    csv5 = []
    siti_metrics = sitiExtraction.videoSiTi(path)
    si = siti_metrics[0]
    ti = siti_metrics[1]
    csv5.append(si)
    csv5.append(ti)
    print("Time Elapsed for SI TI metrics: ", time.perf_counter() - start_time)
    csv_out.send(csv5)

def p3_bitstream_metrics(path, csv_out):
    start_time = time.perf_counter()
    bitrate, framerate, res = BSmetrics.bitstreamMetrics(path)

    csv_out.send([bitrate, framerate, res])  # Send list to output of Pipe
    print("Time Elapsed for bitstream Metrics: ", time.perf_counter() - start_time)


def quickNormalize(oldValue, oldMax, oldMin):
    newMin, newMax = 0, 1
    newValue = ((oldValue - oldMin) / (oldMax - oldMin)) * (newMax - newMin) + newMin
    return newValue


if __name__ == "__main__":
    getFrames("raw-frames")
