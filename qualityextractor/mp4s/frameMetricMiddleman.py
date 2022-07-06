import time
import os.path
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import logging


class NewFrameEventHandler(PatternMatchingEventHandler):
    def __init__(self, n=None, **kwargs):
        super().__init__(**kwargs)

        # number of frames to bundle as a video
        self.n = n
        self.segment = 0

    def on_any_event(self, event):
        #for testing purposes, log every event
        #logging.info(event)
        pass

    def on_created(self, event):
        # when a new png file is created, process the previous one
        # this avoids any potential issues with processing a newly
        # created png file before it is finished being written to

        # split png number and extension from the rest of the path
        prefix, num_ext = event.src_path.rsplit("-", 1)

        # split png number and extension
        sample_num, ext = os.path.splitext(num_ext)

        #check if this is our nth frame
        if int(sample_num) == (self.segment + 1) * self.n + 1:
            # do the processing,
            print(f"Moving video {self.segment}")
            new_dir = f"./live-frames/video-{self.segment}-frames"

            if not os.path.isdir(new_dir):
                os.mkdir(new_dir)

            target_num = int(sample_num) - self.n

            for i in range(target_num, target_num + self.n):
                target_file = f"{prefix}-{i}{ext}"
                new_location = f"{new_dir}/frame-{i}{ext}"
                #move file to new directory.
                os.rename(target_file, new_location)
            self.segment += 1
        else:
            #print(f"frame not multiple of {self.n}")
            return


def getLiveFrames(path, batch_size):
    # Function that repeatedly polls a directory looking for
    # new pngs (samples from livestream) and uses an observer to
    # process them when they are created, and delete them when the
    # next sampled frame is available.  Modified from quickstart example in
    # Python watchdog library documentation
    # path - folder to watch for new pngs

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    event_handler = NewFrameEventHandler(patterns=['*.png'],
                                         n=batch_size,
                                         ignore_directories=True)

    # Create, configure, and start the observer
    observer = Observer()
    observer.schedule(event_handler, path)
    observer.start()
    # while loop so the user is able to interrupt execution
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    getLiveFrames("./raw-frames/", batch_size=75)
