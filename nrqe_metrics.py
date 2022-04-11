# This script should eventually calculate brisque, niqe, and maybe piqe
# https://pypi.org/project/pybrisque/
# Usage
#Initialize once:   brisq = BRISQUE()
#and get the BRISQUE feature or score many times:   brisq.get_feature('/path')  
#                                                   brisq.get_score('/image_path')

import os.path
import statistics
from libsvm import svmutil
import brisque

#should make a loop to extract sample images from a video into a single folder
#   -- this was already done in error_generator.py

#   then iterate over that folder getting BRISQUE for each sample image
#   use simple avg as a single BRISQUE score
#   higher scores correspond to higher quality

def avgBrisque(input_path):
    # input_path  -  path to folder containing input images
    brisq = brisque.BRISQUE()

    brisqueList = []
    for filename in os.listdir(input_path):
        score = brisq.get_score(input_path + filename)
        #print(score)
        brisqueList.append(score)
    print("avg: ", statistics.fmean(brisqueList))
    print("var: ", statistics.variance(brisqueList))
    print("median: ",statistics.median(brisqueList))

avgBrisque("./distortedFrames/Football-2-1649626110-cvSnP-frames/")