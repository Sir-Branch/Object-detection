from collections import defaultdict
import csv
import cv2
import os



# Tracks and draws what's present at any particular time on screen
class ObjectTracker(object):
    #Defines
    EMPTY_FRAME_FALSE = 5 #Number of empty frames to disable person status 
    #Variables
    pers_frame_count = 0
    people_only = True

    def __init__(self):
        self.class_counts = {}
        self.occupancy = False
        self.prev = None


    def update_class_counts(self, class_names):
        frame_counts = defaultdict(int)
        for item in class_names:
            count_item = item[0].split(':')[0]
            frame_counts[count_item] += 1

        self.class_counts = frame_counts

    def update_person_status(self, class_names):
        for item in class_names:
            if item[0].split(':')[0] == 'person':
                self.occupancy = True
                self.pers_frame_count = 0;
                return

        self.pers_frame_count += 1
        if(self.pers_frame_count >= self.EMPTY_FRAME_FALSE ):
            self.occupancy = False      


    def __call__(self, context):
        #self.update_class_counts(context['class_names']) #Counts each one 
        self.update_person_status(context['class_names'])
        frame = context['frame']
        font = cv2.FONT_HERSHEY_SIMPLEX

        for point, name, color in zip(context['rec_points'], context['class_names'], context['class_colors']):
            if not self.people_only or name[0][:6] == "person": #Only detect people, will always be true if people only false
                cv2.rectangle(frame, (int(point['xmin'] * context['width']), int(point['ymin'] * context['height'])),
                                (int(point['xmax'] * context['width']), int(point['ymax'] * context['height'])), color, 3)

                # cv2.rectangle(frame, (int(point['xmin'] * context['width']), int(point['ymin'] * context['height'])),
                #                 (int(point['xmin'] * context['width']) + len(name[0]) * 6,
                #                 int(point['ymin'] * context['height']) - 10), color, -1, cv2.LINE_AA)

                # cv2.putText(frame, name[0], (int(point['xmin'] * context['width']), int(point['ymin'] * context['height'])), font,
                #             0.3, (0, 0, 0), 1)



        cv2.putText(frame, ("Person detected: {occupied}".format(occupied=self.occupancy)), (30, 30),
                font, 0.6, (255, 255, 255), 1)



        return frame
    