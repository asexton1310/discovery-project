from operator import ne
import os
import csv
import numpy as np 

#This tool is based on Paper Modeling of quality of experience in no-reference model 
#Reference URL: https://www.researchgate.net/publication/318506730_Modeling_of_Quality_of_Experience_in_No-Reference_Model

######Intruction########:
#Use the link below to download Single executable based on OS.
#DO NOT put the mitsuScript.sh, Single executable, and this python file into Video folder. Keep it outside that input video folder. 
#Replace input folder with the Name of folder contain video and inputScript with the Name of Single executable
#Depend on the OS the Single executable must change permission by do: chmod 777 <nameOfTheScript> 

#https://qoe.agh.edu.pl/indicators/#:~:text=List%20of%20implemented%20indicators%3A%20%20%20Indicators%20,%20%20%20%2011%20more%20rows%20

######################################

#This function extract 13/15 metrics from the AGH tool , 
#2 metrics Temporal Activity and Spatial Activity will use the tools suggested from professor Kalva.
#Require inputFolder's Name and inputScript's Name
def extractMetrics(inputFolder, inputScript):
    #run the script to calculate all metrics
    os.system(f"mitsuScriptWin.bat {inputFolder} {inputScript}")
    row=[]
    listOfTA, listOfFlicker, listOfBlockiness, listOfLetterbox,	listOfPillarbox  =[],[],[],[],[]
    listOfBlockloss, listOfBlur, listOfBlackout, listOfFreezing, listOfExposure =[],[],[],[],[]
    listOfContrast, listOfInterlace, listOfNoise, listOfSlice=[],[],[],[]
    numberOfDecimal=5

    #extract Metrics Data from ouput file
    with open('./mitsu/metricsResultsCSV.csv') as fileObj:
        readerCSV = csv.reader(fileObj)
        for item in readerCSV:
            row.append(item)

    for i in range(2, len(row)):
        singleRow = row[i]
        for item in singleRow:
            #It depend on team choice to decide whether we use this Temporal Activity from this tool 
            #or the tool from Dr Kalva suggest
            #singleTA = item.split('\t')[7]
            #listOfTA.append(float("".join(singleTA)))

            singleFlicker = item.split('\t')[15]
            singleFlickerToFloat = float("".join(singleFlicker))
            if singleFlickerToFloat != -1:
                listOfFlicker.append(singleFlickerToFloat)

            singleBlockiness = item.split('\t')[1]
            listOfBlockiness.append(float("".join(singleBlockiness)))

            singleLetterBox = item.split('\t')[3]
            listOfLetterbox.append(float("".join(singleLetterBox)))

            singlePillarbox = item.split('\t')[4]
            listOfPillarbox.append(float("".join(singlePillarbox)))

            singleBlockloss = item.split('\t')[5]
            listOfBlockloss.append(float("".join(singleBlockloss)))

            singleBlur = item.split('\t')[6]
            listOfBlur.append(float("".join(singleBlur)))

            singleBlackout = item.split('\t')[8]
            listOfBlackout.append(float("".join(singleBlackout)))

            singleFreezing = item.split('\t')[9]
            listOfFreezing.append(float("".join(singleFreezing)))

            singleExposure = item.split('\t')[10]
            listOfExposure.append(float("".join(singleExposure)))

            singleContrast = item.split('\t')[11]
            listOfContrast.append(float("".join(singleContrast)))

            singleInterlace = item.split('\t')[12]
            listOfInterlace.append(float("".join(singleInterlace)))
            
            singleNoise = item.split('\t')[13]
            listOfNoise.append(float("".join(singleNoise)))
            
            singleSlice = item.split('\t')[14]
            listOfSlice.append(float("".join(singleSlice)))
            
    #tA = round(np.average(normalizeOutput(listOfTA)),numberOfDecimal)
    norm_flickering =  quickNormalize(np.average(listOfFlicker), 8, 0)
    norm_blockiness =  quickNormalize(np.average(listOfBlockiness), 3570, 0)
    norm_letterBox = quickNormalize(np.average(listOfLetterbox), 1, 0)
    norm_pillarBox = quickNormalize(np.average(listOfPillarbox), 1, 0)
    norm_blockloss = quickNormalize(np.average(listOfBlockloss), 200, 0)
    norm_blur = quickNormalize(np.average(listOfBlur), 70, 0)
    norm_blackout = quickNormalize(np.average(listOfBlackout), 1, 0)
    norm_freezing = quickNormalize(np.average(listOfFreezing), 1, 0)
    norm_exposure = quickNormalize(np.average(listOfExposure), 255, 0)
    norm_contrast = quickNormalize(np.average(listOfContrast), 120, 0)
    norm_interlace = quickNormalize(np.average(listOfInterlace), 1, 0)
    norm_noise = quickNormalize(np.average(listOfNoise), 30, 0)
    norm_slices = np.average(listOfSlice)

    flickering =  round(norm_flickering,numberOfDecimal)
    blockiness =  round(norm_blockiness,numberOfDecimal)
    letterBox = round(norm_letterBox,numberOfDecimal)
    pillarBox = round(norm_pillarBox,numberOfDecimal)
    blockloss = round(norm_blockloss,numberOfDecimal)
    blur = round(norm_blur,numberOfDecimal)
    blackout = round(norm_blackout,numberOfDecimal)
    freezing = round(norm_freezing,numberOfDecimal)
    exposure = round(norm_exposure,numberOfDecimal)
    contrast = round(norm_contrast,numberOfDecimal)
    interlace = round(norm_interlace,numberOfDecimal)
    noise = round(norm_noise,numberOfDecimal)
    slices = round(norm_slices,numberOfDecimal)

    return [flickering, blockiness, letterBox, pillarBox, blockloss, blur, blackout, freezing, exposure, contrast, interlace, noise, slices]


def normalizeOutput(arrayOuput):
	normalizedTA =[]
	for i in range(len(arrayOuput)):
		num = arrayOuput[i]
		oldValue = num
		oldMin, oldMax = 0,255
		newMin, newMax = 0,1
		newValue = ((oldValue - oldMin) / (oldMax - oldMin)) * \
			(newMax - newMin) + newMin	
		#append normalized value to list
		normalizedTA.append(round(newValue, 5))
	return normalizedTA

def quickNormalize(oldValue, oldMax, oldMin):
    newMin, newMax = 0,1
    newValue = ((oldValue - oldMin) / (oldMax - oldMin)) * \
        (newMax - newMin) + newMin	
    return newValue


if __name__ == "__main__":
    inputFolder = f'{os.path.abspath("./live-test/A026.mp4")}'
    inputScript = os.path.abspath("./Calculate_AGH_Metrics/mitsuWin64.exe")
    #flickering, blockiness, letterBox, pillarBox, blockloss, blur, blackout, freezing, exposure, contrast, interlace, noise, slice = extractTemporalActivity(inputFolder, inputScript)
    print(f"a {inputFolder}, b {inputScript}")

    print("flickering, blockiness, letterBox, pillarBox, blockloss, blur, blackout, freezing, exposure, contrast, interlace, noise, slices \n" ,extractMetrics(inputFolder, inputScript))
