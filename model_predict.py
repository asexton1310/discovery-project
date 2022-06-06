import pandas as pd
import tensorflow as tf
import custom_tf_metrics as custom_metrics
import logging
import os.path
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import time

class NewMetricEventHandler(PatternMatchingEventHandler):
    # filesystem watchdog for integrating quality metric extractor with
    # trained model predictions.
    # based on examples from python watchdog library available at:
    # https://github.com/gorakhargosh/watchdog/

    def __init__(self, model_loc=None, **kwargs):
        super().__init__(**kwargs)
        
        # load model used to make predictions
        self.model = tf.keras.models.load_model(model_loc,
                                        custom_objects={"PearsonCorrelation":custom_metrics.PearsonCorrelation,
                                                        "SpearmanCorrelation":custom_metrics.SpearmanCorrelation})
        # Check its architecture
        print(self.model.summary())

    def on_any_event(self, event):
        #for testing purposes, log every event
        logging.info(event)
    
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
        df = pd.read_csv(target_file)
        print("df.head: ", df.head() )

        # make the predictions
        print("Predictions: ")
        print(self.model.predict(df.iloc[0:1]))
        
        # delete the csv file now that we have made predictions
        os.remove(target_file)

def getMetrics(path):
    # Function that repeatedly polls a directory looking for
    # new csvs (extracted metrics) and uses an observer to
    # make predictions and delete them when the next csv is 
    # available.  Modified from quickstart example in
    # Python watchdog library documentation
    # https://github.com/gorakhargosh/watchdog
    #
    # path - folder to watch for new csvs

    # set up logging for debugging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    
    #set up the event handler we want the watchdog observer to use
    event_handler = NewMetricEventHandler(patterns=['*.csv'],
                                         ignore_directories=True,
                                         model_loc="./savedModels/feedfw-nn-1/")
    # Create, configure, and start the observer                                     
    observer = Observer()
    observer.schedule(event_handler, path)
    observer.start()
    # while loop with exception so the user is able to interrupt execution
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    getMetrics("./quality-metrics/")