#this will be the ocr portion of the project
#from medium.com/better-programming/how-to-convert-pdfs-into-searchable-key-words-with-python-85aab86c544f
import PyPDF2
import textract

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

filename = file_path

pdfFileObj = open(filename, 'rb')

pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

num_pages = pdfReader.numPages
count = 0
text = ""

while count < num_pages:
	pageObj = pdfReader.getPage(count)
	count += 1
	text += pageObj.extractText()

if text != "":
	text = text
else:
	text = textract.process(fileurl, method='tesseract', language='eng')

tokens = word_tokenize(text)

stop_words = stopwords.words('english')

keywords = [word for word in tokens if not word in stop_words and not word in punctuations]

