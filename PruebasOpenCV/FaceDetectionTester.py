# este documento está hecho para testear la función de detectMultiscale() de opencv

# escoger diferentes haar_cascades, ver diferentes métodos y cómo se comportan

 # parámetros que testear: tiempo que tarda en reconocer todas las imágenes (falsos positivos, falsos negativos, ...)
from asyncio.windows_events import INFINITE
from FaceRecognition import *
import shutil
import face_recognition
from shapely.geometry import Polygon
import math 

# solo debería haber una cara, si hay mas caras contarlas como falsos positivos
# deberíamos calcular el error con todas las caras reconocidas y coger el mínimo error de todas ellas
# si el numero de caras reconocidas es 0 suponemos que hay un falso negativo
def computeError(faces, metadata):

    #print("Num faces detected: " + str(len(faces)))
    #print("Original face(left, top, right, bottom): " + metadata)

    falsePositives = len(faces) - 1

    lowerError = 9999999999999999999999999

    left, top, right, bottom = metadata.split()
    left = round(float(left))
    top = round(float(top))
    right = round(float(bottom))
    bottom = round(float(right))

    originalRectangle = Polygon([(left, top), (right, top), (right, bottom), (left, bottom)])
 
    for (x,y,w,h) in faces:
        #print("Detected face(left, top, right, bottom):", str(x), str(y), str(x + w), str(y+h))
        polygon = Polygon([(x, y), (x + w, y), (x + w, y+h), (x,y+h)])
        intersection = polygon.intersection(originalRectangle)
        union = polygon.union(originalRectangle)

        error = (union.area - intersection.area) / (originalRectangle.area + 1) # esto desfavorece rectángulos grandes (eso bien) pero favorece rectángulos pequeños (mal)
        
        #print("inteseccion, union, error:", str(intersection.area), str(union.area), str(error))

        if lowerError > error:
            lowerError = error

    return lowerError, falsePositives


def printRectangles(frame, faces, metadata):

    left, top, right, bottom = metadata.split()
    left = round(float(left))
    top = round(float(top))
    right = round(float(bottom))
    bottom = round(float(right))

    cv.rectangle(frame,(left, top),(right, bottom),(0,0,255),2)

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

    #TODO: mejorar el datasetParser para que no coja imágenes vacías

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

    return detectionTime, error, falsePositives, falseNegatives


def captureAndSaveFacesTester():

    baseImagesPath = 'database\\imagesFD\\'
    baseMetadataPath = 'database\\imagesFDMetadata\\'
    methods = ["haarcascade_frontalface_alt.xml", "haarcascade_frontalface_alt2.xml", "haarcascade_frontalface_alt_tree.xml", "haarcascade_frontalface_default.xml", "dlib"]
    
    results = {}
    numImgs = 0

    for method in methods:
        results[method] = {"time": 0, "errors": {}, "falsePositives": 0, "falseNegatives":0}

    for person in os.listdir(baseImagesPath):

        for method in methods:
            results[method]["errors"][person] = 0  

        for img in os.listdir(baseImagesPath + person):

            imagePath = baseImagesPath + person + '\\' + img

            metadataPath = baseMetadataPath + person + '\\' + os.path.splitext(img)[0] + ".txt"
            
            image = cv.imread(imagePath)

            if image is not None:
                numImgs += 1
                metadata = open(metadataPath, 'r').readline()

                for method in methods:
                    if method.startswith("haarcascade"): # if opencv
                        #print(imagePath, method)
                        time, error, fp, fn  = detectFaceTesterOpenCV(image, method, metadata)
                        results[method]["time"] += time
                        results[method]["errors"][person] += error ** 2
                        results[method]["falsePositives"] += fp
                        results[method]["falseNegatives"] += fn

                    elif method == "dlib": # if Dlib
                        img = face_recognition.load_image_file(imagePath)
                        #print(imagePath, method)
                        time, error, fp, fn  = detectFaceTesterDlib(img, metadata, image)
                        results[method]["time"] += time
                        results[method]["errors"][person] += error ** 2
                        results[method]["falsePositives"] += fp
                        results[method]["falseNegatives"] += fn
    
    finalError = {}

    for method in methods:
        finalError[method] = 0

        for person in results[method]["errors"]:
            finalError[method] += results[method]["errors"][person]
            results[method]["errors"][person] = math.sqrt(results[method]["errors"][person]) / numImgs

        finalError[method] = math.sqrt(finalError[method]) / (numImgs - results[method]["falseNegatives"])

        print(" STATS FOR " + method + ":\n")
        print(" - Image count: ", numImgs)
        print(" - Results: ")
        print("\tThe total error was:", finalError[method])
        print("\tThe total execution time was:", results[method]["time"])
        print("\tThe total number of false positives:", results[method]["falsePositives"])
        print("\tThe total number of false negatives:", results[method]["falseNegatives"])
        print()
        #TODO: hacer un estudio de qué personas tenían más error (esto puede ir en future work si no nos da tiempo)


def main():
    captureAndSaveFacesTester()


if __name__ == "__main__":
    main()