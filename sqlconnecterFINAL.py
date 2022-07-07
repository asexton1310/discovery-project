#Juan Merlos ED2
#must import mysql.connector and mysql.connector-python in python enviorment
#install pip if you don't have it already
#command: pip install virtualenv
#create virtual enviorment with virtualenv "name" - make sure your terminal directory is in project folder
#activate enviorment with "name"/Scripts/activate
#then install the connector using the commands: pip install mysql-connector and pip install mysql-connector-python
from logging import raiseExceptions
import mysql.connector
import random
import time

#The Stream class will handle all the data as well as hanlde the SQL injection (updating)

class Stream:
    def __init__(self, connectionDB, stream_id, location_id):
        try:
            self.connectionDB = connectionDB
            self.status = 1
            self.stream_id = stream_id
            self.location_id = location_id
            self.datapoints = {
                "bitrate": None,
                "framerate": None,
                "resolution": None,
                "avg_blockiness": None,
                "max_blockiness": None,
                "min_blockiness": None,
                "avg_blur": None,
                "max_blur": None,
                "min_blur": None,
                "avg_contrast":	None,
                "max_contrast":	None,
                "min_contrast": None,
                "avg_color": None,	
                "max_color": None,	
                "min_color": None,	
                "avg_ltp": None,
                "max_ltp": None,
                "min_ltp": None,
                "avg_noise": None,	
                "max_noise": None,	
                "min_noise": None,	
                "avg_brisque": None,
                "max_brisque": None,	
                "min_brisque": None,	
                "avg_flicker": None,	
                "avg_flickering_agh": None,	
                "avg_blockiness_agh": None,	
                "avg_letterBox_agh": None,	
                "avg_pillarBox_agh": None,	
                "avg_blockloss_agh": None,	
                "avg_blur_agh": None,
                "avg_blackout_agh": None,
                "avg_freezing_agh": None,	
                "avg_exposure_agh": None,	
                "avg_contrast_agh": None,	
                "avg_interlace_agh": None,	
                "avg_noise_agh": None,	
                "avg_si_agh": None,	
                "avg_ti_agh": None,
                "quality_estimate": None
              }
 
            self.logstring = ""
            print("connection obj: ", self.connectionDB, "/n CLASS initialization data:")
            print(self.toString())
        except Exception as e:
            raise Exception("There was an error initializing the class: ", e)
    
    #this function will inizialize the database with the inizialization data
    def initializeDB(self):
        try: 
            cursor = self.connectionDB.cursor()
            query = """INSERT INTO final_tblv2 (entry_id, status_on, stream_id, location_id) 
                           VALUES 
                           (%s, %s, %s, %s) """
            #the 0 updates by itself server side NO TOUCH
            record = (0, self.status, str(self.stream_id), str(self.location_id), )
            cursor.execute(query, record)
            self.connectionDB.commit()
            cursor.close()
            print("\n*************************************\n")
            print("DATABASE entry has been successfully intitialized to the following data: ")
            print(self.toString())
        except mysql.connector.Error as error:
            print("Failed to inizialize database in table {}".format(error))

    
    #update datapoints in SQL
    def injectData(self):
        try:
            cursor = self.connectionDB.cursor()
            metrics = ""
            for metric in self.datapoints:
                if (self.datapoints[metric] != None):
                    metrics = metrics + str(metric) + " = " + str(self.datapoints[metric]) + ", "
            metrics =  metrics[:-2]#remove last comma
            metrics = metrics + " "
            metrics = metrics + "WHERE status_on = " + str(self.status) + " AND stream_id = '" + str(self.stream_id) + "' AND location_id = '" + str(self.location_id)+"'"
            cursor = self.connectionDB.cursor()
            sql = "UPDATE final_tblv2 SET " + str(metrics)
            #print(str(sql))
            cursor.execute(sql)
            self.connectionDB.commit()      
            cursor.close()
            
            print("\n*************************************\n")
            print("DATABASE entry has been successfully updated to the following data where stream is on: ")
            print(self.toString())
        except Exception as e:
            raise Exception("There was an error injecting the data: ", e)
    
    def updateLogString(self, log_string):
        try:
            self.logstring += log_string 
        except Exception as e:
            raise Exception("There was an error updating logstring: ", e)
    
    def injectLogString(self):
        try:
            cursor = self.connectionDB.cursor()
            sql = "UPDATE final_tblv2 SET log_string = %s WHERE stream_id = %s AND location_id = %s"
            values = (str(self.logstring), str(self.stream_id), str(self.location_id))
            cursor.execute(sql, values)
            self.connectionDB.commit()
            cursor.close()
            print("Stream ", self.stream_id, "Location ", self.location_id, " Offline")
        except Exception as e:
            raise Exception("There was an error injecting logstring: ", e)
    
    #bring stream offline
    def offline(self):
        try:
            cursor = self.connectionDB.cursor()
            sql = "UPDATE final_tblv2 SET status_on = 0 WHERE stream_id = %s AND location_id = %s"
            values = (str(self.stream_id), str(self.location_id))
            cursor.execute(sql, values)
            self.connectionDB.commit()
            cursor.close()
            print("Stream ", self.stream_id, "Location ", self.location_id, " Offline")
        except Exception as e:
            raise Exception("There was an error turning stream offline: ", e)
    
    #stream starts online use only if needed
    def online(self):
        try:
            cursor = self.connectionDB.cursor()
            sql = "UPDATE final_tblv2 SET status_on = 1 WHERE stream_id = %s AND location_id = %s"
            values = (str(self.stream_id), str(self.location_id))
            cursor.execute(sql, values)
            self.connectionDB.commit()
            cursor.close()
            print("Stream ", self.stream_id, "Location ", self.location_id, " Online")
        except Exception as e:
            raise Exception("There was an error turning stream online: ", e)
    
    def closeDBstream(self):
        self.connectionDB.close()
    
    def toString(self):
         try:
             title = "status | stream_id | location_id | data1 - data(n) || logstring\n\n"
             datapointsstr = ""
             for metric in self.datapoints:
                datapointsstr = datapointsstr + str(self.datapoints[metric]) + " | "
             return title + " | " + str(self.status) + " | " + str(self.stream_id) + " | " \
                + str(self.location_id) + " | " + datapointsstr + " ||\n " + str(self.logstring)

         except Exception as e:
             return "data return error" + e

    def streamExists(self):
        try:
            cursor = self.connectionDB.cursor(buffered=True)
            sql = "SELECT stream_id FROM final_tblv2 WHERE stream_id = %s"
            values = (str(self.stream_id), )
            cursor.execute(sql, values)
            self.connectionDB.commit()
            existing = ""
            for (exists, ) in cursor:
               existing = exists
            cursor.close()
            if(existing == ""):
                return 0
            else:
                return 1
        except Exception as e:
            print(e)




def connectSQL():
    try:
        connectionDB = mysql.connector.connect(user='admin', password='#', database='video_analysis_db',
                              host='#',
                       )
        print("Connection String Opened successfully")
        mainRunTime(connectionDB)
        connectionDB.close()
    except Exception as e:
        print("**ERROR HAS OCCURED**: This was your error: ", e)
        print("Make sure the username and password and hostname are correct. If the database is offline contact your server admin (Juan)")

def mainRunTime(connectionDB):
  
    stream_id = "streamid025" #local team responsible for this variable***
    location_id = 1 ##local team responsible for this variable***
    stream1 = Stream(connectionDB, stream_id, location_id)
    #stream1.streamExists()#make sure that your stream id is uniuque if adding new stream
    #TO UPDATE DATA USE THE self.datapoints dictionary: Example class.datapoints.update({'bitrate': 20.25}) - to view the dictionary values reference line 20 - to update table value as null inject "Null" string
    #stream1.online()
    #stream1.initializeDB()
    #cycles = 20
    #while cycles != 0:
        #stream1.datapoints.update({'bitrate': "Null", 'framerate': random.randint(0,60), 'resolution': 720, 'avg_blockiness': random.randint(0, 100)})
        #stream1.injectData()
        #time.sleep(1)
        #cycles = cycles - 1
    
    #stream1.updateLogString("hello")
    #stream1.injectLogString()
    #stream1.offline()
    #V MAIN CODE SEGMENT HERE V#    




    #^ MAIN CODE SEGMENT HERE ^#
    stream1.closeDBstream()#close the DB for whatever class you open a stream with (optional)



if __name__ == '__main__':
    connectSQL()
