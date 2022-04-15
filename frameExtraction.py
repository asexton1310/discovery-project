import time
import os.path
import cv2 #opencv
import numpy as np

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
        print(f"imwrite(...): {output_dir}/{filename}-f{frame_pos:0{digits}}.png")
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

if __name__ == "__main__":
    #extractFrameLoop('./distortedVideos/','./distortedFrames/', 2)
    #extractFrameLoop('./temp/','./live-frames/', 2)
    frames, step = extractFrames(0,2)
    ts = str(int(time.time())) # timestamp for unique filenames

    saveFrames(frames, step, ts, "./temp/")
