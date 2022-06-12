import time
import os.path
import cv2 #opencv
import numpy as np
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import logging
import ffmpeg

class NewFrameEventHandler(PatternMatchingEventHandler):
    def __init__(self, n=None, **kwargs):
        super().__init__(**kwargs)
        
        # number of frames to bundle as a video
        self.n = n
        self.segment = 0

    def on_any_event(self, event):
        #for testing purposes, log every event
        logging.info(event)
    
    def on_created(self, event):
        # when a new png file is created, process the previous one
        # this avoids any potential issues with processing a newly
        # created png file before it is finished being written to
        
        # split png number and extension from the rest of the path
        prefix, num_ext = event.src_path.rsplit("-", 1)

        # split png number and extension
        sample_num, ext = os.path.splitext(num_ext)

        #check if this is our nth frame
        if sample_num == (self.segment + 1) * self.n:
            # do the processing,
            new_dir = f"./live-frames/video-{self.segment}-frames"
            os.mkdir(new_dir)
            target_num = int(sample_num) - self.n

            for i in range(target_num, target_num + self.n):
                target_file  = f"{prefix}-{target_num}.{ext}"
                new_location = f"{new_dir}/frame-{target_num}.{ext}"
                #move file to new directory.
                os.replace(target_file,new_location)
        else:
            print(f"frame not multiple of {self.n}")
            return

def saveFrames(frames, step, filename, output_dir):
    #uses openCV for saving frames as png files
    #frames     - numpyarray containing a cv2 representation of each frame
    #step       - step size between each frame
    #filename   - prefix for name of output png files
    #output_dir - path to folder that will contain output frames

    #get how many digits to use when naming files based on number of frames to save
    max_frame = len(frames) * step    
    digits = len(f"{max_frame}")    
    for i, frame in enumerate(frames):
        #get the position of the frame we're saving
        frame_pos = i * step
        #save the frame
       # print(f"imwrite(...): {output_dir}/{filename}-f{frame_pos:0{digits}}.png")
        cv2.imwrite(f"{output_dir}/{filename}-f{frame_pos:0{digits}}.png", frame)

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

        print(f"{filename} extract frames")

        frames, step = extractFrames(in_filepath, sample_rate)
        saveFrames(frames, step, fname, output_dir)

def extractFrames(in_filepath, sample_rate):
    # uses openCV to extract frames from a video
    # in_filepath -  path to input video or webcam
    # sample_rate -  number of frames per second to sample
    # Returns a numpy array with opencv representation of a single frame
    # and step size betwen each saved frame

    #create video capture object for the input video
    cap = cv2.VideoCapture(in_filepath)
    if not cap.isOpened():
        print("Couldn't open video.")
        return
    
    video_fps = cap.get(cv2.CAP_PROP_FPS)  # get fps of video
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"video_fps, {video_fps}")
    print(f"frames, {frames}")
    print(f"samplerate 1, {sample_rate}")
    sample_rate = min(video_fps, sample_rate)   # cap sample_rate if it is higher than video fps
    print(f"samplerate 2, {sample_rate}")
    step = video_fps / sample_rate  # determine minimum space between each saved frame

    framelist = []
    #if the in_filepath is 0, we are reading from a webcam
    if in_filepath == 0:
        frame_pos = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                if (frame_pos % step) < 1:
                    # save the frame
                    framelist.append(frame)
                cv2.imshow("op", frame) #display it for funzies
            if cv2.waitKey(1) == 27:
                #Esc to quit
                break
            frame_pos += 1 
        cap.release()
    else:
        for frame_pos in range(0, frames, int(step)):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            # get the frame from the video
            ret, frame = cap.read()
            if ret:
                # save the frame
                framelist.append(frame)
            else:
                #no frames left to save. exit loop
                break 
        cap.release()
    return np.array(framelist), int(step)

def extractFrameWebcam(output_dir, sample_rate):
    # uses openCV to extract frames from a webcam and save them separately
    # output_dir  -  path to folder that will contain output frames
    # sample_rate -  number of frames per second to sample

    #create video capture object for the webcam
    cap = cv2.VideoCapture(0)   #0 corresponds to webcam
    if not cap.isOpened():
        print("Couldn't open webcam.")
        return
    
    video_fps = cap.get(cv2.CAP_PROP_FPS)  # get fps of video
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) #get frames of video
    print(f"video_fps, {video_fps}")
    print(f"frames, {frames}")
    print(f"samplerate 1, {sample_rate}")
    sample_rate = min(video_fps, sample_rate)   # cap sample_rate if it is higher than video fps
    print(f"samplerate 2, {sample_rate}")
    step = video_fps / sample_rate  # determine minimum space between each saved frame

    frame_digits = len(f"{frames}")
    frame_pos = 0
    ts = str(int(time.time())) # timestamp for unique filenames
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            if (frame_pos % step) < 1:
                # save the frame
                print(f"imwrite(...): {output_dir}/{ts}-f{frame_pos:0{frame_digits}}.png")
                cv2.imwrite(f"{output_dir}/{ts}-f{frame_pos:0{frame_digits}}.png", frame)
            cv2.imshow("op", frame) #display it for funzies
        if cv2.waitKey(1) == 27:
            #Esc to quit
            break
        frame_pos += 1 
    cap.release()

def sampleStreamCMDline(stream_address, sample_rate, output_path):
    # use ffmpeg commandline to sample frames from a live h264 stream within a folder
    # frames will be stored as PNGs for later steps in processing chain to read
    # Note that a much better implementation would be to sample a stream and save frames
    #   based on ffmpeg's "decode_video.c" example since it would be more efficient and 
    #   allow us to directly start the quality analysis when frames are extracted instead
    #   of polling for finished PNGs.   This would take a too much time at the moment, so
    #   rewrite this later if we need to.
    # stream_address - input udp address of the h264 stream
    # sample_rate    - specified fps to sample the stream at
    # output_path    - path to folder that will contain output pngs

    if output_path[-1:] != "/":
        output_path = output_path + "/"
    # %04d forces filename to be a number with 4 decimal places, padded with 0s. This will likely be unnecessary
    # if we access files directly when polling the folder since sorting the pngs would not be needed.
    os.system(f"ffmpeg -c:v h264 -i {stream_address} -vf fps={sample_rate} {output_path}sample-%d.png")

def getLiveFrames(path):
    # Function that repeatedly polls a directory looking for
    # new pngs (samples from livestream) and uses an observer to
    # process them when they are created, and delete them when the 
    # next sampled frame is available.  Modified from quickstart example in
    # Python watchdog library documentation
    # path - folder to watch for new pngs

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    event_handler = NewFrameEventHandler(patterns=['*.png'],
                                         n=5,
                                         ignore_directories=True)

    # Create, configure, and start the observer                                     
    observer = Observer()
    observer.schedule(event_handler, path)
    observer.start()
    # while loop so the user is able to interrupt execution
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def sampleStream(in_file, output_path):
    # uses python wrapper for ffmpeg commandline to sample frames from a 
    # live h264 stream ( or other input video ). frames will be stored as 
    # PNGs in a folder for later steps in processing chain to read
    # in_file        - input udp address of the h264 stream, or path to input video
    # output_path    - path to folder that will contain output pngs

    # Livestream testing procedure:
    # get another computer with ffmpeg cmd-line tool installed
    # identify ip address of computer receiving the stream and 
    # identify open udp port of computer receiving the stream
    # run this function on computer reciving the stream with udp address as
    # in_file and a chosen output folder as output_path
    # Example:  sampleStream('udp://10.0.0.30:9090', './temp/')
    # Next:
    # run following command on second computer (the one streaming to receiver)
    #   ffmpeg -list_devices true -f dshow -i dummy     
    # look for webcam device name in results of above command then run:
    #   ffmpeg -f dshow -i video="__DEVICENAMEHERE__" -vcodec libx264 -f h264 udp://__IPADDRESS__:__UDPPORT__
    # Example of above: ffmpeg -f dshow -i video="Integrated Webcam" -vcodec libx264 -f h264 udp://10.0.0.30:9090
    
    decoder = (
        ffmpeg
        .input(in_file)
        .filter('fps')
        .output(f'{output_path}frame-%d.png')
        .run()
    )
    decoder(in_file)

if __name__ == "__main__":
    #extractFrameLoop('./distortedVideos/','./distortedFrames/', 2)
    #extractFrameLoop('./temp/','./live-frames/', 2)
    #frames, step = extractFrames("./inputVideos/A026.mp4",2)
    #frames, step = extractFrames("./bitstream/Football-2.264",2)
    # frames, step = extractFrames("./save_video.mp4",2)
    # ts = str(int(time.time())) # timestamp for unique filenames

    # saveFrames(frames, step, ts, "./distortedFrames/")
    getLiveFrames("./raw-frames/")
    #sampleStream('udp://10.0.0.30:9090', './raw-frames/')