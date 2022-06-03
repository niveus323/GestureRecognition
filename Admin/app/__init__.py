from datetime import datetime
from io import BytesIO
from flask import Flask, Response, render_template, request, redirect, url_for, send_file
# from werkzeug import secure_filename
import os, sys
import cv2
from moviepy.editor import VideoFileClip
import shutil
import zipfile
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


#Initialize Flask Application
app = Flask(__name__)

staticPath = './app/static'
tempPath = '{0}/Output'.format(staticPath)
outputPath = 'Output'
os.makedirs(outputPath, exist_ok=True)

types = { "Tap", "Slide", "Hold_On", "Hold_Off", "Volume_Up", "Volume_Down", "Double_Cursor_On", "Double_Cursor_Hold_On","Double_Cursor_Hold_Off","Double_Cursor_Off" }
for key in types:
    os.makedirs(os.path.join(outputPath, key), exist_ok=True)

#Recorder Page
@app.route('/')
def index():
    templateData = {
        'title':'Video Recorder'
        }
    return render_template('record.html', **templateData)

@app.route('/video', methods=['POST'])
def record_video():
    try:
        video = request.files['video']
        filename = '{}.mp4'.format(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
        dir = '{0}/{1}'.format(tempPath, filename)
        video.save(dir)
    except Exception:
        print(Exception)
        return {"result" : "fail"}
    else:
        return {"filename" : filename} 

@app.route('/video', methods=['GET'])
def show_video():
    filename = request.args.get('filename', type=str)
    if 'Output/' in filename:
        dir = filename
    else:
        dir = 'Output/'+filename
    video = '{0}/{1}'.format(staticPath, dir)
    duration = request.args.get('duration', type=float)
    result = request.args.get('result')
    cap = cv2.VideoCapture(video)
    fps = int(request.args.get('fps', 0))
    if fps <= 0:
        num_frames = 0
        if not cap.isOpened():
            print('open error! dir is '+video)
        while(cap.isOpened()):
            ret, frame = cap.read()
            if not(ret): 
                cap.release()
                break
            num_frames += 1
        fps = float(num_frames) / duration
    templateData = {
        'title' : 'Video Result',
        'video' : dir,
        'length': duration,
        'fps' : fps,
        'result' : result,
        'types' : types
    }

    return render_template('video.html', **templateData)

#Drive Page
@app.route('/drive')
def drive():
    filename = request.args.get('filename', "")
    dirs = request.args.get('dirs', outputPath)
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

@app.route('/video_trim', methods=['POST'])
def video_edit():
    path = request.form.get('path')
    realPath = './app/static/{0}'.format(path)
    start = request.form.get('start')
    end = request.form.get('end')
    duration = request.form.get('duration')
    result = request.form.get('result')
    fps = request.form.get('fps')
    fps = int(fps.split('.')[0])
    cap = cv2.VideoCapture(realPath)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if frames <= 0:
        print('No frames data in video, trying to convert this video..')
        writer = cv2.VideoWriter('fixedVideo.avi', 
            cv2.VideoWriter_fourcc(*'DIVX'), 
            fps, 
            (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        )
        while True:
            ret, frame = cap.read()
            if ret is True:
                writer.write(frame)
            else:
                cap.release()
                print("Stopping video writer")
                
                writer.release()
                writer = None
                break
        videoclip = VideoFileClip('fixedVideo.avi')
    else:
        videoclip = VideoFileClip(realPath)    
    videoclip = videoclip.subclip(start, end)
    nfilename = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    ndir = '{0}/{1}.mp4'.format(tempPath, nfilename)
    videoclip.write_videofile(ndir, fps=fps, threads=1, codec="libx264")
    videoclip.close()
    os.remove('fixedVideo.avi')
    result = 'Output/{0}.mp4'.format(nfilename)
    return redirect(url_for('show_video', filename=path, duration=duration, fps=fps, result=result ))

@app.route('/health_check')
def health_check():
    return "pong"

@app.route('/video/save', methods=['POST'])
def save_video():
    type = request.form.get('type')
    original = request.form.get('original')
    filename = request.form.get('filename')
    duration = request.form.get('duration')
    fps = request.form.get('fps')
    shutil.move('./app/static/{0}'.format(filename), 'Output/{0}'.format(type))

    return redirect(url_for('show_video', filename=original, duration=duration, fps=fps))

@app.route('/video/exit')
def exit_trimer():
    path = request.args.get('path')
    os.remove('{0}/{1}'.format(staticPath, path))
    return redirect('/')

@app.route('/drive/download')
def download_Output():
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for (path, dir, files) in os.walk(outputPath):
            for file in files:
                if file.endswith('.mp4'):
                    zf.write(os.path.join(path, file), compress_type=zipfile.ZIP_DEFLATED)
        zf.close()

    memory_file.seek(0)    
    return send_file(memory_file, attachment_filename='Output.zip', as_attachment=True)

if __name__== "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)