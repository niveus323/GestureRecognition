const video = $('.input_video').get(0);
const startButton = $('#btn_start');
const stopButton = $('#btn_stop');
let currentTypeSelect = $('#type-Default');
let data = [];

startButton.click(function() {
  navigator.mediaDevices.getUserMedia({
    video : true,
    audio : false
  }).then(stream => {
    video.srcObject = stream;
    video.captureStream = video.captureStream || video.mozCaptureStream;
    video.play();
    return new Promise(resolve => video.onplaying = resolve);
  }).then(() => startRecording(video.captureStream()))
  .then(recordedChunks => {
    let recordedBlob = new Blob(recordedChunks, { type: "video/mp4" });
    console.log(recordedBlob);
    let formData = new FormData();
    formData.append('video', recordedBlob, 'video');
    // formData.append('model', $('select[name=model]').val());
    formData.append('duration', (endTime - startTime)/1000 )
    return new Promise((resolve, reject) => {
      try {
        axios.post('/video',formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }).then((response) => {
          console.log(response.data['result'])
          window.location.href = response.data['result']
          resolve();
        }).catch((error) => {
          console.log('전송 실패')
          console.log(error);
        })
      } catch (error) {
        reject(error);
      }
    })
  });
});
let startTime, endTime;
function startRecording(stream) {
  let recorder = new MediaRecorder(stream); //Recorder 생성
  recorder.ondataavailable = event => data.push(event.data); //Blob는 Array data에 저장된다.
  startTime = new Date();
  recorder.start(); //녹화 시작
  console.log("녹화 시작!");
  
  stopButton.click(function() {
    stopRecording(stream, recorder);
  });

  return new Promise((resolve, reject) => {
    recorder.onstop = resolve;
    recorder.onerror = event => reject(event.name);
  }).then(() => data);
}

function stopRecording(stream, recorder) {
  if(recorder.state == "recording"){
    recorder.stop();
    endTime = new Date();
    console.log("녹화 종료!");
    stream.getTracks().forEach(track => track.stop());
  } else {
    console.log("이미 종료되어 있습니다!");
  }
}

function selectModel(value){
  currentTypeSelect.css('display','none');
  let selectId = '#type-'+value;
  currentTypeSelect = $(selectId);
  currentTypeSelect.css('display','');
}