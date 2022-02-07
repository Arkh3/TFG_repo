import cv2 as cv
from datetime import datetime
import os, os.path
import numpy as np

import dlib
from math import hypot

def loadCascade(cascade):

    cascadePath = cv.data.haarcascades + cascade
    face_cascade = cv.CascadeClassifier()

    #-- 1. Load the cascades
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
    
    modelo = 'EigenFaces'

    if opc == 2:
        register(modelo)
        
    elif opc == 1:
        logIn(modelo)
        
    else:
        print("\nFin")


def register(modelo):

    user = input("\nInserte su nombre o DNI: ").lower() 
    userPath = 'users/' + user + "/"
    
    # Comprobamos que no esté repetido 
    while user in os.listdir('users/'):

        print("Ese nombre ya existe... intenta escoger otro diferente.")
        user = input("\nInserte su nombre o DNI: ").lower() 
        userPath = 'users/' + user + "/"

    #Creamos las carpetas correspondientes
    prepareFolders(user)

    #capturar las caras y guardarlas    
    captureAndSaveFaces2(user) #TODO: hacer un try excepcion, y si falla borrar las carpetas

    # Iniciamos el entrenamiento con las imagenes tomadas anteriormente
    train(modelo, user) 
    
    print("Cuenta %s creada" % user)
    return user


def logIn(modelo):

    user = input("\nInserte su nombre o DNI: ").lower() 
    userPath = "users" + user + "/"

    # Comprobamos que existe
    while user not in os.listdir("users"):

        print("Mal escrito o no existe...")
        user = input("\nInserte su nombre o DNI: ").lower() 
        userPath = "users" + user + "/"


    # TODO: sacar fotos y utilizar el modelo entrenado para ver si da acierto o nó
    face = captureAndCheckFace3(user)
    
    # Esto lo hacemos ya dentro de la funcion captureAndCheckFace2
    #if not(recognize(user, face, modelo, user)):
    #    print("No te hemos podido detectar la cara %s!" % user)
    #else:
    #    print("Bienvenido %s!" % user)

    return user


def saveFace(face, identifier):

    path = "users/" + identifier + '/train/'
    
    id = len(os.listdir(path)) + 1

    cv.imwrite(path + str(id) + ".jpg", face)


def train(modelo, user):
    # Cargando las fotos
    images, labels = getTrainingInfo(user)

    # Creando modelo
    if modelo == 'EigenFaces': recognizer = cv.face.EigenFaceRecognizer_create()
    if modelo == 'FisherFaces': recognizer = cv.face.FisherFaceRecognizer_create()
    if modelo == 'LBPH': recognizer = cv.face.LBPHFaceRecognizer_create()

    # TODO: a lo mejor es interesante hacer un estudio de tiempos, atuch en su código tiene la parte de medir tiempos

    print("Entrenando reconocedor...")

    recognizer.train(images,  np.array(labels))

    print("El reconocedor ha terminado de entrenarse!")

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


def recognize(id, face, modelo, user):

    if modelo == 'EigenFaces': recognizer = cv.face.EigenFaceRecognizer_create()
    if modelo == 'FisherFaces': recognizer = cv.face.FisherFaceRecognizer_create()
    if modelo == 'LBPH': recognizer = cv.face.LBPHFaceRecognizer_create()

    path = 'users/' + user + "/recognizer/trainer.yml"

    recognizer.read(path)

    labels = {user : 0}

    id_, conf = recognizer.predict(face) # TODO mirar en la documentacion pero se puede hacer que esto te devuelva un % con la confianza que reconoce

    if conf > 0: # TODO: jugar con los valores, para mejorar el reconocimiento
        print("Acierto")
        return True
    
    else:
        print("Fallo")
        return False


def detectMainFace(frame):

    face_cascade = loadCascade("haarcascade_frontalface_alt2.xml")

    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY) #Para que no salga un warning
    frame_gray = cv.equalizeHist(frame_gray) # probar a hacerlo sin esto para ver las diferencias en optimización y cosas de esas
    
    #-- Detect faces
    faces = face_cascade.detectMultiScale(frame_gray) # ver cual es el tamaño mínimo de cara que debería reconocer (no queremos que reconozca caras muy pequeñas)

    biggerFace = {"x":0, "y":0, "w":0, "h":0}

    for (x,y,w,h) in faces:

        cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2) # TODO: borrarlo, solo dejarlo para las pruebas

        if (biggerFace["w"] * biggerFace["h"]) < (w * h):   # guardar solo la cara más grande (ver a ver si deberíamos coger las 2 caras mas grandes en caso de que las dos estén cerca de tamaño)
            biggerFace["x"], biggerFace["y"], biggerFace["w"], biggerFace["h"] = x, y, w, h            

    ## coger la cara principal y devolverla con frame_gray[y:y+h,x:x+w]
    mainFace = frame_gray[biggerFace["y"]:biggerFace["y"]+biggerFace["h"],biggerFace["x"]:biggerFace["x"]+biggerFace["w"]]
    
    if not np.any(mainFace): # empty
        print('No se ha detectado ninguna cara')
    else:
        faceDimentions = (260,260)
        mainFace = cv.resize(mainFace, faceDimentions)

    return mainFace#, [(biggerFace["y"], biggerFace["y"]+biggerFace["h"]), (biggerFace["x"],biggerFace["x"]+biggerFace["w"])]


def captureAndSaveFaces(user):
    
    cap = cv.VideoCapture(0, cv.CAP_DSHOW) #Para que no salga un warning

    if cap is None or not cap.isOpened(): # TODO: comprobar si existe webcam no? en caso de que no exista dejar loggearse con usuario y contraseña (oAuth2)
        print('Warning: unable to open video source: ', 0)

    while True:
        _, img = cap.read()
        #img = cv.flip(img, 1, 0)         # Esto no se si es necesario o no
        cv.imshow("Capturando img", img)  
        
        mainFace = detectMainFace(img)

        if np.any(mainFace): # not empty
            saveFace(mainFace, user)

        if cv.waitKey(1) == ord('q'):     # waitKey(x) espera x ms; waitKey(0) espera indefinidamente; presionas "q" y acaba antes
            break     

    cap.release()
    cv.destroyAllWindows()


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


def captureAndSaveFaces2(user): # Estariamos detectando las caras con dlib
    cap = cv.VideoCapture(0)

    detector = dlib.get_frontal_face_detector() # Lo he intentado dividir en subfunciones pero va mas lento
    predictor = dlib.shape_predictor("C:\\Users\\aturi\\anaconda3\\Library\\etc\\dlib_models\\shape_predictor_68_face_landmarks.dat")

    if cap is None or not cap.isOpened(): # TODO: comprobar si existe webcam no? en caso de que no exista dejar loggearse con usuario y contraseña (oAuth2)
        print('Warning: unable to open video source: ', 0)
        
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
    
    for i in range(100):
        _, frame = cap.read()        
        frame = cv.flip(frame, 1, 0)   
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        faces = detector(gray)
        for face in faces:
            a, b, c, d = face.top(), face.left(), face.right(), face.bottom()            
            face_area  = gray[a:d, b:c]
            
            cv.rectangle(frame, (b, a), (c, d), (0, 255, 0), 2)  # TODO: borrarlo, solo dejarlo para las pruebas                                 
                       
            faceDimentions = (260,260)
            face_area = cv.resize(face_area, faceDimentions)
            saveFace(face_area, user) #TODO estariamos guardando cualquier cara, una sol seria poner if len(faces)==1

        cv.imshow("Capturando img", frame)

        if cv.waitKey(1) == ord('q'):     # waitKey(x) espera x ms; waitKey(0) espera indefinidamente; presionas "q" y acaba antes
            break     

    cap.release()
    cv.destroyAllWindows()


def captureAndSaveFaces3(user): # Estariamos detectando las caras con los face_cascade
    cap = cv.VideoCapture(0)

    detector = dlib.get_frontal_face_detector() # Lo he intentado dividir en subfunciones pero va mas lento
    predictor = dlib.shape_predictor("C:\\Users\\aturi\\anaconda3\\Library\\etc\\dlib_models\\shape_predictor_68_face_landmarks.dat")

    if cap is None or not cap.isOpened(): # TODO: comprobar si existe webcam no? en caso de que no exista dejar loggearse con usuario y contraseña (oAuth2)
        print('Warning: unable to open video source: ', 0)
        
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
    
    for i in range(100):
        _, frame = cap.read()        
        frame = cv.flip(frame, 1, 0)   

        mainFace = detectMainFace(frame)

        if np.any(mainFace): # not empty
            saveFace(mainFace, user) #TODO estariamos guardando cualquier cara, una sol seria poner if len(faces)==1

        cv.imshow("Capturando img", frame)

        if cv.waitKey(1) == ord('q'):     # waitKey(x) espera x ms; waitKey(0) espera indefinidamente; presionas "q" y acaba antes
            break     

    cap.release()
    cv.destroyAllWindows()


def captureAndCheckFace(user): # Estariamos reconociendo sin lo del pestañeo: Versión anatigua

    cap = cv.VideoCapture(0, cv.CAP_DSHOW)    

    if cap is None or not cap.isOpened(): # TODO: comprobar si existe webcam no? en caso de que no exista dejar loggearse con usuario y contraseña (oAuth2)
        print('Warning: unable to open video source: ', 0)

    while True:
        _, frame = cap.read()
        frame=cv.flip(frame,1,0)
        
        mainFace = detectMainFace(frame)
        if np.any(mainFace): # not mainFace
                        
            if recognize(user, mainFace, 'EigenFaces', user):
                cv.putText(frame, 'Known', (50, 50), cv.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
            else:
                cv.putText(frame,"Unkown", (50, 50), cv.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))  

        #Mostramos la imagen
        cv.imshow('OpenCV Reconocimiento facial', frame)

        if cv.waitKey(1) == ord('q'):     # waitKey(x) espera x ms; waitKey(0) espera indefinidamente; presionas "q" y acaba antes
            break
    
    cap.release()
    cv.destroyAllWindows()
    return mainFace


def captureAndCheckFace2(user): # Estariamos reconociendo las caras con dlib

    cap = cv.VideoCapture(0, cv.CAP_DSHOW)    
    detector = dlib.get_frontal_face_detector() # Lo he intentado dividir en subfunciones pero va mas lento
    predictor = dlib.shape_predictor("C:\\Users\\aturi\\anaconda3\\Library\\etc\\dlib_models\\shape_predictor_68_face_landmarks.dat")

    if cap is None or not cap.isOpened(): # TODO: comprobar si existe webcam no? en caso de que no exista dejar loggearse con usuario y contraseña (oAuth2)
        print('Warning: unable to open video source: ', 0)

    blinked = False
    while not blinked: # Hasta que no parpadee no empezamos a reconocer
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
        cv.imshow('OpenCV Reconocimiento facial', frame)

        if cv.waitKey(1) == ord('q'):     # waitKey(x) espera x ms; waitKey(0) espera indefinidamente; presionas "q" y acaba antes
            break

    while True:
        _, frame = cap.read()
        frame=cv.flip(frame,1,0)
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        
        faces = detector(gray)
        for face in faces:
            a, b, c, d = face.top(), face.left(), face.right(), face.bottom()            
            face_area  = frame[a:d, b:c] # not mainFace           

            faceDimentions = (260,260)
            face_area = cv.resize(face_area, faceDimentions)

            # Aqui peta no se porque (Was size(src) = (1,202800), size(W) = (67600,91))
            #if recognize(user, face_area, 'EigenFaces', user):
            #    cv.putText(frame, 'Known', (30, 30), cv.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
            #else:
            #    cv.putText(frame,"Unkown", (30, 30), cv.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))  

        #Mostramos la imagen
        cv.imshow('OpenCV Reconocimiento facial', frame)

        if cv.waitKey(1) == ord('q'):     # waitKey(x) espera x ms; waitKey(0) espera indefinidamente; presionas "q" y acaba antes
            break
    
    cap.release()
    cv.destroyAllWindows()
    return face_area 


def captureAndCheckFace3(user): # Estariamos reconociendo las caras con los face_cascade

    cap = cv.VideoCapture(0, cv.CAP_DSHOW)    
    detector = dlib.get_frontal_face_detector() # Lo he intentado dividir en subfunciones pero va mas lento
    predictor = dlib.shape_predictor("C:\\Users\\aturi\\anaconda3\\Library\\etc\\dlib_models\\shape_predictor_68_face_landmarks.dat")

    if cap is None or not cap.isOpened(): # TODO: comprobar si existe webcam no? en caso de que no exista dejar loggearse con usuario y contraseña (oAuth2)
        print('Warning: unable to open video source: ', 0)

    blinked = False
    while not blinked: # Hasta que no parpadee no empezamos a reconocer
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
        cv.imshow('OpenCV Reconocimiento facial', frame)

        if cv.waitKey(1) == ord('q'):     # waitKey(x) espera x ms; waitKey(0) espera indefinidamente; presionas "q" y acaba antes
            break

    while True:
        _, frame = cap.read()
        frame=cv.flip(frame,1,0)
        
        mainFace = detectMainFace(frame)
        if np.any(mainFace): # not mainFace

            if recognize(user, mainFace, 'EigenFaces', user):
                cv.putText(frame, 'Known', (30, 30), cv.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
            else:
                cv.putText(frame,"Unkown", (30, 30), cv.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))  

        #Mostramos la imagen
        cv.imshow('OpenCV Reconocimiento facial', frame)

        if cv.waitKey(1) == ord('q'):     # waitKey(x) espera x ms; waitKey(0) espera indefinidamente; presionas "q" y acaba antes
            break
    
    cap.release()
    cv.destroyAllWindows()
    return mainFace 


def main():

    prepareFolders("default")

    initUser()


if __name__ == "__main__":
    main()

# He añadido funciones nuevas y a alguna le he cambiado en num de argumentos
# dlib.shape_predictor esta en mi ruta local, pero deberia estar en ruta para evitar problemas
# Funciona muchísimo mejor captureAndSaveFaces2 que el 3, y al guardar las img se ve mas distinto
# captureAndCheckFace2 no tira, pero captureAndCheckFace3 si