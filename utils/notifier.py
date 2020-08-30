from collections import defaultdict
import csv
import cv2
import os

class notifier(object):
	def __init__(self, samplerate):
		self.pictures = []
		self.framecounter = 0
		self.samplerate = samplerate

	def __call__(self, context):
		self.framecounter += 1;
		if not(self.framecounter % self.samplerate):
			frame = context['frame']
			for point, name, color in zip(context['rec_points'], context['class_names'], context['class_colors']):
				if(name[0][:6] == "person"): #Only detect people
					crop = frame[int(point['ymin'] * context['height']):int(point['ymax'] * context['height']), int(point['xmin'] * context['width']):int(point['xmax'] * context['width'])]
					if len(self.pictures) < 20:
						self.pictures.append(crop)
					else:
						self.pictures.insert(0, crop)
						self.pictures.pop()
				for index,im in enumerate(self.pictures):
					cv2.imwrite('savedpictures/dummy' + str(index) + '.bmp',im)
				#Saved for .bmp to avoid compression time with slowdowns server aprox 5ms per image
				#Although larger write files, so not exactly 5ms. Anyways fasters
		return
	