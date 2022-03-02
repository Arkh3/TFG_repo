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

            #solo cogemos imágenes cuya request haya fallado o cuya extensión sea .jpg
            if r.status_code == 403 or r.status_code == 404 or (extension != ".jpg" and extension != ".JPG"):
                return False
            else:
                open("database\\imagesFD\\" + name + '\\' + id + os.path.splitext(url)[1], 'wb').write(r.content)
                open("database\\imagesFDMetadata\\" + name + '\\' + id + '.txt', 'wb').write(str.encode(left + ' ' + top + ' ' + right + ' ' + bottom))
                return True

        except:
            print('Error en el request: ' +  str(id))
            return False


def printRectangles():

    for img in os.listdir("database\\imagesFD\\"):

        file_name, file_extension = os.path.splitext(img)
        try:
            image = cv.imread("database\\imagesFD\\" + img)

            info = open("database\\imagesMetadataFD\\" + file_name + '.txt', 'r').readline()

            left, top, right, bottom = info.split()
            left = round(float(left))
            top = round(float(top))
            right = round(float(bottom))
            bottom = round(float(right))

            cv.rectangle(image,(left, top),(right, bottom),(0,255,0),2)

            cv.imshow(img, image)
            k = cv.waitKey(0) 
        except:
            print('error leyendo la imagen: ' + img)


def main():

    filesPath = os.getcwd() + '\\database\\files'
    prepareFolders()

    i = 0
    maxPeople = 5
    maxImgs = 20
    
    for file in os.listdir(filesPath):
        person = file[0:-4]

        path = "database\\imagesFD\\" + person

        if not os.path.isdir(path):
            os.mkdir(path)

        path = "database\\imagesFDMetadata\\" + person

        if not os.path.isdir(path):
            os.mkdir(path)

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

    #printRectangles()


if __name__ == "__main__":
    main()