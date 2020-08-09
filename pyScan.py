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
#import sched
#import os.path

import win32file
import win32event
import win32con

#0 --------- verify file path

def_file_path = "C:/Users/Imagi/Documents"
file_path = input("Please input file path:")

if file_path is "":
	file_path = def_file_path


#5. If 15 minutes (900 seconds) with no new files have passed, close
def timeout():
	sys.exit()

def newtimer():
	global t
	t = Timer(900.0, timeout)

#1 ---------

namescheme = input("Please input name scheme here:")

#2 ---------
#2. Wait for new .pdf files to appear in the Documents directory
path_to_watch = os.path.abspath (".")

change_handle = win32file.FindFirstChangeNotification (
	path_to_watch,
	0,
	win32con.FILE_NOTIFY_CHANGE_FILE_NAME
	)

try:
	old_path_contents = dict ([(f, None) for f in os.listdir (path_to_watch)])
	#this 'while 1:' should be changed to while 15 minute wait timer has not been reached
	newtimer()
	t.start()
	count = 0
	while 1:
		result = win32event.WaitForSingleObject (change_handle, 500)
		
		if result == win32con.WAIT_OBJECT_0:
			t.cancel()
			new_path_contents = dict ([(f, None) for f in os.listdir (path_to_watch)])
			added = [f for f in new_path_contents if not f in old_path_contents]
			#here is probably where I need to implement step 3...
			if added.endswith(".pdf"):
				newname = namescheme + str(count)  	
				os.rename(added, newname) 
			old_path_contents = new_path_contents
			win32file.FindNextChangeNotification (change_handle)
			newtimer()
			t.start
			count += 1
			#I guess this is step 4

finally:
	win32file.FindCloseChangeNotification (change_handle)


#3 ---------
#3. Once they appear, rename the files and move to a different folder (just rename for now)
#	for file in os.listdir():
#		if file.endswith(".pdf"):	
		
		
