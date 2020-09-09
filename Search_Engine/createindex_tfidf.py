import os
import sys
import re as reg
import math
from array import array
from collections import defaultdict
from porterStemmer import PorterStemmer
import copy

#Creating object of PorterStemmer Class
portstemmer_obj = PorterStemmer()
class CreateIndex:
	def __init__(self):
		self.mainindex = defaultdict(list)
		self.termfrequency = defaultdict(list)
		self.documentfrequency = defaultdict(int)
		self.totaldocuments = 0
		self.indexanditstitle = defaultdict(list)

	def findstopwords(self):
		stopwordsfile = open('stopwords.txt','r',encoding='UTF-8')
		stopwords=[line.rstrip() for line in stopwordsfile]
		self.stop_words = dict.fromkeys(stopwords)
		stopwordsfile.close()

	def get_important_terms(self , lines):
		#get the useful words and terms from the text
		lines = lines.lower()
		lines = reg.sub(r'[^a-z0-9 ]' , ' ' , lines)
		lines = lines.split()
		lines = [ele for ele in lines if ele not in self.stop_words]
		lines = [portstemmer_obj.stem(letter , 0 , len(letter) - 1) for letter in lines]
		return lines


	def writetofile(self):
		file = open('indexfiletfidf.dat','w',encoding='UTF-8')
		file.write(str(self.totaldocuments) + "\n")
		x = float(self.totaldocuments)
		for eachterm in self.mainindex.keys():
			indexlist = []
			for details in self.mainindex[eachterm]:
				documentid = details[0]
				positions = details[1]
				indexlist.append(':'.join([str(documentid) ,','.join(map(str,positions))]))
			res = ';'.join(indexlist)
			termfrequency_ = ','.join(map(str, self.termfrequency[eachterm]))
			y = float(self.documentfrequency[eachterm])
			inverted_doc_freq = '%.5f' % (x/y)
			s = '|'.join((eachterm , res , termfrequency_ , inverted_doc_freq))
			file.write(s + "\n")
		file.close()
		file = open('indexanditstitle.dat' , 'w' , encoding = 'UTF-8')
		for pageid , pagetitle in self.indexanditstitle.items():
			file.write(pageid + "," + pagetitle + "\n")
		file.close()

	def createindex(self):
		self.collectionfile = open('testcollection.txt','r',encoding='UTF-8')
		self.findstopwords()
		pagedictionary = {}
		document = []
		megadocument = []
		for line in self.collectionfile:
			if line == '</page>\n':
				#print(document)
				currentpage = ''.join(document)
				megadocument.append(currentpage)
				document = []
				continue
			else:
				document.append(line)
		count = -1
		size = int(len(megadocument))
		while True:
			count = count + 1
			if count == size:
				break
			print(count)
			currentpage = megadocument[count]
			pageid = reg.search('<id>(.*?)</id>', currentpage , reg.DOTALL)
			pagetitle = reg.search('<title>(.*?)</title>', currentpage, reg.DOTALL)
			pagetext = reg.search('<text>(.*?)</text>' , currentpage , reg.DOTALL)
			if pageid == None or pagetext == None or pagetitle == None or pageid.group(1) == None or pagetext.group(1) == None or pagetitle.group(1) == None:
				break
			dictionary = {}
			dictionary['id'] = pageid.group(1)
			dictionary['title'] = pagetitle.group(1)
			dictionary['text'] = pagetext.group(1)
			pagedictionary = dictionary
			lines = '\n'.join((pagedictionary['title'] , pagedictionary['text']))
			pageid = int(pagedictionary['id'])
			terms = self.get_important_terms(lines)
			self.totaldocuments = self.totaldocuments + 1
			self.indexanditstitle[pagedictionary['id']] = pagedictionary['title']
			termdictionarypage = {}
			collections = enumerate(terms)
			for current_position , current_term in collections:
				try:
					termdictionarypage[current_term][1].append(current_position)
				except:
					termdictionarypage[current_term] = [pageid, array('q' , [current_position])]
			donormalization = 0
			#print(termdictionarypage)
			for current_term , indexlist in termdictionarypage.items():
				toadd = len(indexlist[1]) ** 2
				donormalization = donormalization + toadd
			donormalization = math.sqrt(donormalization)
			#print(donormalization)
			for current_term , indexlist in termdictionarypage.items():
				x = float(len(indexlist[1]))
				y = float(donormalization)
				self.termfrequency[current_term].append('%.5f' % (x / y))
				self.documentfrequency[current_term] = self.documentfrequency[current_term] + 1
			for current_term , current_positions in termdictionarypage.items():
				self.mainindex[current_term].append(current_positions)
			#print(self.termfrequency)
			#print(self.mainindex)
			if count == 1:
				break
		self.writetofile()

if __name__=="__main__":
	obj = CreateIndex()
	obj.createindex()






