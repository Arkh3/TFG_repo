from asyncio.windows_events import INFINITE
from FaceRecognition import *
import shutil
import face_recognition
from shapely.geometry import Polygon
import math 
import time


def computeError(faces, metadata):

    #print("Num faces detected: " + str(len(faces)))
    
    falsePositives = len(faces) - 1

    lowerError = 9999999999999999999999999

    img, left, top, width, height = metadata
    left = round(float(left))
    top = round(float(top))
    width = round(float(width))
    height = round(float(height))

    #print("Original face(left, top, right, bottom): ", str(left), str(top), str(left + width), str(top + height))

    originalRectangle = Polygon([(left, top), (left + width, top), (left + width, top + height), (left, top + height)])
 
    for (x,y,w,h) in faces:
    #    print("Detected face(left, top, right, bottom):", str(x), str(y), str(x + w), str(y+h))
        polygon = Polygon([(x, y), (x + w, y), (x + w, y+h), (x,y+h)])
        intersection = polygon.intersection(originalRectangle)
        union = polygon.union(originalRectangle)

        #TODO: SE Pueden ver los falsos positivos si la interseccion es 0 no:?

        error = (union.area - intersection.area) / (originalRectangle.area + 1)
        
    #    print("inteseccion, union, error:", str(intersection.area), str(union.area), str(error))

        if lowerError > error:
            lowerError = error

    return lowerError, falsePositives


def printRectangles(frame, faces, metadata):

    image, left, top, width, height = metadata
    left = round(float(left))
    top = round(float(top))
    width = round(float(width))
    height = round(float(height))

    cv.rectangle(frame,(left, top),(left + width, top + height),(0,0,255),2)

    for (x,y,w,h) in faces:
        cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv.imshow("frame", frame)
    k = cv.waitKey(0) 


def detectFaceTesterOpenCV(frame, cascade, metadata):
    
    face_cascade = loadCascade(cascade) 

    frame_gray = frame

    detectionTime = 0
    e1 = cv.getTickCount()
    faces = face_cascade.detectMultiScale(frame_gray)
    e2 = cv.getTickCount()
    detectionTime = (e2 - e1)/ cv.getTickFrequency()

    if len(faces) == 0:
        falseNegatives = 1
        error = 0
        falsePositives = 0
    else:
        error, falsePositives = computeError(faces, metadata) 
        falseNegatives = 0

    #print("detectionTime error falsePositives falseNegatives:", str(detectionTime), str(error), str(falsePositives), str(falseNegatives))
    #print("----------------------------------------------------------------------------------------")

    #printRectangles(frame, faces, metadata)

    return detectionTime, error, falsePositives, falseNegatives


def detectFaceTesterDlib(image, metadata, opencvimage):

    detectionTime = 0
    e1 = cv.getTickCount()
    face_locations = face_recognition.face_locations(image)
    e2 = cv.getTickCount()
    detectionTime = (e2 - e1)/ cv.getTickFrequency()

    face_locations_aux = []

    for (top, right, bottom, left) in face_locations:
        face_locations_aux.append([left, top, right-left, bottom - top])
        
    # hacemos la suposicion que sollo hay una cara por imagen para los falsos positivos y negativos
    if len(face_locations) == 0:
        falseNegatives = 1
        error = 0
        falsePositives = 0
    else:
        error, falsePositives = computeError(face_locations_aux, metadata) 
        falseNegatives = 0

    #print("detectionTime error falsePositives falseNegatives:", str(detectionTime), str(error), str(falsePositives), str(falseNegatives))
    #print("----------------------------------------------------------------------------------------")

    #printRectangles(opencvimage, face_locations_aux, metadata)

    return detectionTime, error, falsePositives, falseNegatives


def faceDetectionTester(maxImgs):

    methods = ["haarcascade_frontalface_alt.xml", "haarcascade_frontalface_alt2.xml", "haarcascade_frontalface_alt_tree.xml", "haarcascade_frontalface_default.xml", "dlib"]
    results = {}

    for method in methods:
        results[method] = {"time": 0, "errors": 0, "falsePositives": 0, "falseNegatives":0}

    metadata = open('dataset_new\list_bbox_celeba.txt', 'r')
    metadata.readline()
    metadata.readline()

    line = ""

    j = 1

    while line is not None and j < maxImgs:

        line = metadata.readline()

        img, x, y, w, h = line.split()
        x = int(x)
        y = int(y)
        w = int(w)
        h = int(h)


        print(img, end="\r")
        metadt = [img, x, y, w, h]

        image = cv.imread("D:\\Andres\\Escritorio\\TFG\\img_celeba\\" + img)

        for method in methods:
            if method.startswith("haarcascade"): # if opencv
                #print(img, method)
                time, error, fp, fn  = detectFaceTesterOpenCV(image, method, metadt)
                results[method]["time"] += time
                results[method]["errors"] += error ** 2
                results[method]["falsePositives"] += fp
                results[method]["falseNegatives"] += fn

            elif method == "dlib": # if Dlib
                aux = face_recognition.load_image_file("D:\\Andres\\Escritorio\\TFG\\img_celeba\\" + img)
                #print(img, method)
                time, error, fp, fn  = detectFaceTesterDlib(aux, metadt, image)
                results[method]["time"] += time
                results[method]["errors"] += error ** 2
                results[method]["falsePositives"] += fp
                results[method]["falseNegatives"] += fn

        j += 1

    finalError = {}

    for method in methods:

        results[method]["errors"] = math.sqrt(results[method]["errors"]) / (maxImgs - results[method]["falseNegatives"])

        print(" STATS FOR " + method + ":\n")
        print(" - Image count: ", maxImgs)
        print(" - Results: ")
        print("\tThe total error was:",  results[method]["errors"])
        print("\tThe total execution time was:", results[method]["time"])
        print("\tThe total number of false positives:", results[method]["falsePositives"])
        print("\tThe total number of false negatives:", results[method]["falseNegatives"])
        print()


def main():
    faceDetectionTester(2000)


if __name__ == "__main__":
    main()