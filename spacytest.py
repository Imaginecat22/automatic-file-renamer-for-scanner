import spacy
from collections import Counter
from string import punctuation

nlp = spacy.load("en_core_web_lg")

#import en_core_web_lg
#nlp = en_core_web_lg.load()

def get_hotwords(text):
	result = []
	pos_tag = ['PROPN', 'ADJ', 'NOUN']
	doc = nlp(text.lower())
	for token in doc:
		if(token.text in nlp.Defaults.stop_words or token.text in punctuation):
			continue:
		if(token.pos_ in pos_tag):
			result.append(token.text)
	return result

output = set(get_hotwords(text))
