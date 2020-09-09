import os
import sys
import re as reg
import math
from array import array
from collections import defaultdict
from porterStemmer import PorterStemmer
import copy
from CreateIndex import CreateIndex as CI

portstemmer_obj = PorterStemmer()
prev = CI()


class Query():
	def __init__(self):
		self.mainindex = {}
		self.fetch_page = {}
		self.termfrequency = {}
		self.inversedocumentfrequency = {}
		self.titleindex = {}

	def dofetching(self):
		self.collectionfile = open('testcollection.txt','r',encoding='UTF-8')
		document = []
		for line in self.collectionfile:
			if line == '</page>\n':
				currentpage = ''.join(document)
				pageid = reg.search('<id>(.*?)</id>', currentpage , reg.DOTALL)
				pagetitle = reg.search('<title>(.*?)</title>', currentpage, reg.DOTALL)
				pagetext = reg.search('<text>(.*?)</text>' , currentpage , reg.DOTALL)
				pid = pageid.group(1)
				ptitle = pagetitle.group(1)
				ptext = pagetext.group(1)
				total_text = ""
				total_text += ptitle
				total_text += "\n"
				total_text += ptext
				self.fetch_page[pid] = total_text
				document = []
				continue
			else:
				document.append(line)



	def readfromfile(self):
		file = open("indexfiletfidf.dat" , "r", encoding = 'UTF-8')
		self.totaldocuments = int(file.readline().rstrip())
		for eachline in file:
			current_term , indexlist , termfrequency_ , inversedocumentfrequency_ = eachline.split('|')
			indexlist = indexlist.split(';')
			indexlist = [ele.split(':') for ele in indexlist]
			indexlist= [[int(ele[0]), list(map(int, ele[1].split(',')))] for ele in indexlist]
			self.mainindex[current_term] = indexlist
			termfrequency_ = termfrequency_.split(',')
			self.termfrequency[current_term] = list(map(float , termfrequency_))
			self.inversedocumentfrequency[current_term] = float(inversedocumentfrequency_)
			'''print(current_term)
			print(indexlist)
			print(termfrequency_)
			print(inversedocumentfrequency_)'''
		file.close()
		file = open("indexanditstitle.dat" , "r" , encoding = 'UTF-8')
		for eachline in file:
			pageid , pagetitle = eachline.rstrip().split(',',1)
			pageid = int(pageid)
			self.titleindex[pageid] = pagetitle
		file.close()
		#print(self.titleindex)
		#print(self.termfrequency)
		#print(self.inversedocumentfrequency)

	def whattypeof(self , type):
		if '"' in type:
			return "phase query"
		elif len(type.split()) >= 2:
			return "only text query"
		elif len(type.split()) == 1:
			return "one word query"
		else:
			return "not correctly written."

	def dotproduct(self, current_doc_vector , query_vector):
		if len(current_doc_vector)!=len(query_vector):
			return 0
		else:
			return sum([ x*y for x,y in zip(current_doc_vector,query_vector)])

	def dorankingofdocuments(self , Idlist , query):
		documentvector = (defaultdict(lambda: [0]*len(query)))
		queryvector = [0]*len(query)
		collections = list(enumerate(query))
		for index , query_ in collections:
			if query_ not in self.mainindex:
				continue
			else:
				queryvector[index] = self.inversedocumentfrequency[query_]
				newcollection = list(enumerate(self.mainindex[query_]))
				#print(newcollection)
				for newindex , (id , idlist_) in newcollection:
					if id in Idlist:
						x = self.termfrequency[query_][newindex]
						documentvector[id][index] = x
		document_score = [ [self.dotproduct(currentdocument, queryvector) , document_id] for document_id, currentdocument in documentvector.items() ]
		#print(document_score)
		document_score.sort(reverse = True)
		results = [x[1] for x in document_score][:20]
		print("Here are your search results")
		print(results)
		traverse_list = results
		results = [self.titleindex[x] for x in results]
		print(results)
		s = '\n'.join(results)
		print(s)
		while True:
			readall = input("Do you want to fetch the whole document\n" + "Y " + " or " + " N "  + "\n")
			if readall == "Y":
				for x in traverse_list:
					y = str(x)
					print(self.fetch_page[y])
				return
			elif readall == "N":
				return
			else:
				print("You entered wrong keyword , search again")

	def return_one_word_query_search(self , query):
		optimized_query = prev.get_important_terms(query)
		#print(optimized_query)
		num_results_returned = len(optimized_query)
		if num_results_returned == 0:
			print("We couldn't find any document you are searching for! Search again.")
			return
		elif num_results_returned == 1:
			onlyterm = optimized_query[0]
			#print(type(onlyterm))
			if onlyterm not in self.mainindex:
				print("We couldn't find any document you are searching for! Search again.")
				return
			else:
				indexlist = self.mainindex[onlyterm]
				#print(indexlist)
				Idindexlist = [ele[0] for ele in indexlist]
				#print(Idindexlist)
				self.dorankingofdocuments(Idindexlist , optimized_query)
		else:
			self.return_only_text_query_search(query)
			return

	def return_only_text_query_search(self, query):
		optimized_query = prev.get_important_terms(query)
		num_results_returned = len(optimized_query)
		if num_results_returned == 0:
			print("We couldn't find any document you are searching for! Search again.")
			return
		final_id = []
		for eachterm in optimized_query:
			if eachterm in self.mainindex:
				indexlist = self.mainindex[eachterm]
				Idindexlist = [ele[0] for ele in indexlist]
				final_id.append(Idindexlist)
		unique_id = []
		for eachlist in final_id:
			for eachid in eachlist:
				if len(unique_id) == 0:
					unique_id.append(eachid)
				else:
					if eachid not in unique_id:
						unique_id.append(eachid)
					else:
						continue
		num_results_returned = len(unique_id)
		if num_results_returned == 0:
			print("We couldn't find any document you are searching. Search again!")
			return
		else:
			self.dorankingofdocuments(unique_id , optimized_query)


	def return_phase_query_search(self , query):
		optimized_query = prev.get_important_terms(query)
		num_results_returned = len(optimized_query)
		if num_results_returned == 0:
			print("We couldn't find any document you are searching , search again! ")
			return
		elif num_results_returned == 1:
			self.return_one_word_query_search(query)
			return
		else:
			for eachterm in optimized_query:
				if eachterm not in self.mainindex:
					print("There are no any document matching your search , search again! ")
					return
			indexlist = []
			for eachterm in optimized_query:
				indexlist.append(self.mainindex[eachterm])
			#print(indexlist)
			documentid = []
			for idlist in indexlist:
				tempdocid = []
				for ele in idlist:
					tempdocid.append(ele[0])
				documentid.append(tempdocid)
			#print(documentid)
			uniquedocumentid = []
			documentid.sort(key = len)
			if len(documentid) == 1:
				uniquedocumentid = documentid[0]
			elif len(documentid) == 2:
				uniquedocumentid = documentid[0]
				for i in range(1 , len(documentid)):
					temp = documentid[i]
					foo = list(set(uniquedocumentid) & set(temp))
					uniquedocumentid = foo
			#print(uniquedocumentid)
			#print("\n")
			num_results_returned = len(uniquedocumentid)
			if num_results_returned == 0:
				print("There are no any document matching your search , search again")
				return
			temp = []
			for i in range(len(indexlist)):
				indexlist[i] = [ele for ele in indexlist[i] if ele[0] in uniquedocumentid]
			indexlist = copy.deepcopy(indexlist)
			for i in range(len(indexlist)):
				for j in range(len(indexlist[i])):
					indexlist[i][j][1] = [ele-i for ele in indexlist[i][j][1]]
			numofdocuments = len(indexlist[0])
			matches = []
			for i in range(numofdocuments):
				mylist = [ ele[i][1] for ele in indexlist]
				intersection = []
				if len(mylist) == 0:
					continue
				elif len(mylist) == 1:
					intersection = mylist[0]
				else:
					intersection = mylist[0]
					for j in range(1 , len(mylist)):
						temp = mylist[j]
						foo = list(set(intersection) & set(temp))
						intersection = temp
				#print(intersection)
				if len(intersection) == 0:
					continue
				else:
					matches.append(indexlist[0][i][0])
			if len(matches) == 0:
				print("There are no documents matching your search , search again")
			else:
				self.dorankingofdocuments(matches , optimized_query)




	def query(self):
		self.dofetching()
		prev.findstopwords()
		self.readfromfile()
		while True:
			print("Type you query or search !")
			query = sys.stdin.readline()
			if query == '':
				break
			querytype = self.whattypeof(query)
			if querytype == "one word query":
				self.return_one_word_query_search(query)
			elif querytype == "only text query":
				self.return_only_text_query_search(query)
			elif querytype == "phase query":
				self.return_phase_query_search(query)
			else:
				print("We couldn't find any document you are searching for, search again! ")



if __name__=="__main__":
	obj = Query()
	obj.query()
