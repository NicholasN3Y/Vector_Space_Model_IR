#!/usr/bin/python
import re
import nltk
import sys
import math
import getopt
import os
import time
import cPickle as pickle
from collections import defaultdict
from nltk.tokenize import sent_tokenize, word_tokenize

def build_Index(directory) :
	
	index_dict = defaultdict(list)
	docname_list=list()
	# for each document within the directory:
	for docname in next(os.walk(directory))[2]:
		docname_list.append(int(docname))
		
	for docname in sorted(docname_list):
		doc = open(os.path.join(directory, str(docname)), 'r')
		data = doc.readlines()
		doc.close()	
		
		data = " ".join(map(lambda a: a.strip(), data))
					
		#tokenize the document
		sentence = nltk.sent_tokenize(data)
		wordified_sent = map(nltk.word_tokenize, sentence)
			
		#create new Porter stemmer
		stemmer = nltk.PorterStemmer()
			
		for sent in wordified_sent:
			for term in sent:
				term = stemmer.stem(term.lower())
				if (len(index_dict[term]) > 0):
					if(index_dict[term][len(index_dict[term])-1][0] != docname):
						index_dict[term].append((docname, ))
				else:
					index_dict[term.lower()].append((docname, ))
					
		#add list of documents into dictionary
		index_dict['LIST_OF_DOC'].append((docname, ))
	
			
	#add skip pointers
	for term, postings in index_dict.items():
		post_length = len(postings)
		val = int(math.floor(math.sqrt(post_length)))	
		
		#add skip pointer
		for i in range (0, post_length, val):
			if (i + val < post_length):
				postings[i] = (postings[i][0], i+val)
			elif (i != post_length-1):
				postings[i] = (postings[i][0], post_length - 1)
		
	
	
	
	return index_dict

def pickle_Data(index_dict, dictionaryz, postingz):
	#sort, count length and pickle them.
	
	print "dumping pickles into postings file: ", postingz
	term_count_pos = {}
	terms = index_dict.keys()
	postingfile = open(postingz, 'w+b')
	for term in sorted(terms):
		#print term
		docCount = len(index_dict[term])
		term_count_pos[term] = (docCount, postingfile.tell())
		pickle.dump(index_dict[term], postingfile)
	postingfile.close()
	
	print "writing to dictionary file:", dictionaryz
	dictionaryfile = open(dictionaryz, 'w+b')
	pickle.dump(term_count_pos, dictionaryfile)
	dictionaryfile.close()
		
def usage():
    print "usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file"
	
input_directory_i = output_file_d = output_file_p = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-i':
        input_directory_i = a
    elif o == '-d':
        output_file_d = a
    elif o == '-p':
        output_file_p = a
    else:
        assert False, "unhandled option"
if input_directory_i == None or output_file_d == None or output_file_p == None:
    usage()
    sys.exit(2)

start_time = time.time()
Indexed_Dict = build_Index(input_directory_i)
pickle_Data(Indexed_Dict, output_file_d, output_file_p)
elapsed_time = time.time() - start_time
print elapsed_time
