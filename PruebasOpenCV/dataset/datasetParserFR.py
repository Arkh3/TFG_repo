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


def getImgExtension(imageName):

    _ , file_extension = os.path.splitext(imageName)

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
            extension = getImgExtension(url)
            r = requests.get(url, allow_redirects=True)
            
            if r.status_code == 403 or r.status_code == 404 or extension != ".jpg" or extension != ".jpg":
                return False
            else:
                open(path + '\\' + id + extension, 'wb').write(r.content)
                return True                

        except:
            print('Error en el request: ' +  str(id))
            return False


def main():

    filesPath = os.getcwd() + '\\database\\files'
    
    maxPeople = 8
    maxImgs = 250
    
    found = False
    
    for i, file in enumerate(os.listdir(filesPath)):

        id = file[0:-4]
        if id == 'A.R._Rahman': # Persona en concreto para no tener que repetir todo el proceso
            found = True
        
        if found:            
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


                if (processLine(line, storePath)):
                    j += 1
                
            if i >= maxPeople:
                break


if __name__ == "__main__":
    main()