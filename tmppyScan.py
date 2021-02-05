#tmppyscan
import os
import time
import sys
from threading import Timer

#-----------------------
#my file
import preprocessing
#---------------------


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
if not os.path.exists(file_path):
	file_path = "C:/Users/Imagi/OneDrive/Documents/Scanned Documents"		

print("Source Path Used: >" + watch_path)
print("Destination Path Used: >" + file_path)
#5. If 15 minutes (900 seconds) with no new files have passed, close
def newtimer():
	global t
	t = Timer(900.0, timeout)

#1 ---------

def getfullpath(filename, watch_path):	
	full_path = watch_path + '/' + filename
	return full_path

change_handle = win32file.FindFirstChangeNotification (watch_path,0,win32con.FILE_NOTIFY_CHANGE_FILE_NAME)


timeout = time.time() + (60*15)
try:
	old_path_contents = dict ([(f, None) for f in os.listdir (watch_path)])
	#this 'while 1:' should be changed to while 15 minute wait timer has not been reached
	count = 0
	while 1:
		if time.time() > timeout:
			sys.exit()	
		result = win32event.WaitForSingleObject (change_handle, 500)
		if result == win32con.WAIT_OBJECT_0:
			new_path_contents = dict([(f, None) for f in os.listdir (watch_path)])
			added = [f for f in new_path_contents if not f in old_path_contents]
			for add in added:
				if add.endswith(".pdf"):
					fpath = getfullpath(add, watch_path)
					print("fpath: ", fpath)
					#I think this is right?
					namescheme = add
					newname = file_path + "/" + namescheme + ".pdf"
					fp = watch_path + "/" + add
					print(add + " Renamed as: " + newname)
					try:
						os.rename(fp, newname)
					except:
						print("File could not be renamed. Something went wrong. Terminating program.")
						sys.exit()
					timeout = time.time() + (60*15)
					print("timeout: ", timeout)

			old_path_contents = new_path_contents
			win32file.FindNextChangeNotification (change_handle)
			count += 1
			#I guess this is step 4

finally:
	win32file.FindCloseChangeNotification (change_handle)
