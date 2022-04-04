from datetime import datetime
from flask import Flask, Response, jsonify, render_template, request, flash, redirect, safe_join, send_from_directory, url_for
# from werkzeug import secure_filename
import os
import cv2

#Initialize Flask Application
app = Flask(__name__)

path = 'Output'
os.makedirs(path, exist_ok=True)

models = {
    'Gesture' : ["Tap", "Double_Tap", "Grab", "Drop", "Pinch", "Spread", "Slide_Left", "Slide_Right"],
    'Improvement' : ["Finger_Recognition"]
}
for key, types in models.items():
    for type in types :
        os.makedirs(os.path.join(path, key, type), exist_ok=True)

#Recorder Page
@app.route('/')
def index():
    templateData = {
        'title':'Video Recorder',
        'models' : models
        }
    return render_template('record.html', **templateData)

@app.route('/video', methods=['POST'])
def record_video():
    try:
        video = request.files['video']
        model = request.form.get('model')
        type = request.form.get('type')
        filename = '{}.mp4'.format(datetime.now().strftime('%Y-%m-%d %H_%M_%S'))
        dir = os.path.join('{0}/{1}/{2}/{3}'.format(path, model, type, filename))
        video.save(dir)
    except Exception:
        print(Exception)
        return {"result" : "fail"}
    else:
        return {"result" : "success"}

#Drive Page
@app.route('/drive')
def drive():
    filename = request.args.get('filename', "")
    dirs = request.args.get('dirs', path)
    ext = os.path.splitext(filename)[1]
    route = dirs
    if filename != "" :
        route = route +'/'+filename
    templateData = { 'title' : 'Video Drive', 'route' : route }
    if ext == '.mp4' :
        templateData['video'] = filename
    else :
        files = os.listdir(route)
        templateData['files'] = files
    return render_template('drive.html', **templateData)

@app.route('/video_delete', methods=['POST'])
def video_delete():
    dirs = request.form.get('dirs')
    redir = dirs[0 : dirs.rfind('/')]
    os.remove(dirs)
    return redirect(url_for('drive',dirs=redir))

@app.route('/video_feed')
def video_feed():
    dirs = request.args.get('dirs')
    return Response(gen(dirs),mimetype='multipart/x-mixed-replace; boundary=frame')

def gen(video):
    cap = cv2.VideoCapture(video)
    while(cap.isOpened()):
        retval, frame = cap.read()
        if not(retval): 
            break
        ret, jpeg = cv2.imencode('.jpg',frame)
        result = jpeg.tobytes()
        yield(b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + result + b'\r\n\r\n')
    cap.release()
    cv2.destroyAllWindows()

@app.route('/health_check')
def health_check():
    return "pong"

if __name__== "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)