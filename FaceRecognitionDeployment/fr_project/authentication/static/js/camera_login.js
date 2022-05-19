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

//TODO: hacer que el boton de start no aparezca hasta que no se haya iniciado la webcam

async function takepictures() {

    $("#loading").addClass("text-info");
    $("#loading").removeClass("text-warning");

    var csrftoken = getCookie('csrftoken');
    canvas = document.getElementById("canvas");
    cxt = canvas.getContext("2d");

    width = 300;
    height = 250; // TODO: hacer que el aspect-ratio siga siendo igual(no deformar)

    video = document.getElementById("video");

    canvas.width = width; 
    canvas.height = height;

    allPhotos = false;
    allRequests = false;
    block = false;

    while (!allPhotos && !allRequests){
        block = true;

        cxt.drawImage(video, 0, 0, width, height);
        var data = canvas.toDataURL('image/png');    
        var info = data.split(",", 2);
        $.ajax({
            type : "POST",
            url : "/login_fr/", 
            data : {foto:info[1], csrfmiddlewaretoken: csrftoken},
            dataType : 'json',
            success: function (response) {
                /* TODO: HAY QUE HACER QUE LA ZONA DE LA CÁMARA NO SE LE PUEDA HACER CLICK Y A LO MEJOR HABRÍA QUE APAGAR LA CAMARA Y PONER UNA IMAGEN CON UN TICK VERDE O ALGO ASI*/
                var aux = JSON.parse(response["allPhotos"]);
                if (aux){
                    allPhotos = true;
                    block = false;
                    window.location.href = "/welcome";
                }
                block = false;
            },
            error: function (response) {
                var aux = response["noEmail"];
                if (aux){
                    window.location.href = "/";
                }else{
                    $("#btn_start").removeClass("btn-primary");
                    $("#btn_start").addClass("btn-warning");
                    $("#btn_start").removeClass("none");
                    $("#correo_equivocado").removeClass("none");
                    $("#contrasenia").removeClass("none");
                    $("#loading").removeClass("text-info");
                    $("#loading").addClass("text-warning");
                    document.getElementById('loading').innerHTML = '¡Error! No se te ha reconocido ¿Quieres reintentar?'
                    document.getElementById('btn_start').innerHTML ="Reintentar";
                    block = false;
                    allRequests = true;
                }
            }
        });
        await delay(200);

        while(block){await delay(50);}
    }
}

$("#radiotfoto").click(function(){
    $("#video").removeClass("none");
    $("#withOutCameraPic").removeClass("none");
    $("#withCameraPic").addClass("none");
    turnOnCamera();
}); 


$("#btn_start").click(function(){      
    $("#btn_start").addClass("none");
    $("#correo_equivocado").addClass("none");
    $("#contrasenia").addClass("none");
    $("#end").addClass("none");
    $("#end").removeClass("submit");
    document.getElementById('loading').innerHTML = "Reconociendo...";
    takepictures();
}); 

//turnOnCamera();
window.onload=turnOnCamera;