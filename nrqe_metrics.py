import os.path
import numpy as np
import cv2 #opencv
import statistics
from libsvm import svmutil
import brisque
import frameExtraction

def avgBrisque(input_frames):
    # input_frames  -  nparray that contains framedata
    brisq = brisque.BRISQUE()

    brisqueList = []
    for frame in input_frames:
        score = brisq.get_score(frame)
        #print(score)
        brisqueList.append(score)
    print("avg: ", statistics.fmean(brisqueList))
    print("var: ", statistics.variance(brisqueList))
    print("median: ",statistics.median(brisqueList))

def avgBrisqueLoop(input_path):
    # input_path  -  path to folder containing subfolders for each video 
    for folder in os.listdir(input_path):
        print("Folder: ", folder)
        avgBrisque(input_path + folder + "/")
        print("---------------")

def temporalFlickering(frame_array):
    #Paper talking about strategy: Measuring of Flickering Artifacts in Predictive Coded Video Sequences 
    #   Note that this strategy will not work for intra frame codecs since it seems focused on flickering
    #   due to the macroblock prediction in interframe encoding
    #
    #This function looks at macroblocks temporally, compare each macroblock to the
    #previous one in the same position, if there is a (mean squared) difference, 
    # consider it as having updates. If there is no difference, call it no change
    #if a macroblock rapidly switches between update and no update, it is 
    #possibly due to flickering. we want to measure that
    #To avoid overestimating flicker, only consider a block changing from
    #no update to update if the difference between its previous state to exceed
    #a threshold.  Additionally, once it has started updating, leave it in this 
    #state as long as there is any update, no matter how small
    #
    # the actual measurement of flickers would just be a count of state changes 
    # over maximum possible state changes during a time period
    # additionally, we could get average flicker for a set of macroblocks as the
    # number of state changes across all macroblocks in the set over the maximum 
    # number of state changes that could have occurred across all macroblocks during
    # the time period
    # We could then also get the maximum average flicker for all sets of macroblocks 
    # in a frame (e.g. divide a frame into multiple 3x3 sets of macroblocks, get
    # avg flicker for each set of 3x3, then get maximum of all sets as frame max)

    #adjusting thresh will massively affect how many flickers are counted since
    # thresh determines when a change is drastic enough to be considered a flicker
    # (flicker is when a block has enough changes to switch from static to updating,
    #  or when it switches back to static from updating, according to the paper)
    THRESH = 300
    BLOCK_SIDE = 3
    frames = []
    frameMSDs = []
    flickRatios = []
    flickSum = 0
    i = 0
    # big problem with the following for loop is it processes the 
    # frames in some order that is not the correct temporal order
    for frame in frame_array:
        luma = np.array(frame, copy=True)
        cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb, luma) #convert color format
        frames.append(luma)

        flickerRatio = 0
        if i != 0:
            msds = getMSDs(luma, frames[i-1], BLOCK_SIDE) #2d array of MSDs for each block in the frame
            flickerRatio = getFlickRatio(msds, frameMSDs[i -1], THRESH)
        else:
            width = len(luma)
            height = len(luma[0])
            msds = [[0 for k in range(0, height, BLOCK_SIDE)] for j in range(0, width, BLOCK_SIDE)]
        frameMSDs.append(msds)
        flickRatios.append(flickerRatio * 100) #multiply by 100 to do display as a percentage
        flickSum += flickerRatio
        print(f"Frame: {frame}  %Flicker: {flickerRatio * 100}")
        i += 1
    print(flickRatios)
    print(f"Avg %Flicker: {(flickSum * 100) / (i+1)}")

def getMSDs(current, previous, block_side):
    # current    - 2d array of luma values for the frame
    # previous   - 2d array of luma values for the previous frame
    # block_size - block size for identifying MSD
    # Returns blockMSDs - a 2d array of MSDs for each block in the frame
    width = len(current) 
    height = len(current[0])

    blockMSDs = []   
    for i in range(0, width, block_side):
        # blocks in the horizontal direction
        colMSDs = []
        for j in range(0, height, block_side):
            #blocks in the vertical direction
            sumSD = 0.0
            for x in range(0, block_side):
                #within the block
                for y in range(0, block_side):
                    sd = (int(current[i+x][j+y][0]) - int(previous[i+x][j+y][0])) ** 2 #square difference
                    sumSD += sd
            msd = sumSD / (block_side ** 2) #mean square difference
            colMSDs.append(msd)
        blockMSDs.append(colMSDs)
    return blockMSDs

def getFlickRatio(msds, prev_msds, thresh):
    #msds       - 2d array of mean square differences for each 
    #             block in the current frame
    #prev_msds  - 2d array of mean square differences for each 
    #             block in the previous frame
    #thresh     - value that a msds must surpass to be move from
    #             not updating state to updating state
    #Returns flickerRatio - a float from 0.0-1.0 indicating 
    #                       the % of blocks that flickered

    possibleCount = 0
    flickerCount = 0
    for j in range(len(msds)):
        # for each horizontal block
        for k in range(len(msds[0])):
            # for each vertical block
            if bool(prev_msds[j][k]) != bool(msds[j][k]):
                # if previous block MSD state (changing/unchanging) does not 
                # match current, we have a flicker when msd is 0, or msd > THRESH
                if (msds[j][k] == 0) or msds[j][k] > thresh:
                    flickerCount += 1
            possibleCount += 1  
    return flickerCount / possibleCount

frames, _ = frameExtraction.extractFrames("./inputVideos/A026.mp4", 2)
print(frames)
avgBrisque(frames)
temporalFlickering(frames)

