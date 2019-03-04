import cv2 as cv
import time
import argparse
import numpy as np
import tensorflow as tf
import os

#Python Libraries
from queue import Queue #Thread safe
from threading import Thread

#Local Files
from tracking import ObjectTracker
from detect_object import detect_objects


"""
Usage example: 
	python object_detection_app.py --video=run.mp4
	python object_detection_app.py --image=bird.jpg

Models:
	https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md

Optimizing Only for python 2:
	https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/
	https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/
"""


def thread_worker(input_q, output_q):
	# load the frozen tensorflow model into memory
	detection_graph = tf.Graph()
	with detection_graph.as_default():
		od_graph_def = tf.GraphDef()
		with tf.gfile.GFile(PATH_TO_MODEL, 'rb') as fid:
			serialized_graph = fid.read()
			od_graph_def.ParseFromString(serialized_graph)
			tf.import_graph_def(od_graph_def, name='')

		sess = tf.Session(graph=detection_graph)

	while run_threads:
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
"""

def thread_process_image(input_q, process_q):
	return
def thread_output_image(process_q, output_q):
	return

def parse_cmd_line():

	video_capture_source = 0 #Webcam number
	output_file = "NULL"

	parser = argparse.ArgumentParser()
	parser = argparse.ArgumentParser(description='Real Time Object Detection using OPENCV + TF')
	#parser.add_argument('-src', '--source', dest='video_source', help='Path of video source, no input webcam.')
	parser.add_argument('-img', '--image', help='Path to image file.')
	parser.add_argument('-vid', '--video', help='Path to video file.')
	args = parser.parse_args()


	if(args.video):
		# Open the video file
		if not os.path.isfile(args.video):
			print("Input video file ", args.video, " doesn't exist")
			sys.exit(1)
		output_file = args.video[:-4]+'_video_out_py.avi' #Removes extension and adds _video_out_py.ave
		video_capture_source = args.video
	elif(args.image):
		#Open image file
		if not os.path.isfile(args.image):
			print("Input image file ", args.image, " doesn't exist")
			sys.exit(1)
		video_capture_source = args.image
		output_file = args.image[:-4]+'_image_out_py.jpg'

	return video_capture_source, output_file


# DEFINES
CWD_PATH = os.getcwd()
MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09'
PATH_TO_MODEL = os.path.join(CWD_PATH, 'detection', MODEL_NAME, 'frozen_inference_graph.pb')
WINDOW_NAME = "People Detector"
#MAX_QUEUE_SIZE = 128

#Global Variables
run_threads = True #will be used to kill threads

if __name__ == '__main__':

	video_capture_source, output_file = parse_cmd_line()

	pending_frames = 0 #Will carry out a count of pending 
	is_video = (output_file[-4:] =='.avi')
	is_image = (output_file[-4:] =='.jpg')

	#Designed for multithreading but python 3 doesn't support various cores running D:
	input_q = Queue(1)
	output_q = Queue()
	object_tracker = ObjectTracker()

	Thread(target=thread_worker, args=(input_q, output_q)).start()

	#Viceo_capture_source integer corresponds to webcam, while string corresponds to file path
	vid_capture = cv.VideoCapture(video_capture_source)
	width = round(vid_capture.get(cv.CAP_PROP_FRAME_WIDTH))
	height = round(vid_capture.get(cv.CAP_PROP_FRAME_HEIGHT))
	codec = cv.VideoWriter_fourcc(*'MJPG')#http://www.fourcc.org/codecs.php

	if is_video:
		vid_writer = cv.VideoWriter(output_file, codec , 30, (width,height))

	while cv.waitKey(1) & 0xFF != ord('q') : #If q key is pressed exit window

		has_frame, frame = vid_capture.read()

		if has_frame:# If not end frame put into the input queue 
			input_q.put(frame)
			pending_frames += 1
		elif pending_frames == 0: #No more pending frames
			break

		if not output_q.empty():
			data = output_q.get()
			new_frame = output_q.get()

			context = {'frame': new_frame, 'class_names': data['class_names'], 'rec_points': data['rect_points'], 
			'class_colors': data['class_colors'], 'width': width, 'height': height}
			new_frame = object_tracker(context)
			pending_frames -= 1

			if is_video: #0 = Webcam
				vid_writer.write(new_frame.astype(np.uint8))
			elif is_image:
				print("writing image")
				cv.imwrite(output_file, new_frame.astype(np.uint8));
			else:
				cv.imshow(WINDOW_NAME, new_frame)

		
	run_threads = False
	vid_capture.release()
	
	if is_video or is_image:
		print("Done processing!")
		print("Output file stored as: ", output_file)
		if is_video: #0 = Webcam
			vid_writer.release()

	cv.destroyAllWindows()



