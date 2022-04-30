import face_recognition
import os
import cv2 as cv
import pickle


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


def cleanDirectory(path):
    
    for file in os.listdir(path):
        os.remove(os.path.join(path, file))


def parseImages(imagesPath, tmpImagesPath):

    ret = 0

    cleanDirectory(tmpImagesPath)

    for imageName in os.listdir(imagesPath):

        imagePath = os.path.join(imagesPath, imageName)

        image = face_recognition.load_image_file(imagePath)

        mainFaceCoordinates = detectMainFaceCoordinates(image)

        if mainFaceCoordinates is not None: # if a face has been found

            cvImage = cv.imread(imagePath)

            mainFace = cvImage[mainFaceCoordinates["y"]:mainFaceCoordinates["y"]+mainFaceCoordinates["h"],mainFaceCoordinates["x"]:mainFaceCoordinates["x"]+mainFaceCoordinates["w"]]
            faceDimentions = (260,260)
            mainFace = cv.resize(mainFace, faceDimentions)

            id = len(os.listdir(tmpImagesPath)) + 1
            cv.imwrite(os.path.join(tmpImagesPath, str(id) + ".jpg"), mainFace)
            ret += 1

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

    cleanDirectory(imagesPath)
    os.rmdir(imagesPath)


    return True


#TODO: hay que asegurarse de que las imagenes en imagespath son 5
def recognize(recognizerPath, imagesPath):

    numRecognizedImages = 0
    
    f = open(recognizerPath, 'rb')
    knownEncodings = pickle.load(f)
    f.close()

    for img in os.listdir(imagesPath):

        imgPath = os.path.join(imagesPath, img)

        image = face_recognition.load_image_file(imgPath)

        unknown_encoding = face_recognition.face_encodings(image, known_face_locations=None)# TODO: se le pueden pasar las localizaciones de las caras en la imagen ( en nuesttro caso hay solo una localización y las cordenadas son las esquinas de toda la imagen)

        if len(unknown_encoding) == 1:
            results = face_recognition.compare_faces(knownEncodings, unknown_encoding[0], tolerance=0.6)
            numFalses = 0
            numTrues = 0

            for result in results:
                if result:
                    numTrues += 1
                else:
                    numFalses += 1

            tolerance =  1/6 # the lower this is, the better (but it might not recongize anyone if its too low)

            if numFalses > len(knownEncodings) * tolerance:
                print("Image " + imgPath + " not recognized with recognizer " + recognizerPath)
            else:
                print("Image " + imgPath + " was recognized!")
                numRecognizedImages += 1
        else:
            print("While encoding: " + str(len(unknown_encoding)) + " faces where found in " + imgPath + " (only 1 face should be found)")

    return  numRecognizedImages >= 4