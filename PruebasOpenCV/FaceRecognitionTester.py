from tkinter.messagebox import NO
import face_recognition, pickle, os
import cv2 as cv
import numpy as np
from sympy import N

# Equilibrar el num de imgs de TestT, TestF
trainingTimes, recognitionTimes, fp, fn, tp, tn = dict(), dict(), dict(), dict(), dict(), dict()
modelosConf = {'EigenFaces50': 8000, 'EigenFaces150': 8000, 'FisherFaces50':90, 'FisherFaces150':90, 'LBPH50':40, 'LBPH150':40}

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
        
    auxPath = path + "/testT/"
    if not os.path.isdir(auxPath):
        os.mkdir(auxPath)
        
    auxPath = path + "/testF/"
    if not os.path.isdir(auxPath):
        os.mkdir(auxPath)
    
        
def getImgFromDatasetAndSaveFaces(user, path): 
    pathToSearch = "database/images/" + user + path
    pathToSave = "users/" + user + path
    
    for img in os.listdir(pathToSearch):
        try:
            image = cv.imread(pathToSearch + img)
            mainFace = detectMainFace(image)
        
            if len(mainFace) > 0: # not empty
                id = len(os.listdir(pathToSave)) + 1
                cv.imwrite(pathToSave + str(id) + ".jpg", mainFace)
        except:
            print("Esta img fue culera: " + img)
     
            
def loadCascade(cascade):
    cascadePath = cv.data.haarcascades + cascade
    face_cascade = cv.CascadeClassifier()

    if not face_cascade.load(cv.samples.findFile(cascadePath)):
        print('--(!)Error loading face cascade')
        exit(0)

    return face_cascade


def detectMainFace(frame):
    face_cascade = loadCascade("haarcascade_frontalface_alt2.xml")

    #frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    #frame_gray = cv.equalizeHist(frame_gray) # TODO: probar a hacerlo sin esto para ver las diferencias en optimización y cosas de esas
    
    # Detectar caras  
    faces = face_cascade.detectMultiScale(frame) # ver cual es el tamaño mínimo de cara que debería reconocer (no queremos que reconozca caras muy pequeñas)

    biggerFace = {"x":0, "y":0, "w":0, "h":0}

    for (x,y,w,h) in faces:

        #cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2) # TODO: esto creo que debería borrarlo 

        if (biggerFace["w"] * biggerFace["h"]) < (w * h):   # guardar solo la cara más grande (ver a ver si deberíamos coger las 2 caras mas grandes en caso de que las dos estén cerca de tamaño)
            biggerFace["x"], biggerFace["y"], biggerFace["w"], biggerFace["h"] = x, y, w, h
            
    # coger la cara principal y devolverla con frame_gray[y:y+h,x:x+w]
    mainFace = frame[biggerFace["y"]:biggerFace["y"]+biggerFace["h"],biggerFace["x"]:biggerFace["x"]+biggerFace["w"]]

    if len(mainFace) == 0: # empty
        print('No se ha detectado ninguna cara')
    else:
        faceDimentions = (260,260)
        mainFace = cv.resize(mainFace, faceDimentions)

    return mainFace  
     
            
def trainOpenCVAux(images, labels, modelo, user, lenForTraining):

    if modelo == 'EigenFaces': recognizer = cv.face.EigenFaceRecognizer_create()
    elif modelo == 'FisherFaces': recognizer = cv.face.FisherFaceRecognizer_create()
    else: recognizer = cv.face.LBPHFaceRecognizer_create() # modelo == 'LBPH' # asi nos cubrimos tbn en caso de que ponga algo inventado
    
    print("Entrenando reconocedor: " + modelo + "_" + str(lenForTraining) + "_trainer.yml")

    trainingTime = 0
    e1 = cv.getTickCount()

    recognizer.train(images, np.array(labels))
    
    e2 = cv.getTickCount()
    trainingTime = (e2 - e1) / cv.getTickFrequency()
    
    print("El reconocedor ha terminado entrenarse!\n")
    
    path = 'users/' + user + "/recognizer/"
    
    # se guardan los datos del training en el archivo correspondiente
    recognizer.save(path + modelo + "_" + str(lenForTraining) + "_trainer.yml")

    return trainingTime


def trainOpenCV(user, lenForTraining, modelos):    
    images, labels = getTrainingInfo(user)
    
    temp = min(lenForTraining, len(images))

    return trainOpenCVAux(images[0:temp], labels[0:temp], modelos, user, lenForTraining) 


def getTrainingInfo(user):

    images = []
    labels = [] # Think of the label as the subject (the person) this image belongs to, so same subjects (persons) should have the same label. 

    path = "users/" + user + "/train/"

    # FISHERFACES necesita que haya al menos dos tipos de labels 
    image = cv.imread("users\\default\\train\\0.jpg")
    image = cv.resize(image, (260,260))
    frame_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    images.append(frame_gray)
    labels.append(1)
    
    for img in os.listdir(path):

        imagePath = path + img
        image = cv.imread(imagePath)
        frame_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        
        images.append(frame_gray)
        labels.append(0)

    return images, labels


def trainDlib(user, lenForTraining):
    
    trainingImagesPath = 'users\\' + user + '\\train\\'
    recognizersPath = 'users\\' + user +  '\\recognizer\\'
    known_encodings = []
    recognitionTime = 0

    print("Training: dlib_"+ str(lenForTraining) + ".dat")

    #TODO: cambiarlo como si fuera un while e ir aumentando la i
    numImgs = min(len(os.listdir(trainingImagesPath)), lenForTraining)
    for imagePath in os.listdir(trainingImagesPath)[0:numImgs]:
        e1 = cv.getTickCount()
        known_image = face_recognition.load_image_file(trainingImagesPath+imagePath)
        known_encoding = face_recognition.face_encodings(known_image)
        if known_encoding:            
            known_encodings.append(known_encoding[0])
        e2 = cv.getTickCount()
        recognitionTime += (e2 - e1) / cv.getTickFrequency()

    f = open(recognizersPath + "dlib_"+ str(lenForTraining) + ".dat", 'wb')
    pickle.dump(known_encodings, f)
    f.close()
    
    return recognitionTime


def testModelOpenCV(user, lenForTraining, modelo):
      
    if modelo == 'EigenFaces': recognizer = cv.face.EigenFaceRecognizer_create()
    elif modelo == 'FisherFaces': recognizer = cv.face.FisherFaceRecognizer_create()
    elif modelo == 'LBPH': recognizer = cv.face.LBPHFaceRecognizer_create()
    
    pathToSearch1 = "users/" + user + "/testT/"
    pathToSearch2 = "users/" + user + "/testF/"
    pathToSearch3 = "users/" + user + "/recognizer/"
    recognizer.read(pathToSearch3 + modelo + "_" + str(lenForTraining) + "_trainer.yml")
    
    fp, fn, tp, tn, conf, suma_conf, recognitionTime = 0, 0, 0, 0, 0, 0, 0    
    persona = "Unknown"    
        
    print("Empezando el test con el método --> " + modelo + "_" + str(lenForTraining))
    
    for file in os.listdir(pathToSearch1): # para cada imagénes del directorio seleccionadas (bbdd de test)
   
        image_array = cv.imread(pathToSearch1 + file)
        frame_gray = cv.cvtColor(image_array, cv.COLOR_BGR2GRAY)
        
        e1 = cv.getTickCount()
        id, conf = recognizer.predict(frame_gray) # Cuanto mas pequeña sea la confianza, mas nos aseguramos de acertar
        e2 = cv.getTickCount()
        recognitionTime += (e2 - e1) / cv.getTickFrequency()
        
        suma_conf = suma_conf + conf

        if conf > modelosConf[modelo+str(lenForTraining)] or id == 1:   # (conf<40) JUGAR CON LOS VALORES, para cuando tenga una media predefinida que funcione correctamene
            persona = "Unknown"
            fn += 1
        else:
            persona = "Known"
            tp += 1
                        
        print('{}{:>7}{:>20}{:>9}{:>20}{:>6}'.format("Imagen bajo test:", file, "  Prediccion:", persona, "  Confidence:", round(conf,2)))
    
    print("El reconocedor ha terminado el testT!\n")
        
    for file in os.listdir(pathToSearch2): # para cada imagénes del directorio seleccionadas (bbdd de test)
   
        image_array = cv.imread(pathToSearch2 + file)
        frame_gray = cv.cvtColor(image_array, cv.COLOR_BGR2GRAY)
        
        e1 = cv.getTickCount()
        id , conf = recognizer.predict(frame_gray) # Cuanto mas pequeña sea la confianza, mas nos aseguramos de acertar
        e2 = cv.getTickCount()
        recognitionTime += (e2 - e1) / cv.getTickFrequency()
        
        suma_conf = suma_conf + conf

        if conf > modelosConf[modelo+str(lenForTraining)] or id == 1:   # (conf<40) JUGAR CON LOS VALORES, para cuando tenga una media predefinida que funcione correctamene
            persona = "Unknown"
            tn += 1
        else:
            persona = "Known"
            fp += 1
                        
        print('{}{:>7}{:>20}{:>9}{:>20}{:>6}'.format("Imagen bajo test:", file, "  Prediccion:", persona, "  Confidence:", round(conf,2)))
    
    print("El reconocedor ha terminado el testF!")
    
    # se muestran los resultados en el terminal
    print("\nEl numero de aciertos es: " + str(tp + tn) + "/" + str(fp+fn+tp+tn))
    print("El porcentaje de exitos es:", round( ( (tn + tp )/ (fp+fn+tp+tn)) * 100,2), "%")
    print("La media de confidence es:", round((suma_conf/(fp+fn+tp+tn)),2), "\n")    
    
    return recognitionTime/(len(os.listdir(pathToSearch1)) + len(os.listdir(pathToSearch2))), fp, fn, tp, tn


def testModelDlib(user, lenForTraining):

    testingImagesPath = 'users\\' + user + '\\testT\\'
    falseTestingImagesPath = 'users\\' + user + '\\testF\\'
    recognizersPath = 'users\\' + user +  '\\recognizer\\'
    
    f = open(recognizersPath + "dlib_"+ str(lenForTraining) + ".dat", 'rb')
    knownEncodings = pickle.load(f)
    f.close()
    
    testTime, fp, fn, tp, tn = 0, 0, 0, 0, 0

    for image in os.listdir(testingImagesPath):
        unknown_image = face_recognition.load_image_file(testingImagesPath+image)

        e1 = cv.getTickCount()
        unknown_encoding = face_recognition.face_encodings(unknown_image)
        if unknown_encoding:
            results = face_recognition.compare_faces(knownEncodings, unknown_encoding[0])
        e2 = cv.getTickCount()
        testTime += (e2 - e1) / cv.getTickFrequency()
 
        numFalses, numTrues = 0, 0
        for result in results:
            if result:                
                numTrues += 1
            else:                
                numFalses += 1
                print("False negative while TestT: " + testingImagesPath + image)
        
        if numFalses > lenForTraining * 0.05:
            fn += 1
        else:
            tp += 1
        
    for image in os.listdir(falseTestingImagesPath):

        unknown_image = face_recognition.load_image_file(falseTestingImagesPath+image)

        e1 = cv.getTickCount()        
        unknown_encoding = face_recognition.face_encodings(unknown_image)
        if unknown_encoding:
            results = face_recognition.compare_faces(knownEncodings, unknown_encoding[0])
        e2 = cv.getTickCount()
        testTime += (e2 - e1) / cv.getTickFrequency()

        numFalses, numTrues = 0, 0
        for result in results:
            if result:                
                numTrues += 1
                print("False positive while TestF: " + falseTestingImagesPath + image)
            else:                
                numFalses += 1                
        
        if numFalses > lenForTraining * 0.05:
            tn += 1
        else:
            fp += 1

    testTimeAverage = testTime / (len(os.listdir(falseTestingImagesPath)) + len(os.listdir(testingImagesPath)))

    return testTimeAverage, fp, fn, tp, tn


def main(training=0, testing=0): 
    #   parámetros que testear: tiempo de entrenamiento (probar con diferentes tamaños del conjunto de entrenamiento)    --------------------- OK
    #   probar como se comportan teniendo en cuenta el tamaño del conjunto de entrenamiento (falsos positivos, falsos negativos, ...) -------- OK ?
    #   tiempo de reconocimiento.   ---------------------------------------------------------------------------------------------------------- OK
    #   espacio que ocupa cada reconocedor (o algo parecido) --------------------------------------------------------------------------------- OK
    #   calcular el umbral min de fotos a reconocer para aceptar a una persona --------------------------------------------------------------- Ok --> 0.05
    
    filesPath = 'database\\images'
    
    lenForTrial = [50, 150]
    modelos = ['EigenFaces', 'FisherFaces', 'LBPH']
    
    user_id= os.listdir(filesPath)[1]
    
    #for user_id in os.listdir(filesPath):
    print('User: ' + user_id + ' ----------------------------------------------------------')
    #    # Con llamarlas una vez vale
    #prepareFolders(user_id)
    #getImgFromDatasetAndSaveFaces(user_id, "/train/")
    #getImgFromDatasetAndSaveFaces(user_id, "/test/")
                
    if training:   # Para entrenar --------------------------------------------------------------------------
        for i in modelos:
            for j in lenForTrial:
                aux = i + "_" + str(j)
                
                if aux not in trainingTimes.keys():
                    trainingTimes[aux] = []
                
                trainingTimes[aux].append(trainOpenCV(user_id, j, i))
        
        for j in lenForTrial:
            aux = "dlib_" + str(j)
            
            if aux not in trainingTimes.keys():
                trainingTimes[aux] = []
            
            trainingTimes[aux].append(trainDlib(user_id, j))
        
        for key in trainingTimes:        
            print(key + " --> " + str(round(sum(trainingTimes[key])/len(trainingTimes[key]),2))) 
                   
    if testing:    # Para testear ---------------------------------------------------------------------------
        for i in modelos:
            for j in lenForTrial:
                aux = i + "_" + str(j)
                
                if aux not in recognitionTimes.keys():
                    recognitionTimes[aux], fp[aux], fn[aux], tp[aux], tn[aux] = [], 0, 0, 0, 0
                
                testTimeAverage, fpAux, fnAux, tpAux, tnAux = testModelOpenCV(user_id, j, i)
                recognitionTimes[aux].append(testTimeAverage)
                fp[aux] += fpAux
                fn[aux] += fnAux
                tp[aux] += tpAux
                tn[aux] += tnAux
        
        for j in lenForTrial:
            aux = "dlib_" + str(j)
            
            if aux not in recognitionTimes.keys():
                recognitionTimes[aux], fp[aux], fn[aux], tp[aux], tn[aux] = [], 0, 0, 0, 0
            
            testTimeAverage, fpAux, fnAux, tpAux, tnAux = testModelDlib(user_id, j)
            recognitionTimes[aux].append(testTimeAverage)
            fp[aux] += fpAux
            fn[aux] += fnAux
            tp[aux] += tpAux
            tn[aux] += tnAux
            
        for key in recognitionTimes:
            print('{}{}'.format(key + "--> ", str(round(sum(recognitionTimes[key])/len(recognitionTimes[key]),2))))
            print('{}{}{:>10}{}{:>10}{}{:>10}{}'.format( "..... Fp:", str(fp[key]), " Fn:", str(fn[key])," Tp:", str(tp[key])," Tn:", str(tn[key])))
          
          
if __name__ == "__main__":
    main(0,1)

