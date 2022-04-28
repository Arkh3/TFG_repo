var localstream, canvas, video, cxt;

function turnOnCamera() {
    canvas = document.getElementById("canvas");
    cxt = canvas.getContext("2d");
    video = document.getElementById("video");

    if(!navigator.getUserMedia)
        navigator.getUserMedia = navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;
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

function turnOffCamera() {  // No lo estoy usando por ahora
    video.pause();
    video.srcObject = null;
    localstream.getTracks()[0].stop();
    //video.load();
}


function dataURItoBlob( dataURI ) {

	var byteString = atob( dataURI.split( ',' )[ 1 ] );
	var mimeString = dataURI.split( ',' )[ 0 ].split( ':' )[ 1 ].split( ';' )[ 0 ];
	
	var buffer	= new ArrayBuffer( byteString.length );
	var data	= new DataView( buffer );
	
	for( var i = 0; i < byteString.length; i++ ) {
	
		data.setUint8( i, byteString.charCodeAt( i ) );
	}
	
	return new Blob( [ buffer ], { type: mimeString } );
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function takepicture() {
    canvas = document.getElementById("canvas");
    cxt = canvas.getContext("2d"); 
    video = document.getElementById("video");
    photo = document.getElementById('photo');

    width = 250;
    height = 250;

    canvas.width = width; 
    canvas.height = height;
    cxt.drawImage(video, 0, 0, width, height);
    var data = canvas.toDataURL('image/png');    
    photo.setAttribute('src', data);
    //e.preventDefault();
    var csrftoken = getCookie('csrftoken');
    var info = data.split(",", 2);

    $.ajax({
        type : "POST",
        url : "/upload/", 
        data : {foto :info[1], csrfmiddlewaretoken: csrftoken},
        dataType : 'json',
        success: function(){
            alert("Imagen guardada en servidor");                       
        }
    });
}

$("#radiotfoto").click(function(){
    $("#video").removeClass("none");
    $("#withOutCameraPic").removeClass("none");
    $("#withCameraPic").addClass("none");
    turnOnCamera();
}); 

$("#btn_start").click(function(){      
    $("#btn_start").addClass("none");
    // Main Buttons
    $("#end").removeClass("none");
    $("#end").addClass("submit noHover");
    $("#ommit").addClass("none");
    $("#ommit").removeClass("submit");
    setTimeout(function() { //QUITO EL TEMPORIZADOR ???????????????????????
        takepicture();
        alert("Foto tomada en teoría xd");
        document.getElementById("end").removeAttribute('disabled');
        $("#end").removeClass("noHover");
    },1000); 
}); 

