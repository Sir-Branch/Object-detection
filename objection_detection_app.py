import cv2 as cv
import argparse
import numpy as np
import tensorflow as tf
import os
#Python Libraries
from queue import Queue #Thread safe
from threading import Thread
from copy import deepcopy
#Local Files
from notifier import notifier 
from tracking import ObjectTracker
from detect_object import detect_objects


"""
Usage example: 
	Webcam:	python object_detection_app.py
	Video:	python object_detection_app.py --video run.mp4
	Image:	python object_detection_app.py --image bird.jpg

Models:
	https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md

Optimizing Only for python 2:
	https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/
	https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/
"""


"""
This thread carries out object detection and loads up the frozen tensorflow model for
classification.
Takes the frames from input_queue calculates classification data and pushes
data and original frame to output_queue

Input:
	-input_q: Input queue, contains frames
	-output_q: Output queue, original frame + data will be pushed to this queue
Return: None
"""
def thread_detect_objects(input_q, output_q):
	# load the frozen tensorflow model into memory
	detection_graph = tf.Graph()
	with detection_graph.as_default():
		od_graph_def = tf.GraphDef()
		with tf.gfile.GFile(PATH_TO_MODEL, 'rb') as fid:
			serialized_graph = fid.read()
			od_graph_def.ParseFromString(serialized_graph)
			tf.import_graph_def(od_graph_def, name='')

		sess = tf.Session(graph=detection_graph)

	while not kill_threads:
		if not input_q.empty(): #better to block than poll empty, as not running on various cores
			frame = input_q.get()
			data = detect_objects(frame, sess, detection_graph)
			output_q.put(data)
			output_q.put(frame)

	sess.close()

"""
Tried to optimize with threads but ended up working slower, is it able to run with various cores?
 https://stackoverflow.com/questions/7542957/is-python-capable-of-running-on-multiple-cores
 Base on various answer it's unable to run on various cores 

If future python version work correctly on multiple cores this will result useful, use one thread to process
and one to output video file.
"""
def thread_process_image(input_q, process_q):
	return
def thread_output_image(process_q, output_q):
	return

"""
Carries out the parsing of the command line, this will detect if the user wants to process webcam,
images or videos. Returns video capture source to be used with cv.VideoCapture() and the name of the output file

Input: None
Return:
	-video_capture_source: 0 for webcam, and for image or video files just the file name
	-output_file: Returns output file name, "...out_py.avi" for video, "...out_py.jpg" and "NULL" for webcam a
	there shouldn't be an output file
	-save_vid: Returns true if save video option selected, will store video
	-show_vid: Returns true if show video option selected, will show video in window while processing

"""
def parse_cmd_line():

	video_capture_source = 0 #Webcam number
	output_file = "NULL"

	parser = argparse.ArgumentParser(description ='Real Time Object Detection using OPENCV + TF')

	group_source = parser.add_mutually_exclusive_group()
	group_source.add_argument('-img', '--image', help='Path to image file.')
	group_source.add_argument('-vid', '--video', help='Path to video file.')
	group_source.add_argument('-ip', '--ipcam', help='Ipcam Ip number.')
	parser.add_argument('-sv', '--save', help='Saves videos to memory.', action="store_true")
	parser.add_argument('-sh', '--show', help='Shows videos in windows while processing.', action="store_true")
	#parser.add_argument('-o', '--output', help='Output name.')

	args = parser.parse_args()

	save_vid = args.save
	show_vid = args.show

	if not save_vid and not show_vid: #Default show video
		show_vid = True
		print("No option choosen, will default show video. WILL NOT BE SAVED TO MEM -h for more options")

	if(args.video):
		# Open the video file
		if not os.path.isfile(args.video):
			print("Input video file ", args.video, " doesn't exist")
			sys.exit(1)
		output_file = args.video[:-4]+'_video_out_py.avi' #Removes extension and adds _video_out_py.ave
		video_capture_source = args.video
	elif(args.ipcam):
		output_file = args.ipcam +'_ipcam_out_py.avi' 
		video_capture_source = args.ipcam
	elif(args.image):
		#Open image file
		if not os.path.isfile(args.image):
			print("Input image file ", args.image, " doesn't exist")
			sys.exit(1)
		video_capture_source = args.image
		output_file = args.image[:-4]+'_image_out_py.jpg'

	return video_capture_source, output_file, save_vid, show_vid


# DEFINES
CWD_PATH = os.getcwd()
MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09'
PATH_TO_MODEL = os.path.join(CWD_PATH, 'detection', MODEL_NAME, 'frozen_inference_graph.pb')
WINDOW_NAME = "People Detector"

#Global Variables
kill_threads = False #will be used to kill threads

if __name__ == '__main__':

	video_capture_source, output_file, save_vid, show_vid = parse_cmd_line()

	pending_frames = 0 #Will carry out a count of pending 
	is_image = (output_file[-4:] =='.jpg') #Incase user input -video and -image video will have priority

	#Designed for multithreading but python 3 doesn't support various cores running D:
	input_q = Queue(1)
	output_q = Queue()

	object_tracker = ObjectTracker()
	website_html = notifier(15)
	Thread(target=thread_detect_objects, args=(input_q, output_q)).start()

	#Viceo_capture_source integer corresponds internal cam, while string corresponds to file path or ipcam
	vid_capture = cv.VideoCapture(video_capture_source)
	width = round(vid_capture.get(cv.CAP_PROP_FRAME_WIDTH))
	height = round(vid_capture.get(cv.CAP_PROP_FRAME_HEIGHT))
	codec = cv.VideoWriter_fourcc(*'MJPG')#http://www.fourcc.org/codecs.php

	#Vid writer is necessary for saving a video file
	if save_vid:
		vid_writer = cv.VideoWriter(output_file, codec , 30, (width,height))

	while cv.waitKey(1) & 0xFF != ord('q') : #If q key is pressed exit window

		has_frame, frame = vid_capture.read() #has_frame returns false when reaching end of file

		if has_frame:# If not end frame put into the input queue 
			input_q.put(frame)
			pending_frames += 1
		elif pending_frames == 0: #No more pending frames
			break

		if not output_q.qsize() >= 2: #Check if empty to avoid blocking
			data = output_q.get()
			new_frame = output_q.get()

			context = {'frame': new_frame, 'class_names': data['class_names'], 'rec_points': data['rect_points'], 
			'class_colors': data['class_colors'], 'width': width, 'height': height}
			website_html(deepcopy(context)) #Avoid the frame from being modified
			new_frame = object_tracker(context) 
			pending_frames -= 1

			if save_vid: 
				vid_writer.write(new_frame.astype(np.uint8))
			if show_vid:
				cv.imshow(WINDOW_NAME, new_frame)
			if is_image:
				cv.imwrite(output_file, new_frame.astype(np.uint8));

		
	kill_threads = True
	vid_capture.release()
	
	if save_vid or is_image:
		print("Done processing!")
		print("Output file stored as: ", output_file)
		if save_vid: #0 = Webcam
			vid_writer.release()

	cv.destroyAllWindows()



