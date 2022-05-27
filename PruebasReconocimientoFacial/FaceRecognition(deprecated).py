import cv2 as cv
from datetime import datetime
import os, os.path
import numpy as np
#for blinking
import dlib
from math import hypot


def loadCascade(cascade):

    cascadePath = cv.data.haarcascades + cascade
    face_cascade = cv.CascadeClassifier()

    if not face_cascade.load(cv.samples.findFile(cascadePath)):
        print('--(!)Error loading face cascade')
        exit(0)

    return face_cascade


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


def initUser():

    print("\n MENÚ DE INICIO \n")
    print("\t0- Salir")
    print("\t1- Iniciar sesion")
    print("\t2- Registrarse")
    print("\n- Seleccione una opcion:")

    opc = int(input()) #TODO:si no escribe un num hacr algo para que no explote

    while opc < 0 or opc > 2:

        print("\nERROR: Opción incorrecta.")
        print("\n\n MENÚ DE INICIO \n")
        print("\t0- Salir")
        print("\t1- Iniciar sesion")
        print("\t2- Registrarse")
        print("\n- Seleccione una opcion:")
        opc = int(input()) # si no escribe un num hacr algo para que no explote


    modelo = 'LBPH' #'EigenFaces' # 'LBPH', 'FisherFaces'

    if opc == 2:
        register(modelo)
    elif opc == 1:
        logIn(modelo)
    else:
        print("\nFin")


def register(modelo):

    user = input("\nInserte su nombre o DNI: ").lower()
    
    # Comprobamos que no esté repetido 
    while user in os.listdir('users/'):

        print("Ese nombre ya existe... intenta escoger otro diferente.")
        user = input("\nInserte su nombre o DNI: ").lower() 

    # Creamos las carpetas correspondientes
    prepareFolders(user)

    # TODO: crear webcam y comprobar que existe y pasarsela por argumentos

    # Ver si la persona parpadea para saber si es una imagen o una persona
    blink = checkBlink() # TODO: añadirle un límite de tiempo

    if blink:
        # Capturar las caras y guardarlas
        captureAndSaveFaces(user, '/train/', 100) #TODO: hacer un try excepcion, y si falla borrar las carpetas 

        # Iniciamos el entrenamiento con las imagenes tomadas anteriormente
        trainModel(modelo, user)
        
        print("Cuenta %s creada" % user)

    else:
        print("Can't create account: you are not blinking!")

    return user


def logIn(modelo):

    user = input("\nInserte su nombre o DNI: ").lower() 

    # Comprobamos que existe
    while user not in os.listdir("users"):

        print("Mal escrito o no existe...")
        user = input("\nInserte su nombre o DNI: ").lower() 

    # TODO: crear webcam y comprobar que existe y pasarsela por argumentos

    # Ver si la persona parpadea para saber si es una imagen o una persona
    blink = checkBlink() # TODO: añadirle un límite de tiempo

    if blink:
        # Capturar las caras y guardarlas
        captureAndSaveFaces(user, '/test/', 10) # TODO # Pasarle el número de imágenes que debería capturar y guardar (reconociendo y entrenando debería coger diferente numero de imagenes)
    
        if not(recognize(modelo, user)):
            print("FALLO")
            user = ""
        else:
            print("ACIERTO")

    else:
        print("Can't log in account: you are not blinking!")
        user = ""

    return user


def saveFace(face, identifier, path):

    path = "users/" + identifier + path
    
    id = len(os.listdir(path)) + 1

    cv.imwrite(path + str(id) + ".jpg", face) 


def trainModel(modelo, user):

    # Cargar fotos de entrenamiento
    images, labels = getTrainingInfo(user)

    # Crear modelo
    if modelo == 'EigenFaces': recognizer = cv.face.EigenFaceRecognizer_create()
    elif modelo == 'FisherFaces': recognizer = cv.face.FisherFaceRecognizer_create()
    elif modelo == 'LBPH': recognizer = cv.face.LBPHFaceRecognizer_create()

    print("Entrenando reconocedor...")

    recognizer.train(images,  np.array(labels))

    print("El reconocedor ha terminado entrenarse!")

    path = 'users/' + user + "/recognizer/"
    
    # se guardan los datos del training en el archivo correspondiente
    recognizer.save(path + "trainer.yml")


def getTrainingInfo(user):

    images = []
    labels = [] # Think of the label as the subject (the person) this image belongs to, so same subjects (persons) should have the same label. 

    path = "users/" + user + "/train/"

    for img in os.listdir(path):

        imagePath = path + img

        image = cv.imread(imagePath, 0)

        images.append(image)
        labels.append(0)

    return images, labels 


def recognize(modelo, user):

    if modelo == 'EigenFaces': recognizer = cv.face.EigenFaceRecognizer_create()
    elif modelo == 'FisherFaces': recognizer = cv.face.FisherFaceRecognizer_create()
    elif modelo == 'LBPH': recognizer = cv.face.LBPHFaceRecognizer_create()

    path = 'users/' + user + "/recognizer/trainer.yml"
    recognizer.read(path)

    imagesPath = "users/" + user + '/test/'

    aciertos = 0
    fallos = 0

    for img in os.listdir(imagesPath):

        imgPath = imagesPath + img
        image = cv.imread(imgPath, 0)

        id_, conf = recognizer.predict(image) # TODO mirar en la documentacion pero se puede hacer que esto te devuelva un % con la confianza que reconoce

        print(conf)
        if conf < 80: # TODO: jugar con los valores, para mejorar el reconocimiento
            aciertos += 1
        else:
            fallos += 1


    if aciertos > 0: # TODO: jugar con los valores de aciertos y fallos y ver cuando decimos que hemos reconocido a la persona
        print("Num aciertos:", aciertos)
        return True
    
    else:
        return False


def detectMainFace(frame):

    face_cascade = loadCascade("haarcascade_frontalface_alt2.xml")

    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    #frame_gray = cv.equalizeHist(frame_gray) # TODO: probar a hacerlo sin esto para ver las diferencias en optimización y cosas de esas
    
    # Detectar caras  
    faces = face_cascade.detectMultiScale(frame_gray) # ver cual es el tamaño mínimo de cara que debería reconocer (no queremos que reconozca caras muy pequeñas)

    biggerFace = {"x":0, "y":0, "w":0, "h":0}

    for (x,y,w,h) in faces:

        cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2) # TODO: esto creo que debería borrarlo 

        if (biggerFace["w"] * biggerFace["h"]) < (w * h):   # guardar solo la cara más grande (ver a ver si deberíamos coger las 2 caras mas grandes en caso de que las dos estén cerca de tamaño)
            biggerFace["x"], biggerFace["y"], biggerFace["w"], biggerFace["h"] = x, y, w, h
            
    # coger la cara principal y devolverla con frame_gray[y:y+h,x:x+w]
    mainFace = frame_gray[biggerFace["y"]:biggerFace["y"]+biggerFace["h"],biggerFace["x"]:biggerFace["x"]+biggerFace["w"]]

    if len(mainFace) == 0: # empty
        print('No se ha detectado ninguna cara')
    else:
        faceDimentions = (260,260)
        mainFace = cv.resize(mainFace, faceDimentions)

    return mainFace


def captureAndSaveFaces(user, path, numFaces):

    cap = cv.VideoCapture(0, cv.CAP_DSHOW) #Para que no salga un warning

    if cap is None or not cap.isOpened(): 
        print('Warning: unable to open video source: ', 0) # TODO: raise exception o algo así de que no hay webcam (a lo mejor deberíamos ver en alguna función anterior que no se detecta webcam)

    actualFaces = 0

    while numFaces > actualFaces :
        _, img = cap.read()
        #img = cv.flip(img, 1, 0)         # Esto no se si es necesario o no
        cv.imshow("Capturando img", img) 
         
        mainFace = detectMainFace(img)

        if len(mainFace) > 0: # not empty
            saveFace(mainFace, user, path)
            actualFaces += 1


    cap.release()
    cv.destroyAllWindows()


# ---------------------------- blinking functions ---------------------------


def midpoint(p1 ,p2):
    return int((p1.x + p2.x)/2), int((p1.y + p2.y)/2)


def get_blinking_ratio(frame, eye_points, facial_landmarks):
    left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
    right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
    center_top = midpoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
    center_bottom = midpoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))

    #Para pintar una linea verde sobre los ojos y ver como se detecta el parpadeo
    #hor_line = cv.line(frame, left_point, right_point, (0, 255, 0), 2)
    #ver_line = cv.line(frame, center_top, center_bottom, (0, 255, 0), 2)

    hor_line_lenght = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
    ver_line_lenght = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))

    ratio = hor_line_lenght / ver_line_lenght
    return ratio


def checkBlink():
    cap = cv.VideoCapture(0)

    if cap is None or not cap.isOpened():
        print('Warning: unable to open video source: ', 0)

    detector = dlib.get_frontal_face_detector() # Lo he intentado dividir en subfunciones pero va mas lento
    predictor = dlib.shape_predictor("PruebasOpenCV\\dlib_shape_predict\\shape_predictor_68_face_landmarks.dat")
    # TODO: de donde me descargo esto y deberíamos ponerlo en alguna carpeta que se pueda hacer referencia desde el propio proyecto
        
    blinked = False
    while not blinked: # Hasta que no parpadee no empezamos a tomar las fotos

        _, frame = cap.read()        
        frame = cv.flip(frame, 1, 0)   
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        
        faces = detector(gray)
        for face in faces:           
            landmarks = predictor(gray, face)

            left_eye_ratio = get_blinking_ratio(frame,[36, 37, 38, 39, 40, 41], landmarks)
            right_eye_ratio = get_blinking_ratio(frame,[42, 43, 44, 45, 46, 47], landmarks)
            blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2

            if blinking_ratio > 5.7:
                blinked = True
                cv.putText(frame, "BLINKING", (50, 100), cv.FONT_HERSHEY_PLAIN, 2, (255, 0, 0))
            
        cv.putText(frame, "Parpadea para empezar!", (30, 30), cv.FONT_HERSHEY_PLAIN, 1, (46, 204, 113),2)
        cv.imshow("Capturando img", frame)

        if cv.waitKey(1) == ord('q'):     # waitKey(x) espera x ms; waitKey(0) espera indefinidamente; presionas "q" y acaba antes
            break
    
    cap.release()
    cv.destroyAllWindows()

    return blinked


# ---------------------------- blinking end ---------------------------


def main():

    prepareFolders("default")

    initUser()


if __name__ == "__main__":
    main()
    
    
    
    # TODO: Con este cod si le damos varias veces a iniciar sesion no se borrar las imgs anteriores se siguen acumulando, para un prototipo mas real eso no tendria sentido