import cv2
import numpy as np
import time

def ReadFile():
    fCode, fKey, fValue = list(), list(), list()
    for i in range(3):
        fCode.append(open("encoded"+str(i)+".bin", "rb"))
        fKey.append(open("keys"+str(i)+".bin", "rb"))
        fValue.append(open("values"+str(i)+".bin", "rb"))
    fShape = open("shape.bin", "rb")
    return fCode, fKey, fValue, fShape


def AdaptiveDecode(listCode):
    listTmp = list()
    for i in range(0, listCode.__len__(), 3):
        value = listCode[i]*255*255 + listCode[i+1]*255 + listCode[i+2]
        listTmp.append(value)
    return listTmp


def AdaptiveImageShape(listCode):
    listTmp = list()
    for i in range(0, listCode.__len__(), 2):
        value = listCode[i]*255 + listCode[i+1]
        listTmp.append(value)
    return listTmp


def ReadFileCodeToList(file):
    listCode, listTmp = list(), list()
    for value in file.read():
        listCode.append(value)
    listTmp = AdaptiveDecode(listCode)
    return listTmp


def ReadFileDictionaryToDic(fileKey, fileValue):
    dicTmp = dict()
    for value1, value2 in zip(fileKey.read(), fileValue.read()):
        dicTmp.setdefault(value2, str(value1))
    return dicTmp


def ReadFileToShapeImage(fileShape):
    listCode, listTmp = list(), list()
    for value in fileShape.read():
        listCode.append(value)
    listTmp = AdaptiveImageShape(listCode)
    return listTmp


def DecodeLZW(code, dictionary, shape):
    s = ""
    lenDic = dictionary.__len__()
    output = list()
    for value in code:
        charTmp = dictionary.get(value, None)
        if charTmp == None:
            charTmp = s + " " + s.split()[0]
        tmp = str(charTmp)
        output.extend(charTmp.split())
        if s != "":
            tmp = s + " " + charTmp.split()[0]
            dictionary.setdefault(lenDic, tmp)
            lenDic += 1
        s = charTmp
    img = np.reshape(output, (shape[0], shape[1])).astype("uint8")
    return img


if __name__ == "__main__":
    start = time.time()
    fCode, fKey, fValue, fShape = ReadFile()
    code, dictionary, value = list(), list(), list()
    shape = ReadFileToShapeImage(fShape)
    for i in range(3):
        code.append(ReadFileCodeToList(fCode[i]))
        dictionary.append(ReadFileDictionaryToDic(fKey[i], fValue[i]))
        value.append(DecodeLZW(code[i], dictionary[i], shape))
        #print("Done decode channel "+str(i))
    output = cv2.merge((value))
    output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
    #output = cv2.resize(output,None,fx=0.4,fy=0.4)
    cv2.imshow("hello", output)
    end = time.time() - start
    print(end, ' s')
    cv2.waitKey(0)
    cv2.destroyAllWindows()
