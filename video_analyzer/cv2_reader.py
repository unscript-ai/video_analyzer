import os
import cv2
import queue
import numpy as np
from tqdm import tqdm
from threading import Thread, Event

class VideoReader:
    def __init__(
        self,
        source,
        batch_size=8,
        frame_size=None,
        resize = None,
    ):
        _, fext = os.path.splitext(source)
        if not os.path.exists(source):
            print("{} not found!!".format(source))
            exit(1)
        if fext not in ['.mp4', '.mkv', '.mov']:
            print("Currently we only support ['.mp4', '.mkv', '.mov'] extensions only!!")
            exit(1)

        self.stream = cv2.VideoCapture(source)
        self.fps = self.stream.get(cv2.CAP_PROP_FPS)
        self.frame_id = 0
        self.frame_count = self.stream.get(cv2.CAP_PROP_FRAME_COUNT)
        width  = int(self.stream.get(3))  # float `width`
        height = int(self.stream.get(4))  # float `height`
        self.org_frame_size = (width, height)
        self.batch_size = batch_size
        self.frame_size = frame_size
        self.batch_len = np.ceil(self.frame_count/self.batch_size)
        # self.resize = resize
        self.__queue = queue.Queue(maxsize=128)
        # thread initialization
        self.__thread = None
        self.__terminate = Event()
        # initialize stream read flag event
        self.__stream_read = Event()

    def start(self):

        self.__thread = Thread(target=self.__update, args=())
        self.__thread.daemon = True
        self.__thread.start()
        return self

    def __update(self):

        while True:
            # if the thread indicator variable is set, stop the thread
            (grabbed, frame) = self.stream.read()

            # check for valid frame if received
            if not grabbed:
                # no frames received, then safely exit
                if not self.__queue.empty():
                    continue
                else:
                    break
            if self.frame_size is not None:
                frame = cv2.resize(frame, self.frame_size)
            # frame = np.expand_dims(frame, axis=0)
            # print("read:",frame.shape)
            self.__queue.put(frame)
            self.frame_id += 1
        # indicate immediate termination
        self.__terminate.set()
        # print("terminated..")
        # release resources
        self.stream.release()

    def __iter__(self):
        return self

    def generate_batch(self):
        # TODO: generate batch and return batch
        x = None
        img_batch = []
        for frame in self:
            # print("batch",frame.shape)
            img_batch.append(frame)
            if len(img_batch)>=self.batch_size:
                yield img_batch
                img_batch = []
        if len(img_batch):
            yield img_batch

    def __next__(self):
        try:
            while not self.__terminate.is_set():
                if not self.__queue.empty():
                    return self.__queue.get()
            else:
                raise StopIteration
        except:
            self.stop()
            raise StopIteration

    def stop(self):
        # indicate that the thread
        # should be terminated immediately
        self.__terminate.set()

        # wait until stream resources are released (producer thread might be still grabbing frame)
        if self.__thread is not None:
            if not (self.__queue is None):
                while not self.__queue.empty():
                    try:
                        self.__queue.get_nowait()
                    except queue.Empty:
                        continue
                    self.__queue.task_done()
            self.__thread.join()

# if __name__=='__main__':
#     input_path = 'input_video.mp4'
#     fpath, fext = os.path.splitext(input_path)
#     output_path = fpath+'_out.mp4'
    
#     vc = VideoReader(input_path)
#     vw = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), vc.fps,\
#             vc.org_frame_size)
#     vc.start()
#     for batch in tqdm(vc.generate_batch(), desc="Video reading", total=vc.batch_len):
#         for frame in batch:
#             vw.write(frame)
#     vw.release()
#     print("Success!!")
    