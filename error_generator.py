# This script adds errors to a video file with a few options.
# 1: Use a bitmask file to set bits low
# 2: Drop packets by specifiyng packet size in bytes, randomly drop packets from a video file 
#    either as a percentage, or a count of packets to drop
# 3: Add salt & pepper noise bytewise or bitwise. Specifying a % rate for bytes/bits to affect
# 4: Add Gaussian noise or blur

# if i was also able to figure out when important information, like transform coefficients, 
# are lost in packets, that could be a great way of indicating when the quality is worse (like in the patent I looked at)

from math import floor
import random
import os.path
import numpy as np
import cv2

# Bitwise & for bytes. taken from: https://www.geeksforgeeks.org/working-with-binary-data-in-python/
# this function converts bytearrays to ints, performs bitwise AND, and converts the result back to a bytearray
def bitwise_and_bytes(a, b):
    result_int = int.from_bytes(a, byteorder="big") & int.from_bytes(b, byteorder="big")
    return result_int.to_bytes(max(len(a), len(b)), byteorder="big")

# Loops over the in_file and mask_file, applying the mask to the bytes in the in_file
# in chunks of bytes_to_read bytes. masks bits to 00, if mask ends before the input file, 
# loop back to the beginning of the mask.
def bitmaskParse(in_filename, out_filename, mask_filename, bytes_to_read):
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

# Parse packet_size bytes in in_filename at a time. randomly set packets low
# with a % chance specified by rate which is a percentage from 0.0-100.0%
def packetRateParse(in_filename, out_filename, rate, packet_size):
    #  get a pseudorandom seed, output seed so we can reproduce for testing,
    #  and then set the seed
    seed = random.random()
    print("Seed: ",seed,"\n")
    random.seed(seed)
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

# Parse packet_size bytes in in_filename at a time. randomly set packets low
# until error_count packets are set low. odds of a packet being dropped increase
# as the number of packets left decreases
def packetCountParse(in_filename, out_filename, error_count, packet_size):
    #  get a pseudorandom seed, output seed so we can reproduce for testing,
    #  and then set the seed
    seed = random.random()
    print("Seed: ",seed,"\n")
    random.seed(seed)
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

# Parse in_file one byte at a time, randomly setting bytes all high or all low
# with a % chance specified by rate which is a percentage from 0.0-100.0%
def saltPepperNoise(in_filename, out_filename, rate):
    # randomly select bytes, then set as b"\FF" or b"\00"
    seed = random.random()
    print("Seed: ",seed,"\n")
    random.seed(seed)
    #open files in byte read/write modes
    with open(in_filename, "rb") as in_file, open(out_filename, "wb") as out_file:
        flip_count = 0
        while True:
            byte = in_file.read(1)
            # when we reach the end of the video file, stop loop
            if byte == b"":
                break
            # determine if this packet should have an error
            if (random.random() * 100) <= rate:
                flip_count += 1
                if random.randint(0,1) == 0:
                    out_file.write(b"\x00")
                else:
                    out_file.write(b"\xFF")
            else:
                out_file.write(byte)
        print("bytes flipped: ",flip_count)

# openCV blurring taken from: https://debuggercafe.com/image-and-video-blurring-using-opencv-and-python/
# uses openCV to extract one frame at a time, add GaussianBlur and write the frame to the output file
def gaussBlur(in_filename, out_filename):
    cap = cv2.VideoCapture(in_filename)
    if not cap.isOpened():
        print("Couldn't open video.")
    # get width and height of frame from video
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
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
        #no frames left
        else:
            break
    cap.release()

# openCV salt & pepper noise taken from: https://stackoverflow.com/questions/22937589/how-to-add-noise-gaussian-salt-and-pepper-etc-to-image-in-python-with-opencv
# uses openCV to extract one frame at a time, adds salt and pepper noise and writes the frame to the output file
# amount is the percentage of bits to salt or pepper as a float
def cvSaltPepper(in_filename, out_filename, amount):
    cap = cv2.VideoCapture(in_filename)
    if not cap.isOpened():
        print("Couldn't open video.")
    # get width and height of frame from video
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    #select codec for writing the blurred video. avc1 is codec used. (https://www.fourcc.org/codecs.php)
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
            num_salt = np.ceil(amount * frame.size * s_vs_p)
            coords = [np.random.randint(0, i - 1, int(num_salt))
                    for i in frame.shape]
            out[coords] = 255

            # Pepper mode
            # gets a count of coordinates to pepper, then generate random coordinates and set them low
            num_pepper = np.ceil(amount * frame.size * (1. - s_vs_p))
            coords = [np.random.randint(0, i - 1, int(num_pepper))
                    for i in frame.shape]
            out[coords] = 0

            #write frame
            outfile.write(out)
        #no frames left
        else:
            break
    cap.release()

# openCV gaussian noise taken from: https://theailearner.com/tag/cv2-randn/
# uses openCV to extract one frame at a time, adds gaussian noise and writes the frame to the output file
def cvGaussNoise(in_filename, out_filename):
    cap = cv2.VideoCapture(in_filename)
    if not cap.isOpened():
        print("Couldn't open video.")
    # get width and height of frame from video
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    #select codec for writing the blurred video. avc1 is codec used. (https://www.fourcc.org/codecs.php)
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
        #no frames left
        else:
            break
    cap.release()

# prompt for file input, could be replaced with hardcoding or reading a config file
# to automate the script better 
in_filename = input("Enter the input video filename: ")
out_filename = input("Enter the output video filename: ")
print("Enter 1 for to use a bitmask in a file, 2 to simulate packet loss mode,")
mode = input("3 to add salt and pepper noise, 4 to add Gaussian noise/blur. Also removes audio. (default): ")

if mode == "1":
    # if bitmask chosen, get the bitmask filename
    mask_filename = input("Enter the error bit mask filename: ")
    bytes_to_read = 1
    bitmaskParse(in_filename, out_filename, mask_filename, bytes_to_read)
elif mode == "2": 
    # if packet loss chosen, get the % rate or count of dropped packets
    bytes_to_read = int(input("Enter the packet size as an integer: "))
    user_num = input("Enter the rate of lost packets as percentage (end with % symbol) or as an integer count: ")
    if "%" in user_num:
        rate = float("".join(ch for ch in user_num if ch.isdecimal() or ch in "."))
        packetRateParse(in_filename, out_filename, rate, bytes_to_read)
    else:
        count = int("".join(filter(str.isdecimal, user_num)))
        packetCountParse(in_filename, out_filename, count, bytes_to_read)
elif mode == "3":
    # if salt and pepper noise was chosen, get the rate
    user_num = input("Enter the rate of noise as percentage: ")
    rate = float("".join(ch for ch in user_num if ch.isdecimal() or ch in "."))
    sp_mode = input ("Enter 1 to salt and pepper bytes, or 2 to salt and pepper bits (default): ")
    if sp_mode == "1":
        saltPepperNoise(in_filename, out_filename, rate)
    else:
        # percent should be a float for cvSaltPepper
        rate = rate / 100.0
        cvSaltPepper(in_filename, out_filename, rate)
else:
    gp_mode = input("Enter 1 to add Gaussian noise, or 2 to add Gaussian blur (default): ")
    if gp_mode == "1":
        cvGaussNoise(in_filename, out_filename)
    else:
        gaussBlur(in_filename, out_filename)