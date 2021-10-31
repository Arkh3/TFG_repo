import cv2 as cv
from datetime import datetime
import os, os.path
import numpy as np


user_id = "default" # pedir en algún momento el identificador

modelo = 'LBPH'

faceDimentions = (260,260)


def loadCascade(cascade):

    cascadePath = cv.data.haarcascades + cascade
    face_cascade = cv.CascadeClassifier()

    #-- 1. Load the cascades
    if not face_cascade.load(cv.samples.findFile(cascadePath)):
        print('--(!)Error loading face cascade')
        exit(0)

    return face_cascade


def train(images, labels):

    if modelo == 'EigenFaces': recognizer = cv.face.EigenFaceRecognizer_create()
    if modelo == 'FisherFaces': recognizer = cv.face.FisherFaceRecognizer_create()
    if modelo == 'LBPH': recognizer = cv.face.LBPHFaceRecognizer_create()

    # TODO: a lo mejor es interesante hacer un estudio de tiempos, atuch en su código tiene la parte de medir tiempos

    print("Entrenando reconocedor...")

    recognizer.train(images,  np.array(labels))

    print("El reconocedor ha terminado entrenarse!")

    path = 'users/' + user_id + "/recognizer/"
    
    # se guardan los datos del training en el archivo correspondiente
    recognizer.save(path + "trainer.yml")


def getTrainingInfo():

    images = []
    labels = [] # Think of the label as the subject (the person) this image belongs to, so same subjects (persons) should have the same label. 

    path = "users/" + user_id + "/train/"

    for img in os.listdir(path):

        imagePath = path + img

        image = cv.imread(imagePath, 0)

        images.append(image)
        labels.append(0)

    return images, labels 


def recognize(id, face):

    if modelo == 'EigenFaces': recognizer = cv.face.EigenFaceRecognizer_create()
    if modelo == 'FisherFaces': recognizer = cv.face.FisherFaceRecognizer_create()
    if modelo == 'LBPH': recognizer = cv.face.LBPHFaceRecognizer_create()

    path = 'users/' + user_id + "/recognizer/trainer.yml"

    recognizer.read(path)

    labels = {user_id : 0}

    id_, conf = recognizer.predict(face)

    if conf > 0:
        print("Acierto")
    
    else:
        print("Fallo")


def detectMainFace(frame):

    face_cascade = loadCascade("haarcascade_frontalface_alt2.xml")

    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    frame_gray = cv.equalizeHist(frame_gray) # probar a hacerlo sin esto para ver las diferencias en optimización y cosas de esas
    
    #-- Detect faces
    faces = face_cascade.detectMultiScale(frame_gray) # ver cual es el tamaño mínimo de cara que debería reconocer (no queremos que reconozca caras muy pequeñas)

    biggerFace = {"x":0, "y":0, "w":0, "h":0}

    for (x,y,w,h) in faces:

        cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        faceROI = frame_gray[y:y+h,x:x+w]

        if (biggerFace["w"] * biggerFace["h"]) < (w * h):   # guardar solo la cara más grande (ver a ver si deberíamos coger las 2 caras mas grandes en caso de que las dos estén cerca de tamaño)
            biggerFace["x"], biggerFace["y"], biggerFace["w"], biggerFace["h"] = x, y, w, h
            

    ## coger la cara principal y devolverla con frame_gray[y:y+h,x:x+w]

    mainFace = frame_gray[biggerFace["y"]:biggerFace["y"]+biggerFace["h"],biggerFace["x"]:biggerFace["x"]+biggerFace["w"]]

    # cv.imshow('Capture - Face detection', mainFace)
    # cv.waitKey(0)

    mainFace = cv.resize(mainFace, faceDimentions)

    return mainFace


def saveFace(face, identifier):

    path = "users/" + user_id + '/train/'
    
    id = len(os.listdir(path)) + 1

    cv.imwrite(path + str(id) + ".jpg", face) 


def captureAndSaveFaces():

    path = 'PruebasOpenCV\images\\'

    for img in os.listdir(path):
        imagePath = path + img
        img = cv.imread(imagePath)
        mainFace = detectMainFace(img)
        saveFace(mainFace, user_id)

    """cap = cv.VideoCapture(0) 

    if cap is None or not cap.isOpened(): # TODO: comprobar si existe webcam no? en caso de que no exista dejar loggearse con usuario y contraseña (oAuth2)
        print('Warning: unable to open video source: ', 0)

    for i in range (100):

        rval, img = cap.read()
        img = cv.flip(img, 1, 0)
        #el código de atuch enseña la imagen y la imprime con rectángulos en la cara detectada
        mainFace = detectMainFace(img)
        saveFace(mainFace, user_id)"""


def prepareFolders():

    path = "users/"

    if not os.path.isdir(path):
        os.mkdir(path)

    path += '/' + user_id

    if not os.path.isdir(path):
        os.mkdir(path)

    auxPath = path + "/train/"

    if not os.path.isdir(auxPath):
        os.mkdir(auxPath)

    auxPath = path + "/test/"

    if not os.path.isdir(auxPath):
        os.mkdir(auxPath)

    auxPath = path + "/recognizer/"

    if not os.path.isdir(auxPath):
        os.mkdir(auxPath)


# Iniciar sesion o registrate. Esto dejarlo para el final, para ahora hacer las pruebas mas rapido

def initUser():

    print("\n MENÚ DE INICIO \n")
    print("\t0- Salir")
    print("\t1- Iniciar sesion")
    print("\t2- Registrarse")
    print("\n- Seleccione una opcion:")

    opc = int(input()) #TODO:si no escribe un num hacr algo para que no explote

    while opc < 0 or opc > 2:

        print("\nERROR: Opción incorrecta.")
        print("\n\n MENÚ DE INICIO \n")
        print("\t0- Salir")
        print("\t1- Iniciar sesion")
        print("\t2- Registrarse")
        print("\n- Seleccione una opcion:")
        opc = int(input()) # si no escribe un num hacr algo para que no explote
    
    if opc == 2:
        register()
        
    elif opc == 1:
        logIn()
        
    else:
        print("\nFin")


def logIn():

    user = input("\nInserte su nombre o DNI: ").lower() 
    userPath = "users" + user + "/"

    # Comprobamos que existe
    while user not in os.listdir("users"):

        print("Mal escrito o no existe...")
        user = input("\nInserte su nombre o DNI: ").lower() 
        userPath = "users" + user + "/"

    global user_id
    user_id = user

    # TODO: sacar fotos y utilizar el modelo entrenado para ver si da acierto o nó

    img = cv.imread("PruebasOpenCV\\recognize\scarlett_johannson.jpg")
    face = detectMainFace(img)
    recognize(user_id, face)


def register():

    user = input("\nInserte su nombre o DNI: ").lower() 
    userPath = 'users/' + user + "/"
    
    # Comprobamos que no esté repetido 
    while user in os.listdir('users/'):

        print("Ese nombre ya existe... intenta escoger otro diferente.")
        user = input("\nInserte su nombre o DNI: ").lower() 
        userPath = 'users/' + user + "/"

    global user_id
    user_id = user
        
    #Creamos las carpetas correspondientes
    prepareFolders()

    # Iniciamos la captura de cara
    # faceCapture(userPath, user)
    # TODO: hacer toda la parte de sacarle fotos, capturar la cara y entrenar un modelo con esas fotos

    #capturar las caras y guardarlas
    captureAndSaveFaces()

    images, labels = getTrainingInfo() #TODO: getTrainingInfo no funciona bien por los paths
    train(images, labels)
    
    print("Correcto")


#TODO: modificar esta función para que funcione hehe que es un copia pega de atuch
def testearModelo(recognizer):

    if modelo == 'EigenFaces': recognizer.read("modeloEigenFaces.xml")
    if modelo == 'FisherFaces': recognizer.read("modeloFisherFaces.xml")
    if modelo == 'LBPH': recognizer.read("modeloLBPH.xml")


    # etiquetado y lectura de los nombres de cada identidad
    #labels = ['Unknown' ,'Scarlett Johansson' , 'Atuch']
    nombres = ['Scarlett Johansson'] #solo hemos entrenado para ella, por tanto id_ siempre será 0

    # se inicializan los contadores de aciertos, fallos y suma_conf a 0
    aciertos = 0
    fallos = 0
    suma_conf = 0
    userPathAux = userPath + testPath
    
    face_cascade = cv.CascadeClassifier(cv.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    for file in os.listdir(userPathAux): # para cada imagénes del directorio seleccionadas (bbdd de test)
        
        if file.endswith("jpg"): # se lee el archivo si acaba en .jpg (formato de las imagénes)
            subPath = userPathAux + file
            image = Image.open(subPath).convert("L") # mode L: 8-bit pixels, black and white -> una capa en blanco y negro
            image_array = np.array(image, "uint8") # convierte imágenes en array de números, unsigned integer (0 a 255)
            faces = face_cascade.detectMultiScale(image_array, scaleFactor=1.2, minNeighbors=4) # detección de caras
            
            for (x, y, w, h) in faces: # para cada cara en esa imagen
                region_of_interest_gray = cv.resize(image_array[y:y+h, x:x+w], (250, 250)) # región de interés de la imagen
                id_, conf = recognizer.predict(region_of_interest_gray) # predicción de la identidad
                suma_conf = suma_conf + conf

                if conf < 40:   # (conf<40) (conf>0) JUGAR CON LOS VALORES
                    persona = "Known"
                    #if file == nombres[id_]:   #pensar otra condicion
                    #    print("---  ACIERTO  ---")
                    #    aciertos += 1
                    #else:
                    #    fallos += 1                
                    #print("Imagen bajo test:", file, "  Prediccion:", nombres[id_], "  Confidence:", conf)
                else:
                    persona = "Unknown"
                
                print('{}{:>7}{:>20}{:>9}{:>20}{:>6}'.format("Imagen bajo test:", file, "  Prediccion:", persona, "  Confidence:", round(conf,2)))

    # se muestran los resultados en el terminal
    #print("\nEl numero de aciertos es:", aciertos)
    #print("El numero de fallos es:", fallos)
    #print("El numero de imagenes predecidas es:", (aciertos+fallos))
    #print("El porcentaje de exitos es:", ((aciertos/(aciertos+fallos))*100), "%")
    #print("La media de confidence es:", (suma_conf/(aciertos+fallos)))
    
    #return


def main():

    prepareFolders()

    initUser()


if __name__ == "__main__":
    main()