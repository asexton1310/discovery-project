import argparse
import logging

import ffmpeg
from ffmpeg_streaming import FFProbe, ffprobe
import os.path
import csv

in_file = "A026.mp4"
output_path = "C:/Users/fireb/PycharmProjects/extract_metrics/rawframes/"



#os.system(f"ffprobe -hide_banner -v error -of default=noprint_wrappers=1"
#          f" -select_streams v:0 -show_entries stream=bit_rate"
#          f" {in_file}")


bit_rate = ["ffprobe","-v",in_file,"error","-of","default=noprint_wrappers=1",
            "-select_streams","v:0","-show_entries", "stream=bit_rate",
            ]


parameter = os.system(f"ffprobe -hide_banner -v error -of default=noprint_wrappers=1"
          f" -select_streams v:0 -show_entries stream=bit_rate,r_frame_rate,width,height"
          f" {in_file} > parameter.csv")

print(parameter)

header = ['Name', 'Bit Rate', 'Framerate', 'Width', 'Height']
#data = [in_file, bit_rate, r_frame_rate, width, height]


with open("bitstream.csv", 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(header)
    print(header)
   # print(data)

    # write the data
    #writer.writerow(data)

    f.close()

