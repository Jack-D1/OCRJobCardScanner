import cv2
import numpy
import time
import os
import shutil
from pdf2image import convert_from_path
from PIL import Image, ImageOps
import pytesseract
from termcolor import *


class PDF:
    PDFPAth = ""
    JobNo = 0
    logLevel = 0

    def __init__(self, path, log=0):
        self.PDFPAth = path
        self.logLevel = log
        self.conToJPG(1,self.logLevel)
        self.getJobNo(self.logLevel)
        if self.JobNo == 0:
            print colored("WARNING: Initially failed to detect a Job No, re-attempting using other conversion methods",'yellow')
            global fails
            opToAtt = 2
            while True:
                if opToAtt < 8:
                    self.conToJPG(opToAtt,self.logLevel)
                    self.getJobNo(self.logLevel)
                    if self.JobNo != 0:
                        break
                    else:
                        opToAtt += 1
                else:
                    print colored("ERROR: Failed to detect Job No for this card",'red')
                    fails+=1
                    cprint("INFO: The name for this pdf will be WARNING " + str(fails) + "(Or that but multiple times)",'green')
                    self.JobNo = "WARNING " + str(fails)
                    break

    def conToJPG(self, op,log):
        pages = convert_from_path(self.PDFPAth,250,first_page=1,last_page=1,thread_count=4)
        pages[0].save('temp.jpg','JPEG')
        img = Image.open('temp.jpg')
        img = img.convert('L')
        img.save('out.jpg')
        img = Image.open('out.jpg')
        width, height = img.size
        border = (width*0.4, height * 0.05, width*0.4, height * 0.9)
        img = ImageOps.crop(img,border)
        img.save('out.jpg')
        pil_image = Image.open('out.jpg').convert('RGB')
        open_cv_image = numpy.array(pil_image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        img_grey = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        img = self.apply_threshold(img_grey, op)
        if log != 0:
            cv2.imshow('image', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        cv2.imwrite('out.jpg', img)

    def getJobNo(self,log):
        text = pytesseract.image_to_string(Image.open('out.jpg'))
        for line in text.splitlines():
            for word in line.split():
                if log != 0:
                    print word
                if word.isdigit():
                    if (int(word) > 199999 and int(word) < 400000):
                        self.JobNo = int(word)
                        break

    def apply_threshold(self, img, argument):
        switcher = {
            1: cv2.threshold(cv2.GaussianBlur(img, (9, 9), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            2: cv2.threshold(cv2.GaussianBlur(img, (7, 7), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            3: cv2.threshold(cv2.GaussianBlur(img, (5, 5), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            4: cv2.threshold(cv2.medianBlur(img, 5), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            5: cv2.threshold(cv2.medianBlur(img, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            6: cv2.adaptiveThreshold(cv2.GaussianBlur(img, (5, 5), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, 31, 2),
            7: cv2.adaptiveThreshold(cv2.medianBlur(img, 3), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31,2),
        }
        return switcher.get(argument, "Invalid method")

    def retJobNo(self):
        return self.JobNo


def main():
    for filename in os.listdir(directory):
        start_time = time.time()
        if filename.endswith(".pdf"):
            tempPDF = PDF(directory + "\\" + filename)
            JOBNO = tempPDF.retJobNo()
            fname = JOBNO
            enddir = directory + r"\DONE\\" + str(fname) + ".pdf"
            while True:
                exists = os.path.isfile(enddir)
                if not(exists):
                    break
                fname += str(JOBNO)
                enddir = directory + r"\DONE\\" + str(fname) + ".pdf"
            shutil.move(directory + "\\" + filename, enddir)
            times.append(time.time() - start_time)
            print "Moved Job " + str(fname)

    total = 0
    for i in times:
        total += i
    print total
    print "Average time taken per Job Card: " + str(total/len(times))


if __name__ == '__main__':
    fails = 0
    directory = r"C:\Users\Jack\Documents\JOBS"
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    times = []
    main()
