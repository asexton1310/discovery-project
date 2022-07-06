#!/bin/bash
#
# The script takes the path to the folder with videofiles and/or images as the input and
# calculates all the metrics, additionaly storing the results in the CSV (Comma Separated Values) files
#
# Author: Jakub Nawala
# Modified: 7th June 2017

# Define ANSI escapes codes for the colorful fonts
RED='\033[0;31m'
L_RED='\033[1;31m' # light red
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
L_GREEN='\033[1;32m' # light green
L_PURPLE='\033[1;35m'
NC='\033[0m' # No Color

# Define the variable storing the current script name
PROGNAME=$(basename "$0")

# Define the function for the error handling
function error_exit {
#	----------------------------------------------------------------
#	Function for exit due to fatal program error
#		Accepts 1 argument:
#			string containing descriptive error message
#	----------------------------------------------------------------

	printf "\033[1;31m" # '\033[1;31m' sets the text color to light red
	printf "${PROGNAME}: ${1:-"Unknown Error"}\n" 1>&2
	printf "\033[0m" # '\033[0m' resets the color back to normal
	exit 3
}

# Check for the input validity
if [ -z "$1" -o -z "$2" ]; then
	printf "${L_RED}ERROR: Not enough parameters${NC}\n\n"
	printf "  ${YELLOW}Usage:\n"
	printf "\t${PROGNAME} <folder_path> <path_to_vqi_binary>\n\n${NC}"
	printf "NOTE: the <folder_path> shall point to the folder containing video or image files.\n"
	printf "      Please keep in mind that script does work recursively so all nested folders\n"
	printf "      and their content will be processed.\n\n"
	printf "      <path_to_vqi_binary> marks the path to video quality indicators binary. It does not \n"
	printf "      matter whether it is single, or multi threaded version.\n\n"
	printf "      Output of the script will be stored in the folder created according to the following\n"
	printf "      syntax:\n\n"
	printf "      \tmitsu_metrics<year><month><day>\n\n"
	printf "      Each video or image file will have its respective *.csv file with the metrics' results.\n"
	printf "      What is more, all the results will be concatenated and stored in the file created \n"
	printf "      according to the following syntax:\n\n"
	printf "      \tresults-all_<year><month><day><hour><minutes><seconds>.csv\n\n"
	exit
fi

# Make the directory for the output files
DIR=".TA_metrics_01"
mkdir -p $DIR
# cd $DIR

# Create a file for storing all the results
ALL_FILE="results-all_01.csv"
touch $ALL_FILE

# Read the folder path with the clips
FOLDER="$1"
if [ "${FOLDER}" = "." ]; then
	FOLDER=""
fi
# Read the binary file
EXECUTABLE="$2"

# Changing the IFS to enable processing of filenames containing spaces
SAVEIFS=$IFS
# IFS=$(echo -en "\n\b")

# Iterate over the files in the source folder
# for VIDEOFILE in $(ls ../"${FOLDER}"); do
find "${FOLDER}" -print0 | while IFS= read -r -d '' VIDEOFILE
do
	# Skip the calculations if the file is a directory
	if [ -d "${VIDEOFILE}" ]; then
		printf "${NC}"
	elif [ "${VIDEOFILE##*.}" = "yuv" ]; then
		printf "${YELLOW} $VIDEOFILE is in a RAW format -> skip it...${NC}\n"
	elif [ "${VIDEOFILE##*.}" = "txt" -o "${VIDEOFILE##*.}" = "csv" ]; then
		printf "${YELLOW} $VIDEOFILE is a text file -> skip it...${NC}\n"
	else
		# Do somehting if the file is the videofile
		# Extracting the sole filename (w/o the path)
		FILENAME=$(basename "${VIDEOFILE}")

		# Read the dimensions of the video frame and the FPS
		WIDTH="$(ffprobe -v error -show_entries stream=width -of default=noprint_wrappers=1:nokey=1 \
			"$VIDEOFILE")" || error_exit "$LINENO: ffmpeg couldn't read the width of the file! Aborting!"
		# Make sure that there is only one width read
		set -- $WIDTH
		WIDTH=$1
		HEIGHT="$(ffprobe -v error -show_entries stream=height -of default=noprint_wrappers=1:nokey=1 \
			"$VIDEOFILE")" || error_exit "$LINENO: ffmpeg couldn't read the height of the file! Aborting!"
		# Make sure that there is only one height read
		set -- $HEIGHT
		HEIGHT=$1
		# If file is the photo, ommit the FPS calculus
		EXTENSION="${VIDEOFILE##*.}"
		if [ "$EXTENSION" = "png" -o "$EXTENSION" = "PNG" -o "$EXTENSION" = "jpg" \
			-o "$EXTENSION" = "JPG" \-o "$EXTENSION" = "jpeg" -o "$EXTENSION" = "JPEG" \
			-o "$EXTENSION" = "bmp" -o "$EXTENSION" = "BMP" ]; then
			FPS=1
		else
			FPS=$(ffprobe -v error -select_streams v:0 -show_entries stream=avg_frame_rate \
			-of default=noprint_wrappers=1:nokey=1 "$VIDEOFILE") \
			|| error_exit "$LINENO: ffmpeg couldn't read the FPS of the file! Aborting!"
			FPS=$(echo "scale=2; $FPS" | bc) # reduce the FPS to 2 digits after dot precision
			# Make sure that there is only one FPS read
			set -- $FPS
			FPS=$1
		fi
		# Convert the file to the yuv format and save the ffmpeg output to the log file
		YUV="${FILENAME}.yuv"
		LOGFILE="ffmpeglog-${FILENAME}-$(date +%Y%m%d%H%M%S).txt"
		< /dev/null ffmpeg -i "$VIDEOFILE" -pix_fmt yuv420p -hide_banner -y "$YUV" &> "$LOGFILE"

		# Calculate the metrics on the file and save the output in the results.txt
		RESULTS="results-${FILENAME}.csv"
		OUTPUT="out.txt"
		"$EXECUTABLE" "$YUV" $WIDTH $HEIGHT $FPS > $OUTPUT
		cat $OUTPUT | grep 'Calculation time'
		cat $OUTPUT | grep 'milliseconds per frame'
		rm $OUTPUT
		mv metricsResultsCSV.csv "$RESULTS"

		# Append the results to the one big file
		echo ${FILENAME} >> $ALL_FILE
		cat $RESULTS >> $ALL_FILE

		# Move the results to one common folder
		#mv "${RESULTS}" "${DIR}"

		# Remove the uncompressed file
		rm "$YUV"
		rm "${LOGFILE}"
		rm "${RESULTS}"
	fi
done

# Move the concatenated results to one common folder
mv "$ALL_FILE" "$DIR"

# Loading IFS variable with the default value
IFS=$SAVEIFS
exit
