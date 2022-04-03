import os
import requests
import cv2 as cv

def prepareFolders():

    path = "database/imagesFD/"

    if not os.path.isdir(path):
        os.mkdir(path)

    path = "database/imagesFDMetadata/"

    if not os.path.isdir(path):
        os.mkdir(path)


def prepareFoldersForPerson(person):

    path = "database\\imagesFD\\" + person

    if not os.path.isdir(path):
        os.mkdir(path)

    path = "database\\imagesFDMetadata\\" + person

    if not os.path.isdir(path):
        os.mkdir(path)


def processLine(name, line):

    splitLine = line.split()

    id = splitLine[0]
    url = splitLine[1]
    left = splitLine[2]
    top =  splitLine[3]
    right = splitLine[4]
    bottom = splitLine[5]
    pose = splitLine[6]

    # if its a frontal face
    if float(pose) > 2:
        try:
            extension = os.path.splitext(url)[1]
            r = requests.get(url, allow_redirects=True)

            cont = r.content
            #TODO: si la imagen está entonces no cogerla
            #solo cogemos imágenes cuya request haya fallado o cuya extensión sea .jpg
            if r.status_code in [403,404,522] or (extension != ".jpg" and extension != ".JPG") or r.content == None:
                return False
            else:
                open("database\\imagesFD\\" + name + '\\' + id + os.path.splitext(url)[1], 'wb').write(r.content)
                open("database\\imagesFDMetadata\\" + name + '\\' + id + '.txt', 'wb').write(str.encode(left + ' ' + top + ' ' + right + ' ' + bottom))
                return True

        except:
            print('Error en el request para ' + name + ': ' +  str(id))
            return False


def printRectangles():
    for folder in os.listdir("database\\imagesFD\\"):
        for img in os.listdir("database\\imagesFD\\" + folder):

            file_name, file_extension = os.path.splitext(img)

            try:
                image = cv.imread("database\\imagesFD\\" + folder + '\\' + img)

                info = open("database\\imagesFDMetadata\\" + folder + '\\' + file_name + '.txt', 'r').readline()


                #top, left, bottom, right= info.split()
                left, top, right, bottom = info.split()
                left = round(float(left))
                top = round(float(top))
                right = round(float(bottom))
                bottom = round(float(right))

                cv.rectangle(image, (left, top),(right, bottom), (0, 255, 0), 2)

                cv.imshow(img, image)
                k = cv.waitKey(0) 
            except:
                print('error leyendo la imagen: ' + img)


# descarga maxImgs imagenes de maxPeople a partir de la persona name (si es none descarga desde el principio)
def getImages(filesPath, maxPeople, maxImgs, name = None):

    i = 0
    found = False

    if name == None:
        found = True
    
    for file in os.listdir(filesPath):
        person = file[0:-4]

        if person == name:
            found = True

        if found:
            prepareFoldersForPerson(person)

            fileReader = open(filesPath + '\\' + file, 'r')
            line = ""

            j = 1
            while line is not None and j < maxImgs:
                line = fileReader.readline()

                if(processLine(person, line)):
                    j += 1
        
            i += 1
            if i >= maxPeople:
                break


def main():

    filesPath = os.getcwd() + '\\database\\files'
    prepareFolders()

    getImages(filesPath, 30, 30, name = "Adrienne_Barbeau")

    #printRectangles()

if __name__ == "__main__":
    main()