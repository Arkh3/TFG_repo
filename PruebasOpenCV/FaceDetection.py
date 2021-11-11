import cv2 as cv
from datetime import datetime
import os, os.path
import numpy as np


def loadCascade(cascade):

    cascadePath = cv.data.haarcascades + cascade
    face_cascade = cv.CascadeClassifier()

    if not face_cascade.load(cv.samples.findFile(cascadePath)):
        print('--(!)Error loading face cascade')
        exit(0)

    return face_cascade


def trainModel(images, labels, modelo, user):

    if modelo == 'EigenFaces': recognizer = cv.face.EigenFaceRecognizer_create()
    elif modelo == 'FisherFaces': recognizer = cv.face.FisherFaceRecognizer_create()
    elif modelo == 'LBPH': recognizer = cv.face.LBPHFaceRecognizer_create()

    # TODO: a lo mejor es interesante hacer un estudio de tiempos, atuch en su código tiene la parte de medir tiempos

    print("Entrenando reconocedor...")

    recognizer.train(images,  np.array(labels))

    print("El reconocedor ha terminado entrenarse!")

    path = 'users/' + user + "/recognizer/"
    
    # se guardan los datos del training en el archivo correspondiente
    recognizer.save(path + "trainer.yml")


def getTrainingInfo(user):

    images = []
    labels = [] # Think of the label as the subject (the person) this image belongs to, so same subjects (persons) should have the same label. 

    path = "users/" + user + "/train/"

    for img in os.listdir(path):

        imagePath = path + img

        image = cv.imread(imagePath, 0)

        images.append(image)
        labels.append(0)

    return images, labels 


def recognize(id, face, modelo, user):

    if modelo == 'EigenFaces': recognizer = cv.face.EigenFaceRecognizer_create()
    elif modelo == 'FisherFaces': recognizer = cv.face.FisherFaceRecognizer_create()
    elif modelo == 'LBPH': recognizer = cv.face.LBPHFaceRecognizer_create()

    path = 'users/' + user + "/recognizer/trainer.yml"

    recognizer.read(path)

    labels = {user : 0}

    id_, conf = recognizer.predict(face) # TODO mirar en la documentacion pero se puede hacer que esto te devuelva un % con la confianza que reconoce

    if conf > 0:
        return True
    
    else:
        return False


def detectMainFace(frame):

    face_cascade = loadCascade("haarcascade_frontalface_alt2.xml")

    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    frame_gray = cv.equalizeHist(frame_gray) # probar a hacerlo sin esto para ver las diferencias en optimización y cosas de esas
    
    #-- Detect faces
    faces = face_cascade.detectMultiScale(frame_gray) # ver cual es el tamaño mínimo de cara que debería reconocer (no queremos que reconozca caras muy pequeñas)

    biggerFace = {"x":0, "y":0, "w":0, "h":0}

    for (x,y,w,h) in faces:

        cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2) # TODO: esto creo que debería borrarlo 
        faceROI = frame_gray[y:y+h,x:x+w]                       # y esto no se ni que hace
        

        if (biggerFace["w"] * biggerFace["h"]) < (w * h):   # guardar solo la cara más grande (ver a ver si deberíamos coger las 2 caras mas grandes en caso de que las dos estén cerca de tamaño)
            biggerFace["x"], biggerFace["y"], biggerFace["w"], biggerFace["h"] = x, y, w, h
            

    ## coger la cara principal y devolverla con frame_gray[y:y+h,x:x+w]

    mainFace = frame_gray[biggerFace["y"]:biggerFace["y"]+biggerFace["h"],biggerFace["x"]:biggerFace["x"]+biggerFace["w"]]

    # cv.imshow('Capture - Face detection', mainFace)
    # cv.waitKey(0)

    faceDimentions = (260,260)
    mainFace = cv.resize(mainFace, faceDimentions)

    return mainFace


def saveFace(face, identifier):

    path = "users/" + identifier + '/train/'
    
    id = len(os.listdir(path)) + 1

    cv.imwrite(path + str(id) + ".jpg", face) 


def captureAndSaveFaces(user):

    path = 'PruebasOpenCV\images\\'

    for img in os.listdir(path):
        imagePath = path + img
        img = cv.imread(imagePath)
        mainFace = detectMainFace(img)
        saveFace(mainFace, user)

    """cap = cv.VideoCapture(0) 

    if cap is None or not cap.isOpened(): # TODO: comprobar si existe webcam no? en caso de que no exista dejar loggearse con usuario y contraseña (oAuth2)
        print('Warning: unable to open video source: ', 0)

    for i in range (100):

        rval, img = cap.read()
        img = cv.flip(img, 1, 0)
        #el código de atuch enseña la imagen y la imprime con rectángulos en la cara detectada
        mainFace = detectMainFace(img)
        saveFace(mainFace, user)"""


def prepareFolders(user):

    path = "users/"

    if not os.path.isdir(path):
        os.mkdir(path)

    path += '/' + user

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


    # TODO: sacar fotos y utilizar el modelo entrenado para ver si da acierto o nó

    img = cv.imread("PruebasOpenCV\\recognize\scarlett_johannson.jpg")
    face = detectMainFace(img)
    
    if not(recognize(user, face, 'LBPH', user)):
        print("fallo")
        user = ""

    else:
        print("acierto")

    return user


def register():

    user = input("\nInserte su nombre o DNI: ").lower() 
    userPath = 'users/' + user + "/"
    
    # Comprobamos que no esté repetido 
    while user in os.listdir('users/'):

        print("Ese nombre ya existe... intenta escoger otro diferente.")
        user = input("\nInserte su nombre o DNI: ").lower() 
        userPath = 'users/' + user + "/"

    #Creamos las carpetas correspondientes
    prepareFolders(user)

    # Iniciamos la captura de cara
    # faceCapture(userPath, user)
    # TODO: hacer toda la parte de sacarle fotos, capturar la cara y entrenar un modelo con esas fotos

    #capturar las caras y guardarlas
    captureAndSaveFaces(user)

    images, labels = getTrainingInfo(user) #TODO: getTrainingInfo no funciona bien por los paths
    trainModel(images, labels, 'LBPH', user)
    
    print("Correcto")

    return user


def main():

    prepareFolders("default")

    initUser()


if __name__ == "__main__":
    main()