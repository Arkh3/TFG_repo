import face_recognition
import os
import cv2 as cv
import pickle
from django.conf import settings


def detectMainFaceCoordinates(frame):

    faces = []
    biggerFace = {"x":0, "y":0, "w":0, "h":0}

    face_locations = face_recognition.face_locations(frame)

    for (top, right, bottom, left) in face_locations:
        faces.append([left, top, right-left, bottom - top])

    
    for (x,y,w,h) in faces:
        if (biggerFace["w"] * biggerFace["h"]) < (w * h):
            biggerFace["x"], biggerFace["y"], biggerFace["w"], biggerFace["h"] = x, y, w, h

    if len(faces) == 0:
        return None

    return biggerFace


def parseImage(rawImagePath, tmpImagesPath):

    ret = False

    image = face_recognition.load_image_file(rawImagePath)

    mainFaceCoordinates = detectMainFaceCoordinates(image)

    if mainFaceCoordinates is not None: # if a face has been found

        cvImage = cv.imread(rawImagePath)

        mainFace = cvImage[mainFaceCoordinates["y"]:mainFaceCoordinates["y"]+mainFaceCoordinates["h"],mainFaceCoordinates["x"]:mainFaceCoordinates["x"]+mainFaceCoordinates["w"]]
        faceDimentions = (260,260)
        mainFace = cv.resize(mainFace, faceDimentions)

        id = len(os.listdir(tmpImagesPath)) + 1
        cv.imwrite(os.path.join(tmpImagesPath, str(id) + ".jpg"), mainFace)
        ret = True

    return ret


def createRecognizer(imagesPath, recognizerPath):

    known_encodings = []

    for imagePath in os.listdir(imagesPath):

        imgPath = os.path.join(imagesPath, imagePath)
        
        known_image = face_recognition.load_image_file(imgPath)
        known_encoding = face_recognition.face_encodings(known_image)
        
        if known_encoding:            
            known_encodings.append(known_encoding[0])

    f = open(recognizerPath, 'wb')
    pickle.dump(known_encodings, f)
    f.close()

    return True


def recognize(recognizerPath, imagesPath):

    numRecognizedImages = 0

    betterImg = [0, None]
    
    ## Cargar el reconocedor
    f = open(recognizerPath, 'rb')
    knownEncodings = pickle.load(f)
    f.close()

    ## Reconocer las imágenes con el reconocedor
    for img in os.listdir(imagesPath):

        imgPath = os.path.join(imagesPath, img)

        image = face_recognition.load_image_file(imgPath)

        unknown_encoding = face_recognition.face_encodings(image)

        if len(unknown_encoding) == 1:
            results = face_recognition.compare_faces(knownEncodings, unknown_encoding[0], tolerance=0.6)
            numFalses = 0
            numTrues = 0

            for result in results:
                if result:
                    numTrues += 1
                else:
                    numFalses += 1

            if numFalses > len(knownEncodings) * settings.RECOGNIZE_TOLERANCE:
                pass
            else:
                if betterImg[0] < numTrues:
                    betterImg[0] = numTrues
                    betterImg[1] = unknown_encoding[0]
                numRecognizedImages += 1


    ret = numRecognizedImages >= settings.RECOGNIZE_MIN_VALID_IMGS

    ## Actualizar el reconocedor con una imágen usada para el inicio de sesión
    if ret:

        if len(knownEncodings) >= settings.MAX_MODEL_IMAGES:
            del knownEncodings[0]
        
        knownEncodings.append(betterImg[1])
        f = open(recognizerPath, 'wb')
        pickle.dump(knownEncodings, f)
        f.close()

    return  ret