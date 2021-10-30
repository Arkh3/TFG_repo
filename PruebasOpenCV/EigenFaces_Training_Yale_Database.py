import os
import numpy as np
from PIL import Image
import cv2
import pickle
from time import time

# se inicia el temporizador
tiempo_inicial = time()

# se selecciona el directorio de la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.join(BASE_DIR, "ExtendedYaleB")

# se escoge el detector facial de la carpeta "Cascades"
face_cascade = cv2.CascadeClassifier('Cascades/data/haarcascade_frontalface_alt2.xml')

# se crea el algoritmo de reconocimiento facial
recognizer = cv2.face.EigenFaceRecognizer_create()

# se inician las variables
current_id = 0
label_ids = {} # se crea un diccionario vacio
y_labels = []
x_train = []

# bucle para todas las imagénes del directorio seleccionadas
for root, dirs, files in os.walk(image_dir):
    for file in files[1:5]:
        if file.endswith("pgm"):
            path = os.path.join(root, file)
            label = os.path.basename(root).replace(" ", "-").lower()
            print(label, path)

            if label not in label_ids:
                label_ids[label] = current_id
                current_id += 1
                
            id_ = label_ids[label]
            print(label_ids)

            pil_image = Image.open(path).convert("L") # mode L: 8-bit pixels, black and white -> una capa en blanco y negro
            image_array = np.array(pil_image, "uint8") # convierte imágenes en array de números, unsigned integer (0 a 255)
            faces = face_cascade.detectMultiScale(image_array, scaleFactor=1.3, minNeighbors=4) # detección de caras

            for (x, y, w, h) in faces:
                region_of_interest_gray = cv2.resize((image_array[y: y+h, x:x+w]), (260, 260)) # región de interés de la imagen
                x_train.append(region_of_interest_gray) # se crea un array con las matrices de valores de cada imagen
                y_labels.append(id_) # se crea un array con las id de cada imagen -> [0, 1, 2, etc]


# escribe la representación serializada de "labels_ids" en el archivo file (f) que está abierto
with open("labels.pickle", 'wb') as f:
    pickle.dump(label_ids, f)

# training con los datos
recognizer.train(x_train, np.array(y_labels))

# se guardan los datos del training en el archivo correspondiente
recognizer.save("trainer_EigenFaces.yml")

# fin del temporizador
tiempo_final = time()
tiempo_ejecucion = tiempo_final - tiempo_inicial
print("El tiempo de ejecución es de: ", tiempo_ejecucion)