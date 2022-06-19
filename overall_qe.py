import mysql.connector

def overallStreamQE(target_stream=None):
    try:
        connectionDB = mysql.connector.connect(user='#', password='#', database='#',
                              host='#',
                       )
        print(target_stream)
        print("Connection String Opened successfully")
        cursor = connectionDB.cursor()
        query = ("SELECT stream_id, location_id, data_5 FROM test_tbl WHERE status_on = %s AND stream_id = %s")
        values = (0,target_stream,)
        cursor.execute(query, values)
        print("cursor: ",cursor)
        estimates = []
        even_weights = []
        weights = []
        for(stream_id, location_id, data_5) in cursor:
            estimates.append(data_5)
            even_weights.append(1)
            weights.append(int(location_id))
        if len(estimates) != 0:
            print("simpleavg: ",weightedAvg(estimates, even_weights))
            print("weightedavg: ",weightedAvg(estimates, weights))
            print()
        cursor.close()
        connectionDB.close()
                
    except Exception as e:
        print("**ERROR HAS OCCURED**: This was your error: ", e)
        print("Make sure the username and password and hostname are correct. If the database is offline contact your server admin (Juan)")
            
def weightedAvg(quality_estimates, weights):
    return sum([quality_estimates[i]*weights[i] for i in range(len(quality_estimates))]) / sum(weights)

if __name__ == "__main__":
    overallStreamQE("abI293098PO98")
 