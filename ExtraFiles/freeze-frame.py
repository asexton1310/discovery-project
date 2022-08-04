import cv2
import brisque


# FOR THE freeze_frame METRIC, YOU ONLY NEED TO ADD THE if STATEMENT IN LINE 18 and
# else STATEMENT AT LINE 27.
def freeze_frame_ex(framesfolder_path, vidname, csv_out):
    brisq = brisque.BRISQUE()
    # lists of each frame's metrics
    brisque_list = []
    csv3 = []  # This will be the list I am sending to the output of the Pipe
    # list of each frame's pixel values
    frame_data = []
    frame_list = os.listdir(framesfolder_path)
    frame_list.sort()
    frame_prev = 1000
    start_time = time.perf_counter()
    freeze_frame = 0 # counts no. of freeze_frame
    framecount = 0 # counts no. of frames
    for frame in frame_list:
        framecount = framecount + 1
        # some metrics require frame to already be read with opencv
        full_path = framesfolder_path + frame
        cv_frame = cv2.imread(full_path)
        frame_data.append(cv_frame)
        # for freeze frame metric check, just add this if statement below.
        if abs(np.mean(frame_prev) - np.mean(cv_frame)) > 0.003:  # checks for freeze-frame
            frame_prev = cv_frame
            brisque_list.append(brisq.get_score(cv_frame) / 100)
        else:  # freeze frame occured
            freeze_frame = freeze_frame + 1
            frame_data.append(cv_frame)
            brisque_list.append(brisque_list[len(brisque_list)-1])
    freeze_frame_metric = freeze_frame/framecount
    #add freeze_frame_metric to CSV file.
    return


if __name__ == "__main__":
    freeze_frame_ex()
