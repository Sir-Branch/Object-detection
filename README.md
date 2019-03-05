# Real Time Object-Person Detection

## Usage/Command-Prompt-Call:

python objection_detection_app.py [-h] [-img IMAGE | -vid VIDEO | -ip IPCAM] [-sv] [-sh]

**Optional arguments:**

    Path to image file: -img IMAGE, --image IMAGE 
    Path to video file: -vid VIDEO, --video VIDEO 
    Ipcam Ip number: -ip IPCAM, --ipcam IPCAM 
    Saves videos to memory: -sv, --save          
    Shows videos in windows while processing: -sh, --show           
  
If -sh option is passed will show in a window whatever is being processed(for videos). If -sv option is passed will save the result in memory. If no -sh or -sv is passed by default will show in a windows whatever is being processed. 

**Usage examples:** 

    Webcam in a window only:		python object_detection_app.py
	Webcam in a window only:		python object_detection_app.py -sh
	Webcam in a window and saved:	python object_detection_app.py -sh -sv
	Webcam saved only:				python object_detection_app.py -sv

    Video in a window only:			python object_detection_app.py --video run.mp4
    Video in a window only:			python object_detection_app.py --video run.mp4 -sh
    Video in a window and saved:	python object_detection_app.py --video run.mp4 -sh -sv
    Video saved only:				python object_detection_app.py --video run.mp4 -sv
	
	IPcam in a window only:			python object_detection_app.py --ipcam http://69.193.186.134:81/mjpg/video.mjpg
    IPcam in a window only:			python object_detection_app.py --ipcam http://69.193.186.134:81/mjpg/video.mjpg -sh
    IPcam in a window and saved:	python object_detection_app.py --ipcam http://69.193.186.134:81/mjpg/video.mjpg -sh -sv
    IPcam saved only:				python object_detection_app.py --ipcam http://69.193.186.134:81/mjpg/video.mjpg -sv

	Image:							python object_detection_app.py --image bird.jpg
	
    

### Available Real Time Models 
* ssd_mobilenet_v1_coco_11_06_2017
* ssd_mobilenet_v1_fpn_2018_07_03
* ssd_mobilenet_v2_coco_2018_03_29
* ssdlite_mobilenet_v2_coco_2018_05_09

For additional models: https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md

For 30fps an image processing time of about 30ms is requiered, this leaves us to choose amongst lower accuracy models for real time object detection. When higher accuary is needed on already stored videos, this can be done via much slower models which provide higher accuracy rates.
### Credits

Based on: 

https://github.com/schumanzhang/object_detection_real_time, which is based on https://github.com/datitran/object_detector_app: 

Optimization ONLY FOR PYTHON 2 as Python 3 can't run threads on different cores, could use multiprocessing: 

https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/
https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/


### Requirements 
As specified in requirements.txt:
* opencv-python==3.4.0
* matplotlib==2.0.0
* numpy==1.12.0
* tensorflow==1.8.0
* six==1.6.0
