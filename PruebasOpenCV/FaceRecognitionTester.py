from FaceRecognition import *
import shutil


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
            

# Mis cambios por aqui arriba -------------------------------------------------------------------

def trainModel(images, labels, modelo, user):

    if modelo == 'EigenFaces': recognizer = cv.face.EigenFaceRecognizer_create()
    elif modelo == 'FisherFaces': recognizer = cv.face.FisherFaceRecognizer_create()
    elif modelo == 'LBPH': recognizer = cv.face.LBPHFaceRecognizer_create()

    print("Entrenando reconocedor...")

    trainingTime = 0
    e1 = cv.getTickCount()

    recognizer.train(images, np.array(labels))
    
    e2 = cv.getTickCount()
    trainingTime = (e2 - e1) / cv.getTickFrequency()
    
    print("El reconocedor ha terminado entrenarse!")
    
    path = 'users/' + user + "/recognizer/"
    
    # se guardan los datos del training en el archivo correspondiente
    recognizer.save(path + modelo + "_trainer.yml")

    return trainingTime


def train(user):

    # parámetros que testear: tiempo de entrenamiento (probar con diferentes tamaños del conjunto de entrenamiento, 
    #   probar como se comportan (teniendo en cuenta el tamaño del conjunto de entrenamiento) (falsos positivos, falsos negativos, ...)
    #   tiempo de reconocimiento.

    #captureAndSaveFaces(user)

    images, labels = getTrainingInfo(user)

    modelos = ['EigenFaces']#, 'LBPH']#, 'FisherFaces'] # 'FisherFaces'
    trainingTimes = [0,0,0]
    recognizeTimes = [0,0,0]

    labels[0] = 1 # FISHERFACES necesita que haya al menos dos tipos de labels
    #labels = [] #TODO: estaba como arriba pero lo he cambiado para las pruebas xd
    
    for i in range (len(modelos)):
        trainingTimes[i] += trainModel(images, labels, modelos[i], user)
        # img = cv.imread("PruebasOpenCV\\recognize\\scarlett_johannson.jpg")
        # face = detectMainFace(img)
        # recognizeTimes[i] += recognize(user, face, modelos[i])

    print("STATS:\n")
    print(" - Training image count:", len(images), "\n")
    print(" - Results: ")

    for i in range (len(modelos)):
        print(modelos[i], " - ", trainingTimes[i], " - ", recognizeTimes[i])


def removeUserFolder(user):

    pathToRemove = "users\\" + user

    try:
        shutil.rmtree(pathToRemove)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))

#TODO: modificar esta función para que funcione hehe que es un copia pega de atuch
def testModel(modelo, user):
      
    if modelo == 'EigenFaces': recognizer = cv.face.EigenFaceRecognizer_create()
    elif modelo == 'FisherFaces': recognizer = cv.face.FisherFaceRecognizer_create()
    elif modelo == 'LBPH': recognizer = cv.face.LBPHFaceRecognizer_create()
    
    pathToSearch = "users/" + user + "/recognizer/"
    recognizer.read(pathToSearch + modelo + "_trainer.yml")


    # etiquetado y lectura de los nombres de cada identidad
    #labels = ['Unknown' ,'Scarlett Johansson' , 'Atuch']
    #nombres = ['Scarlett Johansson'] #solo hemos entrenado para ella, por tanto id_ siempre será 0

    # se inicializan los contadores de aciertos, fallos y suma_conf a 0
    aciertos = 0
    fallos = 0
    suma_conf = 0
    #userPathAux = userPath + testPath
    pathToSearch = "users/" + user + "/test/"
    
    face_cascade = cv.CascadeClassifier(cv.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    for file in os.listdir(pathToSearch): # para cada imagénes del directorio seleccionadas (bbdd de test)
   
        image_array = cv.imread(pathToSearch + file,0)
               
        faces = face_cascade.detectMultiScale(image_array, scaleFactor=1.2, minNeighbors=4) # detección de caras
        
        for (x, y, w, h) in faces: # para cada cara en esa imagen
            #region_of_interest_gray = cv.resize(image_array[y:y+h, x:x+w], (250, 250)) # región de interés de la imagen (sino estuvieran ya normalizadas)
            _, conf = recognizer.predict(image_array) # Cuanto mas pequeña sea la confianza, mas nos aseguramos de acertar
            suma_conf = suma_conf + conf

            if conf > 0:   # (conf<40) JUGAR CON LOS VALORES, para cuando tenga una media predefinida que funcione correctamene
                persona = "Unknown"
                fallos += 1
            else:
                persona = "Known"
                aciertos += 1
                #if file == nombres[id_]:   #pensar otra condicion
                #    print("---  ACIERTO  ---")
                #    aciertos += 1
                #else:
                #    fallos += 1                
                #print("Imagen bajo test:", file, "  Prediccion:", nombres[id_], "  Confidence:", conf)
        
        print('{}{:>7}{:>20}{:>9}{:>20}{:>6}'.format("Imagen bajo test:", file, "  Prediccion:", persona, "  Confidence:", round(conf,2)))
    
    # se muestran los resultados en el terminal
    print("\nEl numero de aciertos es:", aciertos)
    print("El numero de fallos es:", fallos)
    print("El numero de imagenes predecidas es:", (aciertos+fallos))
    print("El porcentaje de exitos es:", round(((aciertos/(aciertos+fallos))*100),2), "%")
    print("La media de confidence es:", round((suma_conf/(aciertos+fallos)),2))
    
    #return


def main():

    user_id = "A.J._Buckley"

    # Con llamarlas la primera vez vale, o mientras trabaje con el mismo num de users
    #prepareFolders(user_id)
    #
    #getImgFromDatasetAndSaveFaces(user_id, "/train/")
    #getImgFromDatasetAndSaveFaces(user_id, "/test/")
    
    #train(user_id)

    testModel('EigenFaces', user_id) # TODO: Por ahora se lo meto a saco pero esto no seria asi, cambiar luego cuando funcione.
    
    #removeUserFolder(user_id)


if __name__ == "__main__":
    main()
