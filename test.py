import os
import cv2
from tqdm import tqdm
from video_analyzer import VideoReader

if __name__=='__main__':
    input_path = 'tests/input_video.mp4'
    fpath, fext = os.path.splitext(input_path)
    output_path = fpath+'_out.mp4'
    
    try:
        vc = VideoReader(input_path)
        vw = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), vc.fps,\
                vc.org_frame_size)
        vc.start()
        for batch in tqdm(vc.generate_batch(), desc="Video reading", total=vc.batch_len):
            for frame in batch:
                vw.write(frame)
        vw.release()
        print("Success!!")
    except:
        print("Failed!!")
