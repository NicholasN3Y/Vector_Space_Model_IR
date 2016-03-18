#!/usr/bin/python
import nltk
import sys
import getopt
import os
import cPickle as pickle
import string
import math

NUM_RESULTS_TO_SHOW = 10
NUM_CANDIDATE_TO_CONSIDER = 200
#placeholder for list of documents, to be filled in afterwards
dictOfDoc=dict()

def loadDictionary(filename):
        #print "reading In Dictionary"
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

def logtf(count):
        return math.log(count, 10) + 1

def idf(dictionary, qterm):
        #print "doccount", dictionary["LIST_OF_DOC"][0]
        if (dictionary.get(qterm) != None):
                #print "df", dictionary[qterm][0]
                #return math.log(dictionary["LIST_OF_DOC"][0]/ dictionary[qterm][0])
                return math.log(dictionary["LIST_OF_DOC"][0])- math.log(dictionary[qterm][0])
        else:
                #print "df", "0"
                return 0
'''
docs: refers to list of docId sorted by number of query terms that appear in it
docDict: dictionary {doc:{query terms : count in doc}}
querydict {term: count in query list}
'''                  
def computeRank(dictionary, docs, docDict, queryDict, postingsfile):
        q = normalize_q_vector(dictionary,queryDict)
        dict_d = dict_normalize_d_vector(dictionary, docs, docDict, postingsfile)
        rankscores = dict()
        for d, vect in dict_d.items():
                score = 0
                for term, wt in vect.items():
                        score += q[term] * wt
                #revised: normalization delayed till done here for efficiency
                score = score / (dictOfDoc[d][1] * q["_DENOM"])
                rankscores.setdefault(d, score)
        return rankscores
        #print q
        #print dict_d

#returns dictionary of normalized vector d
def dict_normalize_d_vector(dictionary, docs, docDict, postingsfile):
        docs = docs[0:NUM_CANDIDATE_TO_CONSIDER]
        normalizedInDoc = dict()
        for document in docs:
                querydict_doc = docDict[document]
                count = querydict_doc.values()
                '''
                for i in count:
                        denom = denom + math.pow(i,2)
                        denom = math.sqrt(denom)
                '''
                for term, count in querydict_doc.items():
                        #cosine normalize query term in doc
                        normalizedInDoc.setdefault(document, dict())
                        #normalizedInDoc[document].setdefault(term, (logtf(count) / dictOfDoc[document][1]))
                        normalizedInDoc[document].setdefault(term, logtf(count))
        return normalizedInDoc

#retuns normalized tf-idf vector q              
def normalize_q_vector(dictionary, queryDict):
        #print "normalizing query terms"
        q_tf_idf = dict()
        normalizedInQuery = dict()
        for qterm, count in queryDict.items():
               q_tf_idf.setdefault(qterm, logtf(count) * idf(dictionary, qterm))
               denom = 0
        for i in q_tf_idf.values():
                denom = denom + math.pow(i,2)
                denom = math.sqrt(denom)
                normalizedInQuery.setdefault("_DENOM", denom)
        for term, wt in q_tf_idf.items():
                #normalizedInQuery.setdefault(term, (wt / denom))
                normalizedInQuery.setdefault(term, wt)
        return normalizedInQuery

def evalQuery(querytermlist, dictionary, postingsfile, outputfile):
        #querytermlist is tokenized query terms
        #convert it to a dictionary to enable query term count
        #querytermdict{term: count in query list}
        querytermdict = dict()
        for i in range(0, len(querytermlist)):
                querytermdict.setdefault(querytermlist[i], 0)
                querytermdict[querytermlist[i]] += 1
        #docsWithQuertTerms: { Doc: (dict of query terms : count)}
        docsWithQueryTerms = getDocWithQueryTerms(querytermdict, dictionary, postingsfile)
        if len(docsWithQueryTerms) == 0:
                return list()
        candidateDocs = [ k  for k in sorted(docsWithQueryTerms, key=lambda k: len(docsWithQueryTerms[k]), reverse=True)]
        rankedScore = computeRank(dictionary, candidateDocs, docsWithQueryTerms, querytermdict, postingsfile);
        sortedRanking = list()
        sortedRanking = sorted(rankedScore, key=lambda k: (rankedScore[k], -k), reverse=True)
        sortedRanking = sortedRanking[0:NUM_RESULTS_TO_SHOW]
        #for i in sortedRanking:
        #       print i, rankedScore[i],
        #print "next query"
        return sortedRanking

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
                        #print "reading query"
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
        #print "writing result"
	resultstring = ""
	for item in resultlist:
		resultstring+=(str(item)+" ")
	resultstring = resultstring[0:len(resultstring)-1]
	outputfile.write(resultstring+"\n")
		 				
def usage():
        print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"
	
dictionary_file_d = postings_file_p = queries_file_q = output_file_r = None
try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:k:')
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
        elif o == '-k':
                NUM_CANDIDATE_TO_CONSIDER = eval(a)
        else:
                assert False, "unhandled option"
if dictionary_file_d == None or postings_file_p == None or queries_file_q == None or output_file_r == None:
        usage()
        sys.exit(2)

print "top-k",NUM_CANDIDATE_TO_CONSIDER
termDictionary = loadDictionary(dictionary_file_d)
with open(postings_file_p, "r") as pf:
        dictOfDoc = getDataFromPostings(termDictionary['LIST_OF_DOC'][1], pf)
evaluateQueries(termDictionary, postings_file_p, queries_file_q, output_file_r)

