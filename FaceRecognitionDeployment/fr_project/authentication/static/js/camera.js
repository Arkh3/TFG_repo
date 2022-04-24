var localstream, canvas, video, cxt;

function turnOnCamera() {
    canvas = document.getElementById("canvas");
    cxt = canvas.getContext("2d");
    video = document.getElementById("video");

    if(!navigator.getUserMedia)
        navigator.getUserMedia = navigator.webkitGetUserMedia || navigator.mozGetUserMedia || 
    navigator.msGetUserMedia;
    if(!window.URL)
        window.URL = window.webkitURL;

    if (navigator.getUserMedia) {
        navigator.getUserMedia({"video" : true, "audio": false
        }, function(stream) {
            try {
                localstream = stream;
                video.srcObject = stream;
                video.play();
            } catch (error) {
                video.srcObject = null;
            }
        }, function(err){
            alert("Error");
        });
    } else {
        alert("User Media No Disponible");
        return;
    }
}

function turnOffCamera() {
    video.pause();
    video.srcObject = null;
    localstream.getTracks()[0].stop();
}

$("#radiotfoto").click(function(){
    $("#video").removeClass("none");
    $("#withOutCameraPic").removeClass("none");
    $("#withCameraPic").addClass("none");
    turnOnCamera();
}); 

$("#btn_start").click(function(){  
    setTimeout(function() { //QUITO EL TEMPORIZADOR ???????????????????????
        $("#btn_start").addClass("none");
        $("#btn_save").removeClass("none"); 
        $("#btn_repeat").removeClass("none");
    },1000); 
}); 

$("#btn_save").click(function(){ // NO FUNCIONA BIEN, llega pero no aplica
    turnOffCamera(); 
    $("#video").addClass("none");
    $("#withOutCameraPic").addClass("none");
    $("#withCameraPic").removeClass("none");
}); 