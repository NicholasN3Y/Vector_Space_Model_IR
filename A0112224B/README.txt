This is the README file for A0112224B's submission
contactable at a0112224@u.nus.edu

== General Notes about this assignment ==
To make the dictionary more precise and accurate:
punctuations that appear before or after a term are pruned. 
terms concatenated with '/' are split into seperate terms
special character "&lt;" is ignored.

Indexing is the same as in Homework two, with the addition that the postings list 
indicate the number of times the terms appear in a specific document

The vector model space is implemented using lnc.ltc SMART NOTATION

From the postings list, we get the postings list of the terms that are queried.
Then have a list of candidate documents and get the top-K for which we will compute the ranking score
the program can be run with an additional argument -k [number of documents to consider] 
by default, it is set to be 200.
We then output the top 10 in the rank, whereby docID with same score are output in ascending order. 


== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

index.py
printpost.py - prints out the term dictionary together with postings list
printed.txt - result of printpost.py
ESSAY.txt
search.py
queries.txt
postings.txt
dictionary.txt
README.txt
output.txt - output upon running the program.


== Statement of individual work ==

Please initial one of the following statements.

[X] I, A0112224B, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

I suggest that I should be graded as follows:

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>

To check on the correct syntax and on how to use pickle 
http://www.tutorialspoint.com/python/
