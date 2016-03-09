import sys
import os
import cPickle as pickle

postingsfile = open("postings.txt", "r");

def loadDictionary(filename):
	dictFile = open(filename, 'r')
	term_count_pos = pickle.load(dictFile)
	dictFile.close()
	return term_count_pos

def getDataFromPostings(position):
	postingsfile.seek(position, 0)
	return pickle.load(postingsfile)
    
def printPosting(dictionary):
    for term, postings in sorted(dictionary.items()):
        postinglist = getDataFromPostings(postings[1]);
        print term, postings, postinglist , "\n"


termDictionary = loadDictionary("dictionary.txt")
printPosting(termDictionary)
