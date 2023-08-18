## Installation
```bash
$ pip install git+https://github.com/unscript-ai/video_analyzer.git
```

## Usage
```bash
from video_analyzer import VideoReader
vc = VideoReader(source='input_video.mp4', batch_size=8, frame_size=None)
vc.start() # To start the video loading

for i, frame in enumerate(vc):
    print("frame shape: {}".format(frame.shape))

vc.stop()
```