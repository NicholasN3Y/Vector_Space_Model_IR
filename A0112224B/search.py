#!/usr/bin/python
import nltk
import sys
import getopt
import os
import cPickle as pickle
import string

def loadDictionary(filename):
        print "reading In Dictionary"
	dictFile = open(filename, 'r')
	term_count_pos = pickle.load(dictFile)
	dictFile.close()
	return term_count_pos

def preprocess(line):
        stemmer = nltk.PorterStemmer()
        assert (type(line) is str)
        list_of_terms = line.split()
        termified_query = list()
        for term in list_of_terms:
                #remove prepended and appended punctuations
                termified_query.append(str((stemmer.stem(term.lower()))).strip(string.punctuation))
        return termified_query

def evalQuery(querytermlist, dictionary, postingsfile, outputfile):
        print repr(querytermlist)
        
        return ["dummy"]
        

def evaluateQueries(dictionary, posting_filename, queries_filename, output_filename):
	outputfile = open(output_filename, 'w')
	postingsfile = open(posting_filename, 'rb')
	with open(queries_filename, 'r') as queries:
		for query in queries:
                        print "reading query"
                        query = preprocess(query)
                        assert (type(query) is list)
			try:
                                result = evalQuery(query, dictionary, postingsfile, outputfile)
                                assert (type(result) is list)
                                write_result(result, outputfile)
                        except: #catch all exceptions
                                e = sys.exc_info()
                                print "exception thrown", e;
                                write_result(["Error querying"], outputfile)
	outputfile.close()
	postingsfile.close()
			
def getDataFromPostings(position, postingsfile):
	postingsfile.seek(position, 0)
	return pickle.load(postingsfile)
			
def write_result(resultlist, outputfile):
	resultstring = ""
	for item in resultlist:
		resultstring+=(str(item[0])+" ")
	resultstring = resultstring[0:len(resultstring)-1]
	outputfile.write(resultstring+"\n")
		 				
def usage():
    print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"
	
dictionary_file_d = postings_file_p = queries_file_q = output_file_r = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-d':
        dictionary_file_d = a
    elif o == '-p':
        postings_file_p = a
    elif o == '-q':
        queries_file_q = a
    elif o == '-o':
        output_file_r = a	
    else:
        assert False, "unhandled option"
if dictionary_file_d == None or postings_file_p == None or queries_file_q == None or output_file_r == None:
    usage()
    sys.exit(2)
	
termDictionary = loadDictionary(dictionary_file_d)
evaluateQueries(termDictionary, postings_file_p, queries_file_q, output_file_r)

