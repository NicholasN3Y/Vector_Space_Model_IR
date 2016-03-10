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
        #querytermlist is tokenized query terms
        #convert it to a dictionary to enable query term count
        #querytermdict: key is term, value is count in the query list
        querytermdict = dict()
        for i in range(0, len(querytermlist)):
                querytermdict.setdefault(querytermlist[i], 0)
                querytermdict[querytermlist[i]] += 1

        #docsWithQuertTerms: { Doc: (dict of query terms : count)}
        docsWithQueryTerms = getDocWithQueryTerms(querytermdict, dictionary, postingsfile)
        #--------12.20pm Thursday
        print repr(docsWithQueryTerms)

        

        
        
        return ["dummy"]

def getDocWithQueryTerms(queryterms, dictionary, posting):
        resultDict = dict()
        for term in queryterms.keys():
                info = dictionary.get(term, None)
                if (info):
                        assert(type(info) is tuple)
                        termPostingList = getDataFromPostings(info[1], posting)
                        #adds the data in termPostingList into resultDict
                        categorizeQueryTermByDoc(term, termPostingList, resultDict)
        return resultDict
                
        
def categorizeQueryTermByDoc(term, postings, dictionary):
        for pair in postings:
                document = pair[0]
                termcount = pair[1]
                dictionary.setdefault(document, dict())
                dictionary[document][term] = termcount
                

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

