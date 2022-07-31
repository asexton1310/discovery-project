from flask import Flask
from flask import Flask, render_template, redirect, url_for, request
import mysql.connector



application = Flask(__name__)


#Sample sign in for debugging
class signIn(): #NOT PRODUCTION READY TESTING ONLY - LINK TO PROPER HASHED DATABASE
   def __init__(self):
      self.username = ""
      self.password = ""

user = signIn()

#Home page, simple sign in form
@application.route('/', methods=['GET', 'POST'])
def home():
   token = ""
   if request.method == 'POST':
        if request.form['username'] != user.username or request.form['password'] != user.password:
            token = 'INVALID'
        else:
            token = 'VERIFIED' #this is a development login DO NOT USE in production
            return redirect(url_for('hub', token=token, user1=user.username))
   return render_template('home.html', token=token)

#Route to mainview page and send data
@application.route('/mainview+<token>+<user1>+<streamid>+<locationid>', methods=['GET', 'POST'])
def mainview(token, user1, streamid, locationid):
    if token == 'VERIFIED': #this is a development login DO NOT USE in production
        try:
            connectionDB = mysql.connector.connect(user='', password='', database='',
                              host='',
                       )
            print("Connection String Opened successfully")
            cursor = connectionDB.cursor()
            query = ("SELECT * FROM final_tblv2 WHERE status_on = %s and stream_id = %s and location_id = %s")
            values = (1, streamid, locationid, )
            cursor.execute(query, values)
            stream_ids = []
            for (stream_id) in cursor:
                stream_ids.append(stream_id)
            cursor.close()
            connectionDB.close()
            stream_ids = list(stream_ids[0])
            stream_ids.pop()
            stream_ids.pop(0)
            namedata = stream_ids[:3] #id, location, entry,...
            streamdata = stream_ids[3:6] 
            streamvalues = stream_ids[6:]
            streamvaluesformated = []
            streamvaluenames = ["avg_blockiness",
            "max_blockiness",
            "min_blockiness",
            "avg_blur",
            "max_blur",
            "min_blur",
            "avg_contrast",	
            "max_contrast",	
            "min_contrast",
            "avg_color",	
            "max_color",	
            "min_color",	
            "avg_ltp",
            "max_ltp",
            "min_ltp",
            "avg_noise",	
            "max_noise",	
            "min_noise",	
            "avg_brisque",
            "max_brisque",	
            "min_brisque",	
            "avg_flicker",	
            "avg_flickering_agh",	
            "avg_blockiness_agh",	
            "avg_letterBox_agh",	
            "avg_pillarBox_agh",	
            "avg_blockloss_agh",	
            "avg_blur_agh",
            "avg_blackout_agh",
            "avg_freezing_agh",	
            "avg_exposure_agh",	
            "avg_contrast_agh",	
            "avg_interlace_agh",	
            "avg_noise_agh",	
            "avg_si_agh",	
            "avg_ti_agh",
            "quality_estimate"]
            i = 0
            for value in streamvalues:
                if value != None:
                    streamvaluesformated.append([streamvaluenames[i], round(float(value), 2)])
                else:
                    streamvaluesformated.append([streamvaluenames[i], None])
                i = i + 1
            print(namedata)
            print(streamdata)
            print(streamvaluesformated)
            return render_template('mainview.html', token=token, user1 = user1, namedata = namedata, streamdata = streamdata, streamvaluesformated = streamvaluesformated, streamvalues = streamvalues)
        except Exception as e:
            print("**ERROR HAS OCCURED**: This was your error: ", e)
            print("Make sure the username and password and hostname are correct. If the database is offline contact your server admin (Juan)")
            return render_template('mainview.html', user = "ERROR CONNECTING TO SQL")
    else:
        return "invalid token"

#Get data, parse through logstring, route to historyview page and send data
@application.route('/historyview+<token>+<user1>+<streamid>+<locationid>', methods=['GET', 'POST'])
def historyview(token, user1, streamid, locationid):
    if token == 'VERIFIED': #this is a development login DO NOT USE in production
        try:
            connectionDB = mysql.connector.connect(user='', password='', database='',
                              host='',
                       )
            print("Connection String Opened successfully")
            cursor = connectionDB.cursor()
            query = ("SELECT log_string FROM final_tblv2 WHERE stream_id = %s and location_id = %s")
            values = (streamid, locationid, )
            cursor.execute(query, values)
            logstring = ""
            for (logstring,) in cursor:
                logstring = logstring
            cursor.close()
            connectionDB.close()
            print(logstring)
            

            return render_template('historyview.html', user1 = user1, logstring = logstring, streamid=streamid, locationid=locationid)
        except Exception as e:
            print("**ERROR HAS OCCURED**: This was your error: ", e)
            print("Make sure the username and password and hostname are correct. If the database is offline contact your server admin (Juan)")
            return render_template('mainview.html', user = "ERROR CONNECTING TO SQL")
    else:
        return "invalid token"

#Route to hub page and send data
@application.route('/hub+<token>+<user1>', methods=['GET', 'POST'])
def hub(token, user1):
    if token == 'VERIFIED': #this is a development login DO NOT USE in production
        try:
            connectionDB = mysql.connector.connect(user='', password='', database='',
                              host='',
                       )
            print("Connection String Opened successfully")
            cursor = connectionDB.cursor()
            query = ("SELECT stream_id, location_id FROM final_tblv2 WHERE status_on = %s")
            values = (1,)
            cursor.execute(query, values)
            stream_ids = []
            locations = []
            for (stream_id, location, ) in cursor:
                stream_ids.append([stream_id, location])
            cursor.close()
            print(stream_ids)
            #-----------------------
            cursor = connectionDB.cursor()
            query = ("SELECT stream_id, location_id FROM final_tblv2")
            cursor.execute(query)
            stream_idshist = []
            stream_idonly = []
            for (stream_id, location, ) in cursor:
                stream_idonly.append(stream_id)
                stream_idshist.append([stream_id, location])
            cursor.close()
            connectionDB.close()
            print(stream_ids)
            stream_ids_unique = []
            stream_ids_unique = list(dict.fromkeys(stream_idonly))
            return render_template('hub.html', user1 = user1, stream_ids = stream_ids, locations = locations, stream_idshist = stream_idshist, stream_ids_unique = stream_ids_unique, token = token)
        except Exception as e:
            print("**ERROR HAS OCCURED**: This was your error: ", e)
            print("Make sure the username and password and hostname are correct. If the database is offline contact your server admin (Juan)")
            return render_template('hub.html', user = "ERROR CONNECTING TO DATABASE")
    else:
        return "invalid token"

#Get data, calculate overall quality and route to overall quality score page and send data
@application.route('/overallview+<token>+<user1>+<streamid>', methods=['GET', 'POST'])
def overallview(token, user1, streamid):
    if token == 'VERIFIED': #this is a development login DO NOT USE in production
        try:
            connectionDB = mysql.connector.connect(user='', password='', database='',
                              host='',
                       )
            print("Connection String Opened successfully")
            cursor = connectionDB.cursor()
            query = ("SELECT log_string FROM final_tblv2 WHERE stream_id = %s")
            values = (streamid,)
            cursor.execute(query, values)
            logstrings = []
            for (logstring,) in cursor:
                logstrings.append(logstring)
            cursor.close()
            connectionDB.close()
            holdarr = []
            estimations = []
            for string in logstrings:
                if string != None:
                    holdarr = string.split("|")
                    if '' in holdarr:
                        holdarr.remove('')
                    for values in holdarr:
                        holdarr = values.split(";")
                        if '' in holdarr:
                            holdarr.remove('')
                        if len(holdarr) != 0:
                            estimations.append(float(holdarr[-1]))
            print(estimations)
            qualityestimation = "This stream did not collect sufficient data so an overall score was not attained"
            if len(estimations) > 0:
                qualityestimation = sum(estimations)/len(estimations)
                qualityestimation = qualityestimation * 100 #make a percent
                qualityestimation = int(qualityestimation) #make in to easy to read int
            
            
            return render_template('overallview.html', user1 = user1, logstring = logstring, streamid=streamid, qualityestimation = qualityestimation)
        except Exception as e:
            print("**ERROR HAS OCCURED**: This was your error: ", e)
            print("Make sure the username and password and hostname are correct. If the database is offline contact your server admin (Juan)")
            return render_template('mainview.html', user = "ERROR CONNECTING TO SQL")
    else:
        return "invalid token"


if __name__ == '__main__':
   application.run()