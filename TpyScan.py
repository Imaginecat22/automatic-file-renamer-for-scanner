#This python script should do the following:
#1. Ask user for the name scheme for files input
#2. Wait for new .pdf files to appear in the Documents directory
#3. Once they appear, rename the files and move to a different folder (just rename for now)
#4. loop back to (2.)
#5. If 15 minutes with no new files have passed, close



import os
import time
import sys
from threading import Timer

#to install missing packages
import subprocess
import pkg_resources

#required = {'win32file', 'win32event', 'win32con', 'pdfminer3', 'spacy'}
#required = {'pdfminer3', 'spacy'}
#installed = {pkg.key for pkg in pkg_resources.working_set}
#missing = required - installed

#if missing:
#	python = sys.executable
#	subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
	#subprocess.check_call([python, '-m', 'spacy', 'download', 'en_core_web_lg'])


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


#for textscheme
try:
	from pdfminer3.layout import LAParams, LTTextBox
except:
	subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfminer3"])
	from pdfminer3.layout import LAParams, LTTextBox

from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import PDFPageAggregator
from pdfminer3.converter import TextConverter
import io

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

#most of this is from: stackoverflow.com/questions/56494070/how-to-use-pdfminer-six-with-python-3
def textscheme(filename, watch_path):
	resource_manager = PDFResourceManager()
	fake_file_handle = io.StringIO()

	converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
	page_interpreter = PDFPageInterpreter(resource_manager, converter)

	full_path = watch_path + '/' + filename
	with open(full_path, 'rb') as fh:
		for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
			page_interpreter.process_page(page)
		text = fake_file_handle.getvalue()

	converter.close()
	fake_file_handle.close()
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
			
	print("New File Name: ", newfilename, ".pdf")
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
			
			#print("added: ")
			#print(added)
			time.sleep(2)
			for add in added:
				if add.endswith(".pdf"):
					outtext = textscheme(add, watch_path)
					namescheme = myparse(outtext)
					time.sleep(2)
					newname = file_path + "/" + namescheme + ".pdf"
					fp = watch_path + "/" + add
					os.rename(fp, newname)
					print(add + " Renamed as: " + namescheme)

			old_path_contents = new_path_contents
			win32file.FindNextChangeNotification (change_handle)
			newtimer()
			t.start
			count += 1
			#I guess this is step 4

finally:
	win32file.FindCloseChangeNotification (change_handle)
