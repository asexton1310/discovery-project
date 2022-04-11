# This script extracts bitstream parameters from an h.264 bitstream

import os.path

def encodeH264stream(in_filename, output_path):
    # use ffmpeg to encode a video as h264 bitstream with default settings
    #   and store the encoded bitstream in local file
    # in_filename  -  name of input video
    # output_path  -  path to folder that will contain subfolder containing output frames

    in_fname, ext = os.path.splitext(in_filename) # split extension off input path and filename
    in_fname = os.path.basename(in_fname)         # remove the path to only have filename
    output_filename = output_path + in_fname + ".264"
        
    os.system("ffmpeg -i {0} -c:v libx264 -y -f h264 {1}".format(in_filename, output_filename))

def extractH264streamParams(in_filename, output_path):
    # extract stream & codec parameters and output them to a file
    # in_filename  -  name of input video
    # output_path -  path to folder that will contain subfolder containing output frames

    in_fname, ext = os.path.splitext(in_filename) # split extension off input path and filename
    in_fname = os.path.basename(in_fname)         # remove the path to only have filename
    output_filename = output_path + in_fname + ".txt"

    #os.system("ffprobe -show_streams -i {0} -of csv=p=0 > {1}".format(in_filename, output_filename))     # for csv results
    os.system("ffprobe -show_streams -i {0} -of default=nw=1 > {1}".format(in_filename, output_filename)) # for human readable results

encodeH264stream('./inputVideos/Football-2.mp4', './bitstream/')
extractH264streamParams('./bitstream/Football-2.264', './bitstream/')