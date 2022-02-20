import os
import requests


def getImgExtension(imageName):

    _ , file_extension = os.path.splitext(imageName)

    return file_extension

def main():

    filesPath = os.getcwd() + '\\database\\files'
    
    maxPeople = 0
    maxImgs = 1000
    
    ext = {}
    for i, file in enumerate(os.listdir(filesPath)):

        id = file[0:-4]

        fileReader = open(filesPath + '\\' + file, 'r')
        line = ""

        j = 0
        while line is not None and j < maxImgs:
            line = fileReader.readline()

           # try:
            splitLine = line.split()
            url = splitLine[1]
            extension = getImgExtension(url)
                        
            if extension not in ext:
                ext[extension] = 1
            else:
                ext[extension] += 1
                    
                
            j = j+1
            #except: 
            #    print(line)
            


            
        if i >= maxPeople:
            break
    
    print(ext)


if __name__ == "__main__":
    main()