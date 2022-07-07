import argparse
import logging

import ffmpeg
import os.path
import csv

def bitstreamMetrics(in_file):
    """
        This function uses FFprobe to get the bitrate, framerate, and resolution of 
        a given video, stream, or other valid input to FFprobe (See: https://ffmpeg.org/ffprobe.html)

        in_file     - a string specifying the path to the file, url, or other input to be processed
        
        Returns: bitrate, framerate, resolution
            bitrate - integer containing the input's bitrate as reported by FFprobe
            framerate   - integer containing the input's framerate as reported by FFprobe
            resolution  - integer containing the result of width*height. width and height are as reported by FFprobe
    """

    ffprobeResults = os.popen(f"ffprobe -hide_banner -v error -of default=noprint_wrappers=1"
            f" -select_streams v:0 -show_entries stream=bit_rate,avg_frame_rate,width,height"
            f" {in_file}").read()

    width, height, framerate, bitrate = [i.split("=")[1] for i in ffprobeResults.split()]

    resolution = int(width) * int(height)

    numerator, denominator = framerate.split("/")
    framerate = int(numerator) / int(denominator)

    bitrate = int(bitrate)
    return bitrate, framerate, resolution

def main():
    from ffmpeg_streaming import FFProbe, ffprobe

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


if __name__ == "__main__":
    main()
    