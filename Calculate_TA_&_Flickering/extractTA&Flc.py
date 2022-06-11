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

#Require inputFolder's Name and inputScript's Name
def extractTemporalActivity(inputFolder, inputScript):
	#run the script to calculate Temporal Activity
	#TA as Temporal Activity
	os.system("bash mitsuScript.sh "+ "./"+inputFolder+ " ./"  + inputScript)
	row=[]
	listOfTA=[]
	indexTA=7

	#extract TA Data from ouput file
	with open('./.TA_metrics_01/results-all_01.csv') as fileObj:
		readerCSV = csv.reader(fileObj)
		for item in readerCSV:
			row.append(item)

	for i in range(2, len(row)):
		singleRow = row[i]
		for item in singleRow:
			singleTA = item.split('\t')[indexTA]
			listOfTA.append(float("".join(singleTA)))

	#This will return into a single score of Temporal Activity 
	#for a single input video
	return round(np.average(normalizeOutput(listOfTA)),5)



def extractFlickering():
	listOfFlicker=[]
	row=[]
	indexFlickering=15
	#extract Flickering Data from ouput file
	with open('./.TA_metrics_01/results-all_01.csv') as fileObj:
		readerCSV = csv.reader(fileObj)
		for item in readerCSV:
			row.append(item)
	for i in range(2, len(row)):
		singleRow = row[i]
		for item in singleRow:
			singleFlicker = item.split('\t')[indexFlickering]
			singleFlickerToFloat = float("".join(singleFlicker))
			if singleFlickerToFloat != -1:
				listOfFlicker.append(singleFlickerToFloat)

	#This will return into a single score of Flickering
	#for a single input video
	return round(np.average(listOfFlicker),5)


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



if __name__ == "__main__":
	inputFolder = "inputVideo"
	inputScript ="mitsuLinux"
	singleTA=extractTemporalActivity(inputFolder, inputScript)
	flickering = extractFlickering();
	
	print("Normalized List of TA: ", singleTA)
	print("\n List of Flickering: ", flickering)
