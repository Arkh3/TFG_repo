# este documento está hecho para testear la función de detectMainFace() de FaceDetection.py

# escoger diferentes haar_cascades, ver diferentes métodos y cómo se comportan
from FaceRecognition import *
import shutil
import face_recognition


def detectFaceTester(frame, cascade):
    
    face_cascade = loadCascade(cascade) 

    frame_gray = frame
    # frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY) # probar a hacer el gris antes y despues de la detección
    # frame_gray = cv.equalizeHist(frame_gray) 

    detectionTime = 0

    e1 = cv.getTickCount()

    faces = face_cascade.detectMultiScale(frame_gray)
    
    e2 = cv.getTickCount()
    detectionTime = (e2 - e1)/ cv.getTickFrequency()

    for (x,y,w,h) in faces:
        cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # cv.imshow('Capture - Faces detected', frame_gray)
    # cv.waitKey(0)

    saveFace(frame_gray, "tester", "\\train\\")

    return detectionTime


def detectFaceTester2(path):

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

    # cv.imshow('Capture - Faces detected', img)
    # cv.waitKey(0)

    saveFace(img, "tester", "\\train\\")

    return detectionTime
        

def captureAndSaveFacesTester():

    path = 'PruebasOpenCV\\testing\\images\\'

    numImgs = 0

    haarCascades = ["haarcascade_frontalface_alt.xml", "haarcascade_frontalface_alt2.xml", "haarcascade_frontalface_alt_tree.xml", "haarcascade_frontalface_default.xml"]
    results = [0,0,0,0,0]

    for img in os.listdir(path):

        numImgs += 1
        imagePath = path + img

        for i in range (len(haarCascades)):
            img = cv.imread(imagePath)
            results[i] += detectFaceTester(img, haarCascades[i])
    
        results[4] += detectFaceTester2(imagePath)

    print("STATS:\n")
    print(" - Image count: ", numImgs, "\n ")
    print(" - Results: ")

    for i in range (len(haarCascades)):
        print(haarCascades[i], " - ", results[i])

    print("face_detection library:", results[i+1])


def test(user):

    # parámetros que testear: tiempo que tarda en reconocer todas las imágenes (probar con diferentes tamaños del conjunto de entrenamiento, 
    #   probar como se comportan (teniendo en cuenta el tamaño del conjunto de entrenamiento) (falsos positivos, falsos negativos, ...)

    testPath = "PruebasOpenCV\\recognize\\"
    trainPath = "PruebasOpenCV\\recognize\\"

    captureAndSaveFacesTester()


def removeTesterFolder():

    pathToRemove = "users\\tester" 
    try:
        shutil.rmtree(pathToRemove)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))


def main():

    global user_id
    user_id = "tester"

    prepareFolders(user_id)

    test(user_id)

    # removeTesterFolder()


if __name__ == "__main__":
    main()