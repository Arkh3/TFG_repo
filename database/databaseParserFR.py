import os
import requests

def prepareFolders(id):

    path = "database/images/"

    if not os.path.isdir(path):
        os.mkdir(path)

    path += '/' + id

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


def getImgExtension(imageName):

    file_name, file_extension = os.path.splitext(imageName)

    return file_extension


def processLine(line, path):

    splitLine = line.split()

    id = splitLine[0]
    url = splitLine[1]
    left = splitLine[2]
    top =  splitLine[3]
    right = splitLine[4]
    bottom = splitLine[5]
    pose = splitLine[6]

    if float(pose) > 2: # if its a frontal face
        #download image
        try:
            r = requests.get(url, allow_redirects=True)
            open(path + '\\' + id + getImgExtension(url), 'wb').write(r.content)

        except:
            print('error en el request')


def main():

    filesPath = os.getcwd() + '\\database\\files'

    i = 0
    maxPeople = 10
    maxImgs = 10
    
    for file in os.listdir(filesPath):

        id = file[0:-4]
        prepareFolders(id)

        fileReader = open(filesPath + '\\' + file, 'r')
        line = ""

        j = 0

        while line is not None and j < maxImgs:
            line = fileReader.readline()

            if j < maxImgs * 0.7:
                storePath = "database\\images\\" + id + "\\train"
            else:
                storePath = "database\\images\\" + id + "\\test"


            processLine(line, storePath)
            j += 1
    
        i += 1
        if i >= maxPeople:
            break


if __name__ == "__main__":
    main()