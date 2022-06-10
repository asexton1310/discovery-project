#Juan Merlos ED2
#must import mysql.connector and mysql.connector-python in python enviorment
#install pip if you don't have it already
#command: pip install virtualenv
#create virtual enviorment with virtualenv "name" - make sure your terminal directory is in project folder
#activate enviorment with "name"/Scripts/activate
#then install the connector using the commands: pip install mysql-connector and pip install mysql-connector-python
from logging import raiseExceptions
import mysql.connector

#The Stream class will handle all the data as well as hanlde the SQL injection (updating)

class Stream:
    def __init__(self, connectionDB, stream_id, location_id):
        try:
            self.connectionDB = connectionDB
            self.status = 1
            self.stream_id = stream_id
            self.location_id = location_id
            self.data1 = 0
            self.data2 = 0
            self.data3 = 0
            self.data4 = 0
            self.data5 = 0
            self.logstring = ""
            print("connection obj: ", self.connectionDB, "/n CLASS initialization data:")
            print(self.toString())
        except Exception as e:
            raise Exception("There was an error initializing the class: ", e)
    
    #this function will inizialize the database with the inizialization data
    def initializeDB(self):
        try: 
            cursor = self.connectionDB.cursor()
            query = """INSERT INTO test_tbl (entry_id, status_on, stream_id, location_id, data_1, data_2, data_3, data_4, data_5, log_string) 
                           VALUES 
                           (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
            #the 0 updates by itself server side NO TOUCH
            record = (0, self.status, self.stream_id, self.location_id, self.data1, self.data2, self.data3, self.data4, self.data5, self.logstring)
            cursor.execute(query, record)
            self.connectionDB.commit()
            cursor.close()
            print("\n*************************************\n")
            print("DATABASE entry has been successfully intitialized to the following data: ")
            print(self.toString())
        except mysql.connector.Error as error:
            print("Failed to inizialize database in table {}".format(error))

    
    #the updata data function will update all data values within the class, use in conjunction with injectData to send data to SQL
    def updateData(self, data1, data2, data3, data4, data5):
        try:
            self.data1 = data1
            self.data2 = data2
            self.data3 = data3
            self.data4 = data4
            self.data5 = data5
            print("CLASS data updated successfully")
        except Exception as e:
            raise Exception("There was an error updating the data: ", e)
    
    #update datapoints in SQL
    def injectData(self):
        try:
            cursor = self.connectionDB.cursor()
            
            sql = "UPDATE test_tbl SET data_1 = %s WHERE status_on = %s AND stream_id = %s AND location_id = %s"
            values = (self.data1, 1, self.stream_id, str(self.location_id))
            cursor.execute(sql, values)
            
            sql = "UPDATE test_tbl SET data_2 = %s WHERE status_on = %s AND stream_id = %s AND location_id = %s"
            values = (self.data2, 1, self.stream_id, str(self.location_id))
            cursor.execute(sql, values)
            
            sql = "UPDATE test_tbl SET data_3 = %s WHERE status_on = %s AND stream_id = %s AND location_id = %s"
            values = (self.data3, 1, self.stream_id, str(self.location_id))
            cursor.execute(sql, values)
            
            sql = "UPDATE test_tbl SET data_4 = %s WHERE status_on = %s AND stream_id = %s AND location_id = %s"
            values = (self.data4, 1, self.stream_id, str(self.location_id))
            cursor.execute(sql, values)
            
            sql = "UPDATE test_tbl SET data_5 = %s WHERE status_on = %s AND stream_id = %s AND location_id = %s"
            values = (self.data5, 1, self.stream_id, str(self.location_id))
            cursor.execute(sql, values)
            
            self.connectionDB.commit()
            cursor.close()
            
            print("\n*************************************\n")
            print("DATABASE entry has been successfully updated to the following data where stream is on: ")
            print(self.toString())
        except Exception as e:
            raise Exception("There was an error injecting the data: ", e)
    
    def updateLogString(self, log_string):
        try:
            self.logstring = log_string
        except Exception as e:
            raise Exception("There was an error updating logstring: ", e)
    
    def injectLogString(self):
        try:
            cursor = self.connectionDB.cursor()
            sql = "UPDATE test_tbl SET log_string = %s WHERE stream_id = %s AND location_id = %s"
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
            sql = "UPDATE test_tbl SET status_on = 0 WHERE stream_id = %s AND location_id = %s"
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
            sql = "UPDATE test_tbl SET status_on = 1 WHERE stream_id = %s AND location_id = %s"
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

             return title + " | " + str(self.status) + " | " + str(self.stream_id) + " | " + str(self.location_id) + " | " + str(self.data1) \
                 + " | " + str(self.data2) + " | " + str(self.data3) + " | " + str(self.data4) + " | " + str(self.data5) + " ||\n " + str(self.logstring)

         except Exception as e:
             return "data return error" + e


def connectSQL():
    try:
        connectionDB = mysql.connector.connect(user='#', password='#', database='video_analysis_db',
                              host='#',
                       )
        print("Connection String Opened successfully")
        mainRunTime(connectionDB)
        connectionDB.close()
    except Exception as e:
        print("**ERROR HAS OCCURED**: This was your error: ", e)
        print("Make sure the username and password and hostname are correct. If the database is offline contact your server admin (Juan)")

def mainRunTime(connectionDB):
    stream_id = "abI293098PO98" #local team responsible for this variable***
    location_id = 1 ##local team responsible for this variable***
    stream1 = Stream(connectionDB, stream_id, location_id)
    #stream1.online()
    #stream1.initializeDB()
    #stream1.updateData(.8956, .3456, .4567, .7896, .5445)
    #stream1.injectData()
    #stream1.updateLogString("logstring")
    #stream1.injectLogString()
    #stream1.offline()
    #V MAIN CODE SEGMENT HERE V#    




    #^ MAIN CODE SEGMENT HERE ^#
    stream1.closeDBstream()#close the DB for whatever class you open a stream with (optional)



if __name__ == '__main__':
    connectSQL()
