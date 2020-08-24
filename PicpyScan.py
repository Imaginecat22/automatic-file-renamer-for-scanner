import os
import time
import sys
from threading import Timer

#to install missing packages
import subprocess

#to convert for OCR purposes
try:
	from pdf2image import convert_from_path
except:
	subprocess.check_call([sys.executable, "-m", "pip", "install", "pdf2image"])
	#subprocess.check_call(["conda", "install", "-c", "conda-forge", "poppler"])
	from pdf2image import convert_from_path


#for folder watching
try:
        import win32file
except:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
        import win32file

try:
        import win32event
except:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "win32event"])
        import win32event
        
try:
        import win32con
except:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "win32con"])
        import win32con


import io

#for ocr and image processing
try:
	from PIL import Image
except:
	subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
	from PIL import Image

try:
	import pytesseract
except:
	subprocess.check_call([sys.executable, "-m", "pip", "install", "pytesseract"])
	import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

try:
	import cv2
except:
	subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python"])
	import cv2
	
	

#for get_hotwords and myparse
try:
	import spacy
except:
	subprocess.check_call([sys.executable, "-m", "pip", "install", "spacy"])
	import spacy
	
from collections import Counter
from string import punctuation
#nlp = spacy.load("en_core_web_lg")
try:
	import en_core_web_lg
except:
	subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_lg"])
	import en_core_web_lg

nlp = en_core_web_lg.load()

import dateutil.parser as dparser
import datetime
import re

#0 --------- verify file path

def_watch_path = "C:/Users/Imagi/OneDrive/Documents"
#def_watch_path = "C:/Users/Imagi/Documents"
watch_path = input("Please input file path to watch: ")
def_file_path = "C:/Users/Imagi/OneDrive/Documents/Scanned_Documents"
#def_file_path = "C:/Users/Imagi/Documents/Scanned_Documents"
file_path = input("Please input file path to place renamed document: ")

if watch_path is "":
	watch_path = def_watch_path
	
if file_path is "":
	file_path = def_file_path

print("Source Path Used: >" + watch_path)
print("Destination Path Used: >" + file_path)
#5. If 15 minutes (900 seconds) with no new files have passed, close
def timeout():
	sys.exit()

def newtimer():
	global t
	t = Timer(900.0, timeout)

#1 ---------

def getfullpath(filename, watch_path):	
	full_path = watch_path + '/' + filename
	return full_path

def ocr_convert(file_path, full_path):
	pages = convert_from_path(file_path, 600)
	save_path = full_path + '/' + 'imgtemp' 
	print("save path: ", save_path)
	count = 0
	for page in pages:
		count += 1
		img_path = save_path + '/img_' + str(count) + '.jpg'
		print("imgpath: ", img_path)
		#img_path = 'img_' + str(count) + '.jpg'
		page.save(img_path, 'JPEG') 
	#should I return img path, too?
	return save_path


def ocr(save_path):
	text = ''
	for filename in os.listdir(save_path):	
		img_path = save_path + '/' + filename
		#img = cv2.imread(filename)
		#get grayscale image
		#custom_config = r'--oem 3 --psm 6'
		text += pytesseract.image_to_string(Image.open(img_path))    #img, config=custom_config)	
	return text

#most of this is from medium.com/better-programming/extract-keywords-using-spacy-in-python-4a8415478fbf
def get_hotwords(text):
	result = []
	pos_tag = ['PROPN', 'ADJ', 'NOUN']
	doc = nlp(text.lower())
	for token in doc:
		if(token.text in nlp.Defaults.stop_words or token.text in punctuation):
			continue
		if(token.pos_ in pos_tag):
			result.append(token.text)
	return result

def myparse(text):
	
	#this gets 5 keywords from the text
	output = set(get_hotwords(text))
	hottext = ""
	count = 0
	newfilename = ""
	#print("Hotwords: ", output)
	regex = re.compile('/')
	for word in output:
		hottext += word
		hottext += " "
			
		if (count < 5) and (regex.search(word) == None):
			newfilename += word
			if count < 4:
				newfilename += "_"
			count += 1
			
	print("New File Name: ", newfilename, ".jpg")
	#this gets the date from the text (hopefully)
	try:
                date = dparser.parse(hottext, fuzzy=True)
                #together they make the new filename
                newfilename += "["
                newfilename += date.strftime("%Y-%m-%d")
                newfilename += "]"
	except:
                print("No Date Found")
	return newfilename
		
			
#2 ---------
#2. Wait for new .pdf files to appear in the Documents directory

change_handle = win32file.FindFirstChangeNotification (watch_path,0,win32con.FILE_NOTIFY_CHANGE_FILE_NAME)


try:
	old_path_contents = dict ([(f, None) for f in os.listdir (watch_path)])
	#this 'while 1:' should be changed to while 15 minute wait timer has not been reached
	newtimer()
	t.start()
	count = 0
	while 1:
		result = win32event.WaitForSingleObject (change_handle, 500)
			
		if result == win32con.WAIT_OBJECT_0:
			t.cancel()
			new_path_contents = dict([(f, None) for f in os.listdir (watch_path)])
			added = [f for f in new_path_contents if not f in old_path_contents]
			time.sleep(1)
			for add in added:
				if add.endswith(".pdf"):
					fpath = getfullpath(add, watch_path)
					print("fpath: ", fpath)
					imgs_path = ocr_convert(fpath,file_path)
					outtext = ocr(imgs_path)
					namescheme = myparse(outtext)
					newname = file_path + "/" + namescheme + ".pdf"
					fp = watch_path + "/" + add
					try:
						os.rename(fp, newname)
					except:
						print("File could not be renamed. Something went wrong. Terminating program.")
						sys.exit()
					print(add + " Renamed as: " + namescheme)

			old_path_contents = new_path_contents
			win32file.FindNextChangeNotification (change_handle)
			newtimer()
			t.start
			count += 1
			#I guess this is step 4

finally:
	win32file.FindCloseChangeNotification (change_handle)
