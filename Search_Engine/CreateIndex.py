import os
import sys
import re as reg
from array import array
from collections import defaultdict
from porterStemmer import PorterStemmer

#Creating object of PorterStemmer Class
portstemmer_obj = PorterStemmer()

class CreateIndex():
	#Default contructor
	def __init__(self):
		self.mainindex=defaultdict(list)
		self.fetch_page = {}
	
	#Get all the stopwords
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
		file = open('indexfile.dat','w',encoding='UTF-8')
		for eachterm in self.mainindex.keys():
			indexlist = []
			for details in self.mainindex[eachterm]:
				documentid = details[0]
				positions = details[1]
				indexlist.append(':'.join([str(documentid) ,','.join(map(str,positions))]))
			s = (''.join((eachterm,'|',';'.join(indexlist))))
			file.write(s+"\n")
		file.close()
	
	def createindex(self):
		self.collectionfile = open('testcollection.txt','r',encoding='UTF-8')
		self.findstopwords()
		'''foo = input()
		ziz = self.get_important_terms(foo)
		print(ziz)'''
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
		#print(self.fetch_page['16'])
		count = -1
		size = int(len(megadocument))
		while True:
			count = count + 1
			print(count)
			if count == size:
				break
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
			termdictionarypage = {}
			collections = enumerate(terms)
			for current_position , current_term in collections:
				try:
					termdictionarypage[current_term][1].append(current_position)
				except:
					termdictionarypage[current_term] = [pageid, array('q' , [current_position])]
			#print(termdictionarypage)
			for current_term , indexlist in termdictionarypage.items():
				self.mainindex[current_term].append(indexlist)
			#print(self.mainindex)
			#if count == 1:
				#break
		print("success! :)")
		self.writetofile()

if __name__=="__main__":
	obj = CreateIndex()
	obj.createindex()