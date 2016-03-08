#!/usr/bin/python
import nltk
import sys
import getopt
import os
import cPickle as pickle
import math

''' Code below is credited to https://msoulier.wordpress.com/2009/08/01/dijkstras-shunting-yard-algorithm-in-python/ '''
class QueryParser(object):
	'''implementation of parser to have infix notation of the query to
		be changed to postfix, uses Dijkstra's Shunting-Yard Algorithm'''
	def __init__(self):
		self.tokens = []
		self.stack = []
		self.postfix = []
	
	def tokenize(self, input):
		self.tokens = input.split(" ")
		tokened = []
		for token in self.tokens:
			r_paren = False
			if token[0] == "(":
				tokened.append("(")
				token = token[1:]
			if len(token) > 0 and token[-1] == ")":
				token = token[:-1]
				r_paren = True
			tokened.append(token)
			if r_paren:
				tokened.append(")")
		self.tokens = tokened
	
	def is_operator(self, token):
		if token == "AND" or token == "OR" or token == "NOT":
			return True
	
	def manage_precedence(self, token):
		if token != 'NOT':
			while len(self.stack) > 0:
				op = self.stack.pop()
				if op == 'NOT':
					self.postfix.append(op)
				else:
					self.stack.append(op)
					break

		self.stack.append(token)

	def right_paren(self):
		found_left = False
		while len(self.stack) > 0:
			top_op = self.stack.pop()
			if top_op != "(":
				self.postfix.append(top_op)
			else:
				found_left = True
				break
		if not found_left:
			raise ParseError, "Parse error: Mismatched parens"

		if len(self.stack) > 0:
			top_op = self.stack.pop()
			if self.is_operator(top_op):
				self.postfix.append(top_op)
			else:
				self.stack.append(top_op)

	def parse(self, input):
		if len(self.tokens) > 0:
			self.__init__()
		#factory = PostfixTokenFactory()
		self.tokenize(input)
		for token in self.tokens:
			if self.is_operator(token):
				self.manage_precedence(token)
			else:
				# Look for parens.
				if token == "(":
					self.stack.append(token)
				elif token == ")":
					self.right_paren()
				else:
                                        if (token != ""):
                                                self.postfix.append(token)
		while len(self.stack) > 0:
			operator = self.stack.pop()
			if operator == "(" or operator == ")":
				raise ParseError, "Parse error: mismatched parens"
			self.postfix.append(operator)
		return self.postfix
		
''' above code credited to https://msoulier.wordpress.com/2009/08/01/dijkstras-shunting-yard-algorithm-in-python/ '''
		
def loadDictionary(filename):
	dictFile = open(filename, 'r')
	term_count_pos = pickle.load(dictFile)
	dictFile.close()
	return term_count_pos

def tidyup(line):
        k = list()
        #print "line is type", type(line)
        stemmer = nltk.PorterStemmer()
        line = nltk.word_tokenize(line)
        for term in line:
                if (term != "NOT" and term != "AND" and term != "OR"):
                        term = stemmer.stem(term.lower())
                k.append(str(term))
        return " ".join(k)

def evaluateQueries(dictionary, posting_filename, queries_filename, output_filename):
	parser = QueryParser()
	outputfile = open(output_filename, 'w')
	postingsfile = open(posting_filename, 'rb')
	with open(queries_filename, 'r') as queries:
		for line in queries:
                        #print "before processed", line
                        k = tidyup(line)
                        #print "after processed",k
			postfix = parser.parse(k)
			#print "postfix", postfix
			try:
                                evalquery(postfix, dictionary, postingsfile, outputfile)
                        except: #catch all exceptions
                                e = sys.exc_info()
                                print "exception thrown", e;
                                write_result(list("Error querying"), outputfile)
	outputfile.close()
	postingsfile.close()
			
def evalquery(query, dictionary, postingsfile, outputfile):
	if (len(query) > 2 ):
		opstack = []
		waitToEvaluate = True
		while len(query) >= 0:
			term = query.pop()
			if term == "NOT":
				opstack.append(term)
			elif term == "OR" or term == "AND":
				waitToEvaluate = True
				opstack.append(term)
			else:
				#is a term 
				if waitToEvaluate:
					waitToEvaluate = False
					opstack.append(term)
				else:
					#print opstack
					list1 = term
					list2 = -1
					Notlist1 = False
					Notlist2 = False
					term = opstack.pop()
					#pop until we get a AND or "OR"
					while (term != "AND" and  term != "OR"):
						if term == "NOT":
							if list2 == -1:
								Notlist1 = True
							else:
								Notlist2 = True
						else:
							list2 = term
						term = opstack.pop()
					
					assert(term=="AND" or term =="OR")
					assert(list1 != -1) 
					assert(list2 != -1)
					if (term == "AND"):
						intermediate_list = evalAnd(list1, Notlist1, list2, Notlist2, dictionary, postingsfile)
					elif(term == "OR"):
						intermediate_list = evalOr(list1, Notlist1, list2, Notlist2, dictionary, postingsfile)
					query.append(intermediate_list)
					while (len(opstack) > 0):
						query.append(opstack.pop())
					assert(len(opstack) == 0)
					return evalquery(query, dictionary, postingsfile, outputfile)
	else:
		if(len(query) == 2):
			assert(query[1] == "NOT")
			res = evalNot(query[0])
		else:
			res = query[0]
			if (type(res) is str):
				res = dictionary.get(res, list())
				res = getDataFromPostings(res[1], postingsfile)
			#print res
		write_result(res, outputfile)
		return 
		
def evalAnd(list1, Notlist1, list2, Notlist2, dictionary, postingsfile):
		#print "evaluating AND clause"
		'''get posting lists'''
		if type(list1) is str:
			list1 = dictionary.get(list1, "None")
			if (list1 == "None"):
			 	list1 = list()
			else:	
				list1 = getDataFromPostings(list1[1], postingsfile)
		if type(list2) is str:
			list2 = dictionary.get(list2, "None")
			if (list2 == "None"):
			 	list2 = list()
			else:	
				list2 = getDataFromPostings(list2[1], postingsfile)
		res_list = list()
		#case Not A and Not B -> Not(A or B)
		if (Notlist1 == True and Notlist2 == True):
			res_list = evalOr(list1, False, list2, False, dictionary, postingsfile)
			return evalNot(res_list)
		#case not A and B
		elif(Notlist1 == True and Notlist2 == False):
			return evalAnd(list2, Notlist2, list1, Notlist1, dictionary, postingsfile)
		
		else:
			if(Notlist1 == False and Notlist2 == False):
				#enforce list1 shorter than list2
				if (len(list1) > len(list2)):
					temp = list1
					list1 = list2
					list2 = temp
					del temp
			ptr_list1 = 0;
			ptr_list2 = 0;
			while ptr_list1 < len(list1) and ptr_list2 < len(list2):
				if (list1[ptr_list1][0] == list2[ptr_list2][0]):
					# case A and B
					if (Notlist2 == False):
						res_list.append(list1[ptr_list1])
					ptr_list1+=1
					ptr_list2+=1
				elif (list1[ptr_list1][0] < list2[ptr_list2][0]):
                                        #has skip pointer
                                        #print "ptr 1", ptr_list1
                                        #print "prt 2", ptr_list2
					if (len(list1[ptr_list1]) == 2):
						init = ptr_list1
						while (list1[list1[ptr_list1][1]] <= list2[ptr_list2]):
							ptr_list1 = list1[ptr_list1][1]
							if (ptr_list1 == len(list1) - 1):
                                                                break
						# case A and not B
						if (ptr_list1 == init):
							ptr_list1 += 1        
                                                if (Notlist2 ==True):
                                                        res_list.extend(list1[init:ptr_list1])
                                                
					else:
						#case A and not B
						if (Notlist2 == True):
							res_list.append(list1[ptr_list1])
						ptr_list1+=1
				elif(list1[ptr_list1][0] > list2[ptr_list2][0]):	
					if (len(list2[ptr_list2]) == 2):
						init = ptr_list2
						while (list2[list2[ptr_list2][1]] <= list1[ptr_list1]):
							ptr_list2 = list2[ptr_list2][1]
							if (ptr_list2 == len(list2)-1):
                                                                break
                                                if (ptr_list2 == init):
							ptr_list2+=1
					else:
						ptr_list2+=1
				#print "list1", list1
				#print "list2", list2
				#print "ptr_list1", ptr_list1
				#print "ptr_list2", ptr_list2
			if(Notlist2 == True and ptr_list1<len(list1)):
				assert(ptr_list2 >= len(list2))
				#A but Not B since B has depleted
				res_list.extend(list1[ptr_list1:len(list1)])
			return skipify(res_list)
					
def evalOr(list1, Notlist1, list2, Notlist2, dictionary, postingsfile):
                #print "evaluating OR clause"
		'''get posting lists'''
		if type(list1) is str:
			list1 = dictionary.get(list1, "None")
			if (list1 == "None"):
			 	list1 = list()
			else:	
				list1 = getDataFromPostings(list1[1], postingsfile)
		if type(list2) is str:
			list2 = dictionary.get(list2, "None")
			if (list2 == "None"):
			 	list2 = list()
			else:	
				list2 = getDataFromPostings(list2[1], postingsfile)
		
		#print list1
		#print list2
		#case A or B
		if (Notlist1 == False and Notlist2 == False):
			if (len(list1) == 0):
				return list2;
			elif (len(list2) == 0):
				return list1
			
			#enforce that list 2 be shorter than list1
			if (len(list1) < len(list2)):
				temp = list1
				list1 = list2
				list2 = temp
				del temp
			
			ptr_list1 = 0
			ptr_list2 = 0
			res_list = list()
			while (ptr_list2 < len(list2) and ptr_list1 < len(list1)): 
				if (list1[ptr_list1][0] == list2[ptr_list2][0]):
					res_list.append(list1[ptr_list1])
					ptr_list1+=1
					ptr_list2+=1
				elif(list1[ptr_list1][0] < list2[ptr_list2][0]):
					if (len(list1[ptr_list1]) == 2):
						init = ptr_list1
						while (list1[list1[ptr_list1][1]] <= list2[ptr_list2]):
							ptr_list1 = list1[ptr_list1][1]
							if (ptr_list1 == len(list1) - 1):
                                                                break;
						if (ptr_list1==init):
							ptr_list1+=1
						res_list.extend(list1[init:ptr_list1])
					else:
						res_list.append(list1[ptr_list1])
						ptr_list1+=1
				elif(list1[ptr_list1][0] > list2[ptr_list2][0]):	
					if (len(list2[ptr_list2]) == 2):
						init = ptr_list2
						while (list2[list2[ptr_list2][1]] <= list1[ptr_list1]):
							ptr_list2 = list2[ptr_list2][1]
                                                        if (ptr_list2 == len(list2) - 1):
                                                                break
						if ptr_list2 == init:
							ptr_list2+=1
						res_list.extend(list2[init:ptr_list2])
					else:
						res_list.append(list2[ptr_list2])
						ptr_list2+=1
			#append remainder to the list
			if (ptr_list1 < len(list1)):
				res_list.extend(list1[ptr_list1:len(list1)])
			elif (ptr_list2 < len(list2)):
				res_list.extend(list2[ptr_list2:len(list2)])
			return skipify(res_list)
			
		#case not A or not B -> not (A and B)
		elif (Notlist1 == True and Notlist2 == True):
			res_list = evalAnd(list1, False, list2, False, dictionary, postingsfile)
			return evalNot(res_list, dictionary, postingsfile)
		
		#case not a or b
		elif (Notlist1 == True and Notlist2 == False):
			list1 = evalNot(list1, dictionary, postingsfile)
			Notlist1 == False
			return evalOr(list1,False, list2, False, dictionary, postingsfile)
			
		#case a or not b  (interchange a and b)
		elif (Notlist1 == False and Notlist2 == True):
			return evalOr(list2, Notlist2, list1, Notlist1, dictionary, postingsfile)		




def evalNot(lists, dictionary, postingsfile):
	doclist = getDataFromPostings(dictionary['LIST_OF_DOC'][1], postingsfile)
	if type(lists) is str:
		lists = dictionary.get(list, "None")
		if (lists == "None"):
			#hence the term is not present in any of the documents, so we take all documents
			return doclist
		else:	
			lists = getDataFromPostings(lists[1], postingsfile)

	#negate list from doclist to get NOT list
	ptr_doclist = 0
	ptr_list = 0
	res_list = list()
	
	while (ptr_list < len(lists)):
		
		if (lists[ptr_list][0] > doclist[ptr_doclist][0]):
			
			#if has skip ptr
			if (len(doclist[ptr_doclist]) == 2):
				init = ptr_doclist
				while (doclist[doclist[ptr_doclist][1]] <= lists[ptr_list]):
					 ptr_doclist = doclist[ptr_doclist][1]
					 if (ptr_doclist == len(doclist) - 1):
                                                 break;
				if ptr_doclist == init:
					ptr_doclist += 1
				res_list.extend(doclist[init:ptr_doclist])
			else:
				res_list.append(doclist[ptr_doclist])
				ptr_doclist+=1

		elif(lists[ptr_list][0] == doclist[ptr_doclist][0]):
			#advance pointers by 1
			ptr_doclist+=1
			ptr_list+=1	
		
		else:
			assert (False), "Should be impossible to enter such state" 		
	
	#append the rest of doclist to the res
	res_list.append(doclist[ptr_doclist:len(doclist)])
	
	return skipify(res_list) 
	
def skipify(alist):
        anlist = list()
	#clear rubbish skip data due to merge 
	for i in range(0, len(alist)-1, 1):
		#assert(type(alist[i]) is tuple), "it is not a tuple!"
		anlist.append((alist[i][0], ))		
	#print anlist		
	post_length = len(anlist)
	val = int(math.floor(math.sqrt(post_length)))	
	#add skip pointer
	if val > 1:
                for i in range (0, post_length, val):
                        if (i + val < post_length):
                                anlist[i] = (anlist[i][0], i+val)
                        elif (i != post_length-1):
                                anlist[i] = (anlist[i][0], post_length - 1)
                                break
        #print anlist        
        return anlist

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

