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

import win32file
import win32event
import win32con

#0 --------- verify file path

def_watch_path = "C:/Users/Imagi/Documents"
watch_path = input("Please input file path to watch: ")
def_file_path = "C:/Users/Imagi/Documents/Scanned_Documents"
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

namescheme = input("Please input name scheme here: ")
#replace this with OCR first 5 words + date

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
					newname = file_path + "/" + namescheme + str(count) + ".pdf"
					fp = watch_path + "/" + add
					os.rename(fp, newname)
					print(add + " Renamed!")

			old_path_contents = new_path_contents
			win32file.FindNextChangeNotification (change_handle)
			newtimer()
			t.start
			count += 1
			#I guess this is step 4

finally:
	win32file.FindCloseChangeNotification (change_handle)
