from django.http import HttpResponse
from django.shortcuts import render
from django.core.mail import EmailMessage
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
import cv2
import threading
import os

@gzip.gzip_page
def index(request):
    try:
        cam = VideoCamera()
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        pass
    return render(request, template_name="index.html")

#to capture video class
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        # faces = self.detect_faces(img=image)
        # for item in faces:
        #     self.draw_rectangle(img=image, rect=item['rect'])
        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()

    def detect_faces(self, img):
        '''Detect face in an image'''

        faces_list = []

        # Convert the test image to gray scale (opencv face detector expects gray images)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Load OpenCV face detector (LBP is faster)
        face_cascade = cv2.CascadeClassifier('templates/lbpcascade_frontalface.xml')

        # Detect multiscale images (some images may be closer to camera than others)
        # result is a list of faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5);

        # If not face detected, return empty list
        if len(faces) == 0:
            return faces_list

        for i in range(0, len(faces)):
            (x, y, w, h) = faces[i]
            face_dict = {}
            face_dict['face'] = gray[y:y + w, x:x + h]
            face_dict['rect'] = faces[i]
            faces_list.append(face_dict)

        # Return the face image area and the face rectangle
        return faces_list

    # ----------------------------------------------------------------------------------
    # Draw rectangle on image
    # according to given (x, y) coordinates and given width and heigh
    # ----------------------------------------------------------------------------------
    def draw_rectangle(self, img, rect):
        '''Draw a rectangle on the image'''
        (x, y, w, h) = rect
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')