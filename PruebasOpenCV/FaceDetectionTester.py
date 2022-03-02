# este documento está hecho para testear la función de detectMultiscale() de opencv

# escoger diferentes haar_cascades, ver diferentes métodos y cómo se comportan

 # parámetros que testear: tiempo que tarda en reconocer todas las imágenes (falsos positivos, falsos negativos, ...) ver el error para cada
 # persona por separado y ver los errores más altos para ver si reconoce mal a algun tipo de persona por etnia
from asyncio.windows_events import INFINITE
from FaceRecognition import *
import shutil
import face_recognition
from shapely.geometry import Polygon

# solo debería haber una cara, si hay mas caras contarlas como falsos positivos
# deberíamos calcular el error con todas las caras reconocidas y coger el mínimo error de todas ellas
# si el numero de caras reconocidas es 0 suponemos que hay un falso negativo
def computeError(faces, metadata):

    print("Num faces detected: " + str(len(faces)))
    print("Original face(left, top, right, bottom): " + metadata)

    falsePositives = len(faces) - 1

    lowerError = 9999999999999999999999999

    left, top, right, bottom = metadata.split()
    left = round(float(left))
    top = round(float(top))
    right = round(float(bottom))
    bottom = round(float(right))

    originalRectangle = Polygon([(left, top), (right, top), (right, bottom), (left, bottom)])

    for (x,y,w,h) in faces:

        print("Detected face(left, top, right, bottom):", str(x), str(y), str(x + w), str(y+h))
        polygon = Polygon([(x, y), (x + w, y), (x + w, y+h), (x,y+h)])
        #TODO: imprimir ambos polígonos a ver como se crean + imprimir los rectangulos en las imágenes para ver como actua
        intersection = polygon.intersection(originalRectangle)
        union = polygon.union(originalRectangle)

        error = union.area - intersection.area # esto desfavorece rectángulos grandes (eso bien) pero favorece rectángulos pequeños (mal)

        print("inteseccion, union, error:", str(intersection.area), str(union.area), str(error))

        if lowerError > error:
            lowerError = error

    #TODO: terminar de calcular el error como pone en la memoria (hay que dividir entre el la resolucion de la imagen o algo)
    return lowerError, falsePositives


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

    print("detectionTime error falsePositives falseNegatives:", str(detectionTime), str(error), str(falsePositives), str(falseNegatives))
    print("----------------------------------------------------------------------------------------")

    printRectangles(frame, faces, metadata)

    return detectionTime, error, falsePositives, falseNegatives


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


def detectFaceTester2(path, originalRectangle):

    image = face_recognition.load_image_file(path)

    detectionTime = 0
    e1 = cv.getTickCount()

    face_locations = face_recognition.face_locations(image)

    e2 = cv.getTickCount()
    detectionTime = (e2 - e1)/ cv.getTickFrequency()

    img = cv.imread(path)

    for (left, bottom, right, top) in face_locations:

        cv.line(img, (top, left), (top , right), (0, 255, 0), thickness=2)
        cv.line(img, (bottom, left), (bottom , right), (0, 255, 0), thickness=2)
        cv.line(img, (top, left), (bottom , left), (0, 255, 0), thickness=2)
        cv.line(img, (top, right), (bottom , right), (0, 255, 0), thickness=2)

    saveFace(img, "tester", "\\train\\")

    return detectionTime, computeError(face_locations, originalRectangle)


def captureAndSaveFacesTester():

    baseImagesPath = 'database\\imagesFD\\'
    baseMetadataPath = 'database\\imagesFDMetadata\\'
    methods = ["haarcascade_frontalface_alt.xml", "haarcascade_frontalface_alt2.xml", "haarcascade_frontalface_alt_tree.xml", "haarcascade_frontalface_default.xml", "dlib"]
    
    results = {}
    numImgs = 0

    for method in methods:
        results[method] = {"time": 0, "errors": [], "falsePositives": 0, "falseNegatives":0}

    for person in os.listdir(baseImagesPath):
        for img in os.listdir(baseImagesPath + person):
            
            numImgs += 1
            imagePath = baseImagesPath + person + '\\' + img
            metadataPath = baseMetadataPath + person + '\\' + os.path.splitext(img)[0] + ".txt"

            metadata = open(metadataPath, 'r').readline()

            for method in methods:
                if method.startswith("haarcascade"): # if opencv
                    img = cv.imread(imagePath)
                    print(imagePath, method)
                    print()
                    time, error, fp, fn  = detectFaceTesterOpenCV(img, method, metadata)
                    results[method]["time"] += time
                    results[method]["errors"].append(error)
                    results[method]["falsePositives"] += fp
                    results[method]["falseNegatives"] += fn

                #elif method == "dlib": # TODO
                #    time, error, fp += detectFaceTester2(imagePath)
                #    times[4] += time
                #    RMSE[4] += error
                #    falsePositives[4] += fp

        #TODO: Compute RMSE

        # TODO: Print stats
        """print(" STATS FOR " + person + ":\n")
        print(" - Image count: ", numImgs, "\n ")
        print(" - Results: ")

        #TODO: PRINT RMSE Y FALSE POSITIVES

        for i in range (len(haarCascades)):
            print(haarCascades[i], " - ", times[i])

        print("face_detection library:", times[i+1])"""


def main():

    captureAndSaveFacesTester()


if __name__ == "__main__":
    main()