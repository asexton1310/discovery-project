import pandas as pd
from numpy import typename
import tensorflow as tf
import custom_tf_metrics as custom_metrics
import logging
import os.path
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import time
import mysql.connector
import sqlconnecterFINAL

class NewMetricEventHandler(PatternMatchingEventHandler):
    """ filesystem watchdog for integrating quality metric extractor with
        trained model predictions.
        based on examples from python watchdog library available at:
        https://github.com/gorakhargosh/watchdog/
    """

    def __init__(self, model_loc=None, unused_metrics=None, mysql_connection=None, **kwargs):
        super().__init__(**kwargs)
        
        # load model used to make predictions
        self.model = tf.keras.models.load_model(model_loc,
                                        custom_objects={"PLCC":custom_metrics.PLCC,
                                                        "SpearmanCorrelation":custom_metrics.SpearmanCorrelation})
        # Check its architecture
        print(self.model.summary())

        # store the metrics we won't use for future reference
        self.unused_metrics = unused_metrics

        """ set the database connection for future updates 
            TODO figure out how to set synchronize the stream_id based on some inherent fact of the stream
                 so that multiple local estimation systems can synchronize to have the same stream_id when they
                 are recording the quality of a single stream at different locations
            TODO location_id should be something unique to the specific location the stream is getting sampled at. 
                 Something like IP (if privacy is not a concern) or some unique hardware identifier could
                 be used to signify the specific locatino quality info corresponds to.
        """
        stream_id = time.time() # for demos in this project, this will just be a timestamp of when the stream started. 
                                # this only works with 1 local estimation system as multiple will not be synchronized
        location_id = 1 # for demos in this project, this is fixed at 1

        self.db_stream = sqlconnecterFINAL.Stream(mysql_connection, stream_id, location_id)
        self.db_stream.initializeDB()

    def on_any_event(self, event):
        #for testing purposes, log every event
        #logging.info(event)
        pass
    
    def on_created(self, event):
        # when a new csv file is created, process the previous one
        # this avoids any potential issues with processing a newly
        # created csv file before it is finished being written to
        
        # split csv number and extension from the rest of the path
        prefix, num_ext = event.src_path.rsplit("-", 1)
        # split csv number and extension
        sample_num, ext = os.path.splitext(num_ext)
        # get the previous csv file's number
        target_num = int(sample_num) - 1

        if target_num < 0:
            print(f"No target, fnum too low")
            return

        # reconstruct path to previous csv file (target file)
        target_file = f"{prefix}-{target_num}{ext}"
        print(f"Target File: {target_file}")
       
        # read the target csv file
        orig_df = pd.read_csv(target_file)
        print("orig_df.head: \n", orig_df.head())

        #drop any metrics that are not used by this model
        df = orig_df.drop(columns=self.unused_metrics, axis=1)

        # make the predictions
        quality_estimate = self.model.predict(df.iloc[0:1]) # quality_estimate in form [[numpyFloat]]
        print("Predictions: ")
        print(quality_estimate)

        # update the database
        metric_labels = list(orig_df.columns)
        for metric in metric_labels:
            self.db_stream.datapoints[metric] = orig_df.loc[0,metric]

        self.db_stream.datapoints["quality_estimate"] = float(quality_estimate[0][0])    # minor reformat of quality_estimate to float for DB compatibility
        #print(self.db_stream.datapoints)
        self.db_stream.injectData()

        # update the database's logstring
        datapointsstr = ""
        for metric in self.db_stream.datapoints:
            datapointsstr += str(self.db_stream.datapoints[metric]) + ";"
        self.db_stream.updateLogString(datapointsstr + "|")
        self.db_stream.injectLogString()

        # delete the csv file now that we have made predictions
        os.remove(target_file)

    def end_stream(self):
        """ updates the stream's status in the database to indicate the stream is over
            then closes the connection to the database
        """
        self.db_stream.offline()
        self.db_stream.closeDBstream()

def getMetrics(path, model_path, unused_metrics):
    # Function that repeatedly polls a directory looking for
    # new csvs (extracted metrics) and uses an observer to
    # make predictions and delete them when the next csv is 
    # available.  Modified from quickstart example in
    # Python watchdog library documentation
    # https://github.com/gorakhargosh/watchdog
    #
    # path - folder to watch for new csvs
    # model_path - path to the model we want to use to make predictions
    # unused_metrics - a list of string labels corresponding to the metrics
    #                  that the desired model does not use

    # set up logging for debugging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    
    # set up database connection
    try:
        connectionDB = mysql.connector.connect(user='#', password='#', database='video_analysis_db',
                              host='#',
                       )
        print("Connection String Opened successfully")
    except Exception as e:
        print("**ERROR HAS OCCURED**: This was your error: ", e)
        print("Make sure the username and password and hostname are correct. If the database is offline contact your server admin (Juan)")

    #set up the event handler we want the watchdog observer to use
    event_handler = NewMetricEventHandler(patterns=['*.csv'],
                                         ignore_directories=True,
                                         model_loc=model_path,
                                         unused_metrics=unused_metrics,
                                         mysql_connection=connectionDB)
    # Create, configure, and start the observer                                     
    observer = Observer()
    observer.schedule(event_handler, path)
    observer.start()
    # while loop with exception so the user is able to interrupt execution
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        event_handler.end_stream()
        observer.stop()
        connectionDB.close()
    observer.join()

if __name__ == "__main__":
    #getMetrics("./quality-metrics/", model_path="./savedModels/feedfw-nn-2022-06-09_18-30-34/")
    getMetrics("./quality-metrics/", model_path="./savedModels/live-ls-nrqe-2022-07-02_21-40-51/", unused_metrics=["bitrate", "framerate", "resolution"])