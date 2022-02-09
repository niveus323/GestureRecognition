from genericpath import exists
from json.encoder import ESCAPE_ASCII
from cv2 import waitKey
from flask import Flask, Response, render_template, request, flash, redirect, url_for
import cv2
import mediapipe as mp
import os
import uuid

#Initialize Flask Application
app = Flask(__name__)

path = 'Output_Images'
os.makedirs(path, exist_ok=True)
gestures = ["Tap", "Double Tap", "Grab", "Drop", "Pinch", "Spread", "Slide Left", "Slide Right"]
for gesture in gestures:
    os.makedirs(os.path.join(path,gesture), exist_ok=True)

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5)

#Main Page
@app.route('/')
def index():
    templateData = {
        'title':'Image Streaming',
        'len' : len(gestures),
        'gestures' : gestures
        }
    return render_template('index.html', **templateData)

@app.route('/video_feed', methods=['POST'])
def video_feed():
    return Response(gen_frames(request.form.get('type')), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames(type):
    cap = cv2.VideoCapture(0)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fps = 30
    out = cv2.VideoWriter(os.path.join(path, str(gestures[int(type)]) ,'{}.avi'.format(uuid.uuid1())),fourcc, fps, (int(width), int(height)))

    while cap.isOpened():
        ret, frame = cap.read()
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = cv2.flip(image, 1)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for num, hand in enumerate(results.multi_hand_landmarks):
                mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS, 
                    mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                    mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2),
                    )
        cv2.imshow('image', image)
        out.write(image)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__== "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)