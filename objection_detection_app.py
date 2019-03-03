import cv2 as cv
import time
import argparse
import numpy as np
import tensorflow as tf
import os


from queue import Queue #Thread safe
from threading import Thread
from analytics.tracking import ObjectTracker
from detect_object import detect_objects

#https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md
#https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/
#https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/

#Could speed up with queues for output
# def thread_vid_output(input_q, output_q):
# 	while True:
# 		if not output_q.empty():
# 			data = output_q.get()
# 			context = {'frame': frame, 'class_names': data['class_names'], 'rec_points': data['rect_points'], 
# 						'class_colors': data['class_colors'], 'width': width, 'height': height}

# 			new_frame = object_tracker(context)
# 			vid_writer.write(new_frame.astype(np.uint8))
# 			cv.imshow(WINDOW_NAME, new_frame)


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
		if not input_q.empty():
			frame = input_q.get()
			frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
			output_q.put(detect_objects(frame, sess, detection_graph))

	sess.close()


def thread_process_image(input_q, process_q):

	return




def thread_output_image(process_q, output_q):


	return


CWD_PATH = os.getcwd()

MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09'
PATH_TO_MODEL = os.path.join(CWD_PATH, 'detection', MODEL_NAME, 'frozen_inference_graph.pb')
PATH_TO_VIDEO = os.path.join(CWD_PATH, 'input.mp4')
OUTPUT_FILE = "my_test.avi"
WINDOW_NAME = "People Detector"
#MAX_QUEUE_SIZE = 128


run_threads = True #will be used to kill threads

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser = argparse.ArgumentParser(description='Object Detection using OPENCV')
	parser.add_argument('-src', '--source', dest='video_source', help='Path of video source, no input webcam.')
	parser.add_argument('-img', '--image', help='Path to image file.')
	parser.add_argument('-vid', '--video', help='Path to video file.')
	args = parser.parse_args()

	input_q = Queue(5)
	process_q = Queue()
	output_q = Queue()

	Thread(target=thread_worker, args=(input_q, output_q)).start()

	vid_capture = cv.VideoCapture(0)
	width = round(vid_capture.get(cv.CAP_PROP_FRAME_WIDTH))
	height = round(vid_capture.get(cv.CAP_PROP_FRAME_HEIGHT))
	codec = cv.VideoWriter_fourcc(*'MJPG')#http://www.fourcc.org/codecs.php
	vid_writer = cv.VideoWriter(OUTPUT_FILE, codec , 30, (width,height))

	object_tracker = ObjectTracker()

	while cv.waitKey(1) & 0xFF != ord('q') : #If q key is pressed exit window

		has_frame, frame = vid_capture.read()

		# if not has_frame:
		# 	print("Done processing !!!")
		# 	print("Output file is stored as ", outputFile)
		# 	cv.waitKey(3000)
		# 	# Release device
		# 	cap.release()
		# 	break

		# put data into the input queue 
		input_q.put(frame)

		if not output_q.empty():
			data = output_q.get()
			print("frame going to be outputted")
			context = {'frame': frame, 'class_names': data['class_names'], 'rec_points': data['rect_points'], 
						'class_colors': data['class_colors'], 'width': width, 'height': height}
			new_frame = object_tracker(context)
			vid_writer.write(new_frame.astype(np.uint8))
			cv.imshow(WINDOW_NAME, new_frame)

		
	run_threads = False
	vid_capture.release()
	vid_writer.release()
	cv.destroyAllWindows()



