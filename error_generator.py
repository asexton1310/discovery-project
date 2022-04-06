# This script adds errors to a video file with a few options.
# 1: Use a bitmask file to set bits low
# 2: Drop packets by specifiyng packet size in bytes, randomly drop packets from a video file 
#    either as a percentage, or a count of packets to drop
# 3: Add salt & pepper noise bytewise or bitwise. Specifying a % rate for bytes/bits to affect
# 4: Add Gaussian noise or blur - Causes color distortions.
# 5: Add blockiness to a video

# if i was also able to figure out when important information, like transform coefficients, 
# are lost in packets, that could be a great way of indicating when the quality is worse (like in the patent I looked at)

# TODO try to introduce ringing and banding error functions

from math import floor
import random
import os.path
import numpy as np
import cv2 #opencv
import time
from shutil import copyfile

def bitwise_and_bytes(a, b):
    # Bitwise & for bytes. taken from: https://www.geeksforgeeks.org/working-with-binary-data-in-python/
    # this function converts bytearrays to ints, performs bitwise AND, and converts the result back to a bytearray

    result_int = int.from_bytes(a, byteorder="big") & int.from_bytes(b, byteorder="big")
    return result_int.to_bytes(max(len(a), len(b)), byteorder="big")

def bitmaskParse(in_filename, out_filename, mask_filename, bytes_to_read):
    # Loops over the in_file and mask_file, applying the mask to the bytes in the in_file
    # in chunks of bytes_to_read bytes. masks bits to 00, if mask ends before the input file, 
    # loop back to the beginning of the mask.

    # open files in byte read/write modes, read bytes_to_read bytes every loop
    with open(in_filename, "rb") as in_file, open(out_filename, "wb") as out_file, open(mask_filename, "rb") as mask_file:
        while True:
            byte = in_file.read(bytes_to_read)
            mask = mask_file.read(bytes_to_read)
            # if we reach the end of the mask before the file is over, start the mask over from the beginning.
            if mask == b"" and byte != b"":
                mask_file.seek(0)
                mask = mask_file.read(bytes_to_read)
            # when we reach the end of the video file, stop loop
            if byte == b"": 
                break
            #print("Byte: ",byte," mask: ",mask," Bitwiseand: ",bitwise_and_bytes(byte,mask))
            out_file.write(bitwise_and_bytes(byte,mask))

def packetRateParse(in_filename, out_filename, rate, packet_size):
    # Parse packet_size bytes in in_filename at a time. randomly set packets low
    # with a % chance specified by rate which is a percentage from 0.0-100.0%

    #open files in byte read/write modes, read packet_size bytes every loop (1 packet)
    with open(in_filename, "rb") as in_file, open(out_filename, "wb") as out_file:
        packets_dropped = 0
        while True:
            byte = in_file.read(packet_size)
            # when we reach the end of the video file, stop loop
            if byte == b"": 
                break
            # determine if this packet should have an error
            if (random.random() * 100) <= rate:
                out_file.write(packet_size * b"\x00")
                packets_dropped += 1
            else:
                out_file.write(byte)
        print("Packets dropped: ", packets_dropped)

def packetCountParse(in_filename, out_filename, error_count, packet_size):
    # Parse packet_size bytes in in_filename at a time. randomly set packets low
    # until error_count packets are set low. odds of a packet being dropped increase
    # as the number of packets left decreases
    
    # Round packet_count down to an integer (so overall filesize stays the same, final packet will not be chosen)
    packet_count = floor(os.path.getsize(in_filename) / packet_size)
    #open files in byte read/write modes, read packet_size bytes every loop (1 packet)
    with open(in_filename, "rb") as in_file, open(out_filename, "wb") as out_file:
        while True:
            byte = in_file.read(packet_size)
            # when we reach the end of the video file, stop loop
            if byte == b"": 
                break
            # determine if this packet should have an error
            # error_count / packet_count gives the chance this packet should have an error from 0-1
            # make sure packet_count > 0 to avoid div by 0 when parsing the final (and possibly partial) packet
            if packet_count > 0 and (random.random() <= (error_count / packet_count)):
                out_file.write(packet_size * b"\x00")
                print("packets left: ", packet_count - 1)
                error_count -= 1
            else:
                out_file.write(byte)
            packet_count -= 1

def saltPepperNoise(in_filename, out_filename, rate):
    # Parse in_file one byte at a time, randomly setting bytes all high or all low
    # with a % chance specified by rate which is a percentage as float from 0.0 to 1.0

    # randomly select bytes, then set as b"\FF" or b"\00"
    #open files in byte read/write modes
    with open(in_filename, "rb") as in_file, open(out_filename, "wb") as out_file:
        flip_count = 0
        while True:
            byte = in_file.read(1)
            # when we reach the end of the video file, stop loop
            if byte == b"":
                break
            # determine if this packet should have an error
            if (random.random()) <= rate:
                flip_count += 1
                if random.randint(0,1) == 0:
                    out_file.write(b"\x00")
                else:
                    out_file.write(b"\xFF")
            else:
                out_file.write(byte)
        print("bytes flipped: ",flip_count)

def cvGaussBlur(in_filename, out_filename):
    # openCV blurring taken from: https://debuggercafe.com/image-and-video-blurring-using-opencv-and-python/
    # uses openCV to extract one frame at a time, add GaussianBlur and write the frame to the output file

    cap = cv2.VideoCapture(in_filename)
    if not cap.isOpened():
        print("Couldn't open video.")
    # get width and height of frame from video
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    #select codec for writing the blurred video. avc1 is codec used. (https://www.fourcc.org/codecs.php)
    outfile = cv2.VideoWriter(out_filename, cv2.VideoWriter_fourcc(*'avc1'), 30, (frame_width, frame_height))

    while (cap.isOpened()):
        # get each frame of video
        ret, frame = cap.read()
        if ret:
            #add bluring/noise
            frame = cv2.GaussianBlur(frame, (5,5), 0)
            #write frame
            outfile.write(frame)
        else:
            #no frames left so leave loop
            break
    cap.release()

def cvSaltPepper(in_filename, out_filename, rate):
    # openCV salt & pepper noise taken from: https://stackoverflow.com/questions/22937589/how-to-add-noise-gaussian-salt-and-pepper-etc-to-image-in-python-with-opencv
    # uses openCV to extract one frame at a time, adds salt and pepper noise and writes the frame to the output file
    # rate is the percentage of bits to salt or pepper as a float

    cap = cv2.VideoCapture(in_filename)
    if not cap.isOpened():
        print("Couldn't open video.")
    # get width and height of frame from video
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    #select codec for writing the distorted video. avc1 is codec used. (https://www.fourcc.org/codecs.php)
    outfile = cv2.VideoWriter(out_filename, cv2.VideoWriter_fourcc(*'avc1'), 30, (frame_width, frame_height))

    while (cap.isOpened()):
        # get each frame of video
        ret, frame = cap.read()
        if ret:
            #actually add the noise here
            s_vs_p = 0.5
            out = np.copy(frame)
            # Salt mode
            # gets a count of coordinates to salt, then generate random coordinates and set them high
            num_salt = np.ceil(rate * frame.size * s_vs_p)
            coords = [np.random.randint(0, i - 1, int(num_salt))
                    for i in frame.shape]
            out[coords] = 255

            # Pepper mode
            # gets a count of coordinates to pepper, then generate random coordinates and set them low
            num_pepper = np.ceil(rate * frame.size * (1. - s_vs_p))
            coords = [np.random.randint(0, i - 1, int(num_pepper))
                    for i in frame.shape]
            out[coords] = 0

            #write frame
            outfile.write(out)
        else:
            #no frames left so leave loop
            break
    cap.release()

def cvGaussNoise(in_filename, out_filename):
    # openCV gaussian noise taken from: https://theailearner.com/tag/cv2-randn/
    # uses openCV to extract one frame at a time, adds gaussian noise and writes the frame to the output file

    cap = cv2.VideoCapture(in_filename)
    if not cap.isOpened():
        print("Couldn't open video.")
    # get width and height of frame from video
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    #select codec for writing the distorted video. avc1 is codec used. (https://www.fourcc.org/codecs.php)
    outfile = cv2.VideoWriter(out_filename, cv2.VideoWriter_fourcc(*'avc1'), 30, (frame_width, frame_height))

    while (cap.isOpened()):
        # get each frame of video
        ret, frame = cap.read()
        #print("Frame:\n",frame)
        if ret:
            mean = (0,0,0)
            sigma = (25, 25, 25)
            # copy the frame to get another, correct-size, frame to hold the noise
            gauss = frame.copy()
            #print("gauss1:\n",gauss )
            # generate the noise and replace the copied frame gauss
            cv2.randn(gauss, mean, sigma)
            #print("gauss2:\n",gauss)
            #add noise to the frame
            out = frame + gauss
            #print("Out:\n",out)
            #write frame
            outfile.write(out)
        else:
            #no frames left so leave loop
            break
    cap.release()

def ffmpegBlockiness(in_filename, out_filename, blockiness):
    # use ffmpeg to add blockiness to an image
    # in_filename  -  name of input video
    # out_filename -  name of output video
    # blockiness   -  an int larger than 2, larger numbers result in lower quality.
    #                 Reductions of quality seem to become less noticeable around 5000
    out_fname, ext = os.path.splitext(out_filename) # split filename from extension
    
    #  apply filter using ffmpeg command line
    os.system("ffmpeg -i {0} -c:v mpeg2video -q:v {1} -c:a copy {2}.ts".format(in_filename, blockiness, out_fname))
    os.system("ffmpeg -i {0}.ts -c:v libx264 {1}".format(out_fname, out_filename))

def ffmpegLoop(input_path, output_path):
    # parse all videos within a folder using a given (currently hardcoded) ffmpeg command
    # input_path  -  path to folder containing input videos
    # output_path -  path to folder that will contain output videos
    
    ts = str(int(time.time())) # timestamp for unique filenames

    for filename in os.listdir(input_path):
        fname, ext = os.path.splitext(filename) # split filename from extension

        print(filename, " encoding")

        ffinput = input_path + fname + ext
        ffoutput = output_path + fname + "-" + ts + ".mp4"
        #   encode each input video using ffmpeg command line
        os.system("ffmpeg -i {0} -b:v 1000k {1} -report".format(ffinput, ffoutput))

def extraErrorLoop(input_path, output_path, error_rate):
    # parse all videos within a folder and add a random distortion
    # input_path  -  path to folder containing input videos
    # output_path -  path to folder that will contain output videos
    # error_rate  -  percent (from 0.0 - 1.0) chance of introducing an error

    mask_filename = "bitmask.txt"     # filename of bitmask to use as a distortion type

    packet_loss_rate = 5.0           # percentage of packets lost as a float from 0.0 to 100.0
    packet_count = 3                  # count of packets to drop
    packet_size_bytes = 4092          # number of bytes in a packet

    salt_pepper_rate = 0.01           # percentage rate of salt and pepper noise, as a float from 0.0 to 1.0

    blockiness = 1000                 # blockiness value. higher number results in more noticeable blocks. min value is 2.

    #  get a pseudorandom seed, output seed so we can reproduce for testing,
    #  and then set the seed
    seed = random.random()
    print("Seed: ",seed,"\n")
    random.seed(seed)  

    step = error_rate / 7    

    for filename in os.listdir(input_path):
        fname, ext = os.path.splitext(filename) # split filename from extension
        in_filename = input_path + filename
        out_file_prefix = output_path + fname

        print(filename, " error")

        mode = random.random()

        if 0 <= mode < 1 * step:
            # bitmask error, set bits low according to a pattern in a file
            out_filename = out_file_prefix + "-bitmask" + ext
            bytes_to_read = 1   # how many bytes to parse at a time

            bitmaskParse(in_filename, out_filename, mask_filename, bytes_to_read)
        elif 1 * step <= mode < 2 * step:
            # packet loss as a percentage
            out_filename = out_file_prefix + "-packetLossRate" + ext

            packetRateParse(in_filename, out_filename, packet_loss_rate, packet_size_bytes)
        elif 2 * step <= mode < 3 * step:
            # packet loss as a fixed count of packets to drop
            # distributed roughly evenly across the video file
            out_filename = out_file_prefix + "-packetLossCount" + ext

            packetCountParse(in_filename, out_filename, packet_count, packet_size_bytes)
        elif 3 * step <= mode < 4 * step:
            # salt and pepper noise with openCV
            out_filename = out_file_prefix + "-cvSnP" + ext

            cvSaltPepper(in_filename, out_filename, salt_pepper_rate)
        elif 4 * step <= mode < 5 * step:
            # gaussian noise
            out_filename = out_file_prefix + "-gaussNoise" + ext

            cvGaussNoise(in_filename, out_filename)
        elif 5 * step <= mode < 6 * step:
            # gaussian blur
            out_filename = out_file_prefix + "-gaussBlur" + ext
            
            cvGaussBlur(in_filename, out_filename)
        elif 6 * step <= mode < 7 * step:
            # blockiness
            out_filename = out_file_prefix + "-blocks" + ext

            ffmpegBlockiness(in_filename, out_filename, blockiness)
        else:
            # no additional distortion
            out_filename = out_file_prefix + "-noDistortion" + ext

            copyfile(in_filename, out_filename)

def extractFrames(in_filepath, in_filename, output_dir, sample_rate):
    # uses openCV to extract distorted frames from a video and save them separately
    # in_filepath -  path to input video
    # in_filename -  name of input video (without extension or path)
    # output_dir  -  path to folder that will contain output frames
    # sample_rate -  number of frames per second to sample

    #create video capture object for the input video
    cap = cv2.VideoCapture(in_filepath)
    if not cap.isOpened():
        print("Couldn't open video.")
        return
    
    video_fps = cap.get(cv2.CAP_PROP_FPS)  # get fps of video
    print("video_fps 1, ", video_fps)
    print("samplerate 1, ", sample_rate)
    sample_rate = min(video_fps, sample_rate)   # cap sample_rate if it is higher than video fps
    print("samplerate 2, ", sample_rate)
    step = video_fps / sample_rate  # determine minimum space between each saved frame

    frame_count = 0
    while (cap.isOpened()):
        # get each frame of video
        ret, frame = cap.read()
        if ret:
            # if this is the next frame after 'step' frames have passed, save it
            if ( frame_count % step ) < 1:
                print('imwrite(...): ', output_dir + "/" + in_filename + "-f{0}".format(frame_count) + ".jpg")
                cv2.imwrite(output_dir + "/" + in_filename + "-f{0}".format(frame_count) + ".jpg", frame) 
            frame_count += 1            
        else:
            #no frames left so leave loop
            break
    cap.release()
    
def extractFrameLoop(input_path, output_path, sample_rate):
    # parse all videos within a folder and sample some frames
    # input_path  -  path to folder containing input videos
    # output_path -  path to folder that will contain subfolder containing output frames
    # sample_rate -  number of frames per second to sample

    for filename in os.listdir(input_path):
        fname, ext = os.path.splitext(filename) # split filename from extension
        in_filepath = input_path + filename
        output_dir = output_path + fname + "-frames" 

        # make folder inside output_path with video file's name to hold extracted frames
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)

        print(filename, " extract frames")

        extractFrames(in_filepath, fname, output_dir, sample_rate)

ffmpegLoop('./inputVideos/', './encodedVideos/')
extraErrorLoop('./encodedVideos/', './distortedVideos/', 1)
extraErrorLoop('./distortedVideos/', './doubledistortedVideos/', 0.5)
extractFrameLoop('./distortedVideos/','./distortedFrames/', 2)

# prompt for file input, could be replaced with hardcoding or reading a config file
# to automate the script better 
# in_filename = input("Enter the input video filename: ")
#out_filename = input("Enter the output video filename: ")
#print("Enter 1 for to use a bitmask in a file, 2 to simulate packet loss mode,")
#mode = input("3 to add salt and pepper noise, 4 to add Gaussian noise/blur. Also removes audio. (default): ")

#if mode == "1":
    # if bitmask chosen, get the bitmask filename
#    mask_filename = input("Enter the error bit mask filename: ")
#    bytes_to_read = 1
#    bitmaskParse(in_filename, out_filename, mask_filename, bytes_to_read)
#elif mode == "2": 
    # if packet loss chosen, get the % rate or count of dropped packets
#    bytes_to_read = int(input("Enter the packet size as an integer: "))
#    user_num = input("Enter the rate of lost packets as percentage (end with % symbol) or as an integer count: ")
#    if "%" in user_num:
#        rate = float("".join(ch for ch in user_num if ch.isdecimal() or ch in "."))
#        packetRateParse(in_filename, out_filename, rate, bytes_to_read)
#    else:
#        count = int("".join(filter(str.isdecimal, user_num)))
#        packetCountParse(in_filename, out_filename, count, bytes_to_read)
#elif mode == "3":
    # if salt and pepper noise was chosen, get the rate
#    user_num = input("Enter the rate of noise as percentage: ")
#    rate = float("".join(ch for ch in user_num if ch.isdecimal() or ch in "."))
#    sp_mode = input ("Enter 1 to salt and pepper bytes, or 2 to salt and pepper bits (default): ")
#    if sp_mode == "1":
#        saltPepperNoise(in_filename, out_filename, rate)
#    else:
        # percent should be a float for cvSaltPepper
#        rate = rate / 100.0
#        cvSaltPepper(in_filename, out_filename, rate)
#else:
#    gp_mode = input("Enter 1 to add Gaussian noise, or 2 to add Gaussian blur (default): ")
#    if gp_mode == "1":
#        cvGaussNoise(in_filename, out_filename)
#    else:
#        cvGaussBlur(in_filename, out_filename)