"""
Reference: https://github.com/VQEG/siti-tools
MIT License
siti_tools, Copyright (c) 2021-2022 Werner Robitza, Lukas Krasula
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import numpy as np
from siti_tools.siti import SiTiCalculator
from typing import Generator
import av
from matplotlib import image
from os import path


def singleFrameSiTi(targetFrame, prevFrame):
    # Function calculate the spatial information and temporal information
    # Require input is a single frame and prior frame in np array format
    siValue = SiTiCalculator.si(targetFrame)
    tiValue = SiTiCalculator.ti(targetFrame, prevFrame)

    return siValue, tiValue


def calculateSiTi(setOfFrame):
    # Function calculate the spatial information and temporal information
    # Require input as a set of Frame's name
    setOfTi = []
    setOfSi = []
    previousFrame = None
    for frame in setOfFrame:
        firstFrame = image.imread(frame)
        siValue, tiValue = singleFrameSiTi(firstFrame, previousFrame)
        previousFrame = firstFrame
        setOfSi.append(siValue)
        setOfTi.append(tiValue)
    return setOfSi, setOfTi


def read_container(input_file: str) -> Generator[np.ndarray, None, None]:
    """
    Modification of the read_container generator included in the siti tools library
    by Wener Robitza and Lukas Krasula available at: ttps://github.com/VQEG/siti-tools
    This modification was made to support input videos where a plane's line_size does 
    not match the plane's width. This occurs when videos are encoded with padding.

    Read a multiplexed file via ffmpeg and yield the per-frame Y data.

    This method tries to be clever determining the bit depth and decoding the
    data correctly such that content with >8bpp is returned with the full range
    of values, and not 0-255.

    Args:
        input_file (str): Input file path

    Raises:
        RuntimeError: If no video streams were found or decoding was not possible

    Yields:
        np.ndarray: The frame data, integer
    """
    if "yuv" in path.splitext(input_file)[1]:
        import re
        full_fps = input_file.split("_")[-2]
        fps = re.sub("[^0-9]", "", full_fps)

        container = av.open(input_file, format="rawvideo", options={
                            "vcodec": "rawvideo", "video_size": "3840x2160", "framerate": fps, "pix_fmt": "yuv420p"})
    else:
        container = av.open(input_file)

    if not len(container.streams.video):
        raise RuntimeError("No video streams found!")

    for frame in container.decode(video=0):
        # FIXME: this has been determined experimentally, not sure if it is the
        # correct way to do that -- the return values seem correct for a white/black
        # checkerboard pattern
        if "yuv" not in str(frame.format.name):
            raise RuntimeError(
                f"Decoding not yet possible for format {frame.format.name}! Only YUV is supported.")

        if "p10" in str(frame.format.name):
            datatype = np.uint16
            bytes_per_pixel = 2
        elif "p12" in str(frame.format.name):
            datatype = np.uint16
            bytes_per_pixel = 2
        else:
            datatype = np.uint8
            bytes_per_pixel = 1

        try:
            plane = frame.planes[0]
            total_line_size = abs(plane.line_size)
            useful_line_size = plane.width * bytes_per_pixel
            arr = np.frombuffer(plane, np.uint8)
            if total_line_size != useful_line_size:
                arr = arr.reshape(-1,
                                  total_line_size)[:, 0:useful_line_size].reshape(-1)
            arr.view(np.dtype(datatype))
            yield (
                # The code commented out below does the "standard" conversion of YUV
                # to grey, using weighting, but it does not actually use the correct
                # luminance-only Y values.
                # frame.to_ndarray(format="gray")

                # choose the Y plane (the first one)
                arr.view(np.dtype(datatype))
                .reshape(frame.height, frame.width).astype("int")
            )
        except ValueError as e:
            raise RuntimeError(
                f"Cannot decode frame. Have you specified the bit depth correctly? Original error: {e}"
            )


def videoSiTi(inputVid):
    previous_frame_data = None
    frame_generator = read_container(inputVid)
    frame_cnt = 1

    si_sum = ti_sum = 0
    calc = SiTiCalculator(color_range="full", bit_depth=10)
    for frame_data in frame_generator:
        si_value = calc.si(frame_data)
        ti_value = calc.ti(frame_data, previous_frame_data)

        si_sum += si_value

        if ti_value is None:
            ti_value = ""
        else:
            ti_sum += ti_value

        frame_cnt += 1
        previous_frame_data = frame_data
    avg_si = si_sum / frame_cnt
    avg_ti = ti_sum / frame_cnt

    # normalize si, ti, by dividing by 255 since output ranges are 0-255
    return([avg_si / 255, avg_ti / 255])


if __name__ == "__main__":
    #setOfFrame = ["098.png", "104.png"]
    # print(calculateSiTi(setOfFrame))
    print(videoSiTi("./inputVideos/A026.mp4"))
