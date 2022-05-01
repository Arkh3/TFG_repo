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

function delay(time) {
    return new Promise(resolve => setTimeout(resolve, time));
}

async function takepictures() {

    const fotos = []
    canvas = document.getElementById("canvas");
    cxt = canvas.getContext("2d");

    texto = document.getElementById('loading').innerHTML = '0%'

    width = 300;
    height = 250; // TODO: hacer que el aspect-ratio siga siendo igual(no deformar)

    video = document.getElementById("video");

    canvas.width = width; 
    canvas.height = height;

    for(var i=0; i < 10; i++){
    
        cxt.drawImage(video, 0, 0, width, height);
        var data = canvas.toDataURL('image/png');    
        var info = data.split(",", 2);

        fotos[i] = info
        texto = document.getElementById('loading').innerHTML = i+ '0%'
        await delay(500)
    }

    document.getElementById('loading').innerHTML = i+ '0%'

    var csrftoken = getCookie('csrftoken');

    $.ajax({
        type : "POST",
        url : "/register3/", 
        data : {fotos :fotos, csrfmiddlewaretoken: csrftoken},
        dataType : 'json',
        success: function (response) {
            document.getElementById("end").removeAttribute('disabled');
            document.getElementById('end').innerHTML ="<span></span><span></span><span></span><span></span>Finalizar";
            $("#loading").addClass("text-info");
            $("#loading").removeClass("text-warning");
            document.getElementById('loading').innerHTML = '¡Reconocedor facial creado con éxito!'
            $("#end").removeClass("none");
            $("#end").addClass("submit");
        },
        error: function (response) {
            document.getElementById('end').innerHTML ="<span></span><span></span><span></span><span></span>Omitir";
            document.getElementById("end").removeAttribute('disabled');
            $("#end").removeClass("none");
            $("#end").addClass("submit");
            $("#btn_start").removeClass("btn-primary");
            $("#btn_start").addClass("btn-warning");
            $("#btn_start").removeClass("none");
            $("#loading").removeClass("text-info");
            $("#loading").addClass("text-warning");
            document.getElementById('loading').innerHTML = 'Error creando el reconocedor facial ¿Quieres reintentar?'
            document.getElementById('btn_start').innerHTML ="Reintentar"
        }
    });
}


$("#btn_start").click(function(){      
    $("#btn_start").addClass("none");
    $("#end").addClass("none");
    $("#end").removeClass("submit");
    takepictures();
}); 

//turnOnCamera();
window.onload=turnOnCamera;