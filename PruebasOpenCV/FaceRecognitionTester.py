from FaceRecognition import *
import shutil


def trainTest(images, labels, modelo, user):

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


def test(user):

    # parámetros que testear: tiempo de entrenamiento (probar con diferentes tamaños del conjunto de entrenamiento, 
    #   probar como se comportan (teniendo en cuenta el tamaño del conjunto de entrenamiento) (falsos positivos, falsos negativos, ...)
    #   tiempo de reconocimiento.

    captureAndSaveFaces(user)

    images, labels = getTrainingInfo(user)

    modelos = ['EigenFaces', 'LBPH', 'FisherFaces'] # 'FisherFaces'
    trainingTimes = [0,0,0]
    recognizeTimes = [0,0,0]

    labels[0] = 1 # FISHERFACES necesita que haya al menos dos tipos de labels

    for i in range (len(modelos)):
        trainingTimes[i] += trainTest(images, labels, modelos[i], user)
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


def main():

    user_id = "tester"

    prepareFolders(user_id)

    test(user_id)

    # removeUserFolder(user_id)


if __name__ == "__main__":
    main()


"""#TODO: modificar esta función para que funcione hehe que es un copia pega de atuch
def testearModelo(recognizer):

    if modelo == 'EigenFaces': recognizer.read("modeloEigenFaces.xml")
    if modelo == 'FisherFaces': recognizer.read("modeloFisherFaces.xml")
    if modelo == 'LBPH': recognizer.read("modeloLBPH.xml")


    # etiquetado y lectura de los nombres de cada identidad
    #labels = ['Unknown' ,'Scarlett Johansson' , 'Atuch']
    nombres = ['Scarlett Johansson'] #solo hemos entrenado para ella, por tanto id_ siempre será 0

    # se inicializan los contadores de aciertos, fallos y suma_conf a 0
    aciertos = 0
    fallos = 0
    suma_conf = 0
    userPathAux = userPath + testPath
    
    face_cascade = cv.CascadeClassifier(cv.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    for file in os.listdir(userPathAux): # para cada imagénes del directorio seleccionadas (bbdd de test)
        
        if file.endswith("jpg"): # se lee el archivo si acaba en .jpg (formato de las imagénes)
            subPath = userPathAux + file
            image = Image.open(subPath).convert("L") # mode L: 8-bit pixels, black and white -> una capa en blanco y negro
            image_array = np.array(image, "uint8") # convierte imágenes en array de números, unsigned integer (0 a 255)
            faces = face_cascade.detectMultiScale(image_array, scaleFactor=1.2, minNeighbors=4) # detección de caras
            
            for (x, y, w, h) in faces: # para cada cara en esa imagen
                region_of_interest_gray = cv.resize(image_array[y:y+h, x:x+w], (250, 250)) # región de interés de la imagen
                id_, conf = recognizer.predict(region_of_interest_gray) # predicción de la identidad
                suma_conf = suma_conf + conf

                if conf < 40:   # (conf<40) (conf>0) JUGAR CON LOS VALORES
                    persona = "Known"
                    #if file == nombres[id_]:   #pensar otra condicion
                    #    print("---  ACIERTO  ---")
                    #    aciertos += 1
                    #else:
                    #    fallos += 1                
                    #print("Imagen bajo test:", file, "  Prediccion:", nombres[id_], "  Confidence:", conf)
                else:
                    persona = "Unknown"
                
                print('{}{:>7}{:>20}{:>9}{:>20}{:>6}'.format("Imagen bajo test:", file, "  Prediccion:", persona, "  Confidence:", round(conf,2)))

    # se muestran los resultados en el terminal
    #print("\nEl numero de aciertos es:", aciertos)
    #print("El numero de fallos es:", fallos)
    #print("El numero de imagenes predecidas es:", (aciertos+fallos))
    #print("El porcentaje de exitos es:", ((aciertos/(aciertos+fallos))*100), "%")
    #print("La media de confidence es:", (suma_conf/(aciertos+fallos)))
    
    #return
"""