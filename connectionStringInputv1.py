#Juan Merlos ED2
#must import mysql.connector and mysql.connector-python in python enviorment
#install pip if you don't have it already
#command: pip install virtualenv
#create virtual enviorment with virtualenv "name" - make sure your terminal directory is in project folder
#activate enviorment with "name"/Scripts/activate
#then install the connector using the commands: pip install mysql-connector and pip install mysql-connector-python
from logging import raiseExceptions
import mysql.connector


try:
    connectionDB = mysql.connector.connect(user='#', password='#', database='video_analysis_db',
                      host='#',
                     )
    print("Connection String Opened successfully")
    cursor = connectionDB.cursor()
    query = ("SELECT stream_id, location_id, data_1, data_2, data_3, data_4, data_5 FROM test_tbl WHERE status_on = %s")
    values = (0,)
    cursor.execute(query, values)
    for(stream_id, location_id, data_1, data_2, data_3, data_4, data_5) in cursor:
        print(stream_id)
        print(data_1)
        print(data_2)
        print(data_3)
        print(data_4)
        print(data_5)
    cursor.close()
    connectionDB.close()
            
except Exception as e:
      print("**ERROR HAS OCCURED**: This was your error: ", e)
      print("Make sure the username and password and hostname are correct. If the database is offline contact your server admin (Juan)")
          
if __name__ == '__main__':
  pass
