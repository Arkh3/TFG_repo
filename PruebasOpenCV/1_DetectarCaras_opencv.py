import cv2 as cv
from datetime import datetime
import os, os.path
import numpy as np


identifier = "scarlett" # pedir en algún momento el identificador
faceDimentions = (260,260)


def detect(frame, face_cascade):

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

    path = "bbdd/"

    #Si no hay una carpeta con el nombre ingresado entonces se crea
    if not os.path.isdir(path):
        os.mkdir(path)

    path += identifier + "/"
    
    if not os.path.isdir(path):
        os.mkdir(path)
    
    id = len(os.listdir(path)) +1

    cv.imwrite(path + str(id) + ".jpg", face) # Tener creada esa ruta


def loadCascade(cascade):

    cascadePath = cv.data.haarcascades + cascade
    face_cascade = cv.CascadeClassifier()

    #-- 1. Load the cascades
    if not face_cascade.load(cv.samples.findFile(cascadePath)):
        print('--(!)Error loading face cascade')
        exit(0)

    return face_cascade


def train(images, labels):

    # se crea el algoritmo de reconocimiento facial
    recognizer = cv.face.EigenFaceRecognizer_create()

    recognizer.train(images,  np.array(labels))

    path = "recognizer/"

    #Si no hay una carpeta con el nombre ingresado entonces se crea
    if not os.path.isdir(path):
        os.mkdir(path)

    path += identifier + "/"
    
    if not os.path.isdir(path):
        os.mkdir(path)
    
    # se guardan los datos del training en el archivo correspondiente
    recognizer.save(path + "trainer_EigenFaces.yml")


def getTrainingInfo():

    images = []
    labels = [] # Think of the label as the subject (the person) this image belongs to, so same subjects (persons) should have the same label. 

    path = "bbdd/" + identifier + "/"

    for img in os.listdir(path):

        imagePath = path + img

        image = cv.imread(imagePath, 0)

        images.append(image)
        labels.append(0)

    return images, labels 


def recognize(id, face):

    recognizer = cv.face.EigenFaceRecognizer_create()

    path = "recognizer/" + identifier + "/trainer_EigenFaces.yml"

    recognizer.read(path)

    labels = {"scarlet" : 1}

    id_, conf = recognizer.predict(face)

    if conf > 0:
        print("Acierto")
    
    else:
        print("Fallo")


def main():

    face_cascade = loadCascade("haarcascade_frontalface_alt2.xml")

    """path = "images\\"

    for img in os.listdir(path):

        imagePath = path + img
        img = cv.imread(imagePath)

        mainFace = detect(img, face_cascade)

        saveFace(mainFace, identifier)"""

    images, labels = getTrainingInfo()
    train(images, labels)


    img = cv.imread("recognize/scarlett johannson.jpg")
    face = detect(img, face_cascade)
    recognize(identifier, face)


if __name__ == "__main__":
    main()