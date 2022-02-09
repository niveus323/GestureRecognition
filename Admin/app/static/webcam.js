var myVideoStream = document.getElementById('camera')
getVideo()


function getVideo(){
  navigator.getMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;
  navigator.getMedia(
    {video: true, audio: false}, 
    function(stream) {
      myVideoStream.srcObject = stream   
      myVideoStream.play();
    },                  
    function(error) {
      alert('webcam not working');
    });
}