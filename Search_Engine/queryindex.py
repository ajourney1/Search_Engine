import os
import sys
import re as reg
from array import array
from collections import defaultdict
from porterStemmer import PorterStemmer
from CreateIndex import CreateIndex as CI
import copy

'''obj = CI()
lines = obj.findstopwords()
print(obj.stop_words)
'''

portstemmer_obj = PorterStemmer()
prev = CI()

class QueryIndex():
	def __init__(self):
		self.mainindex = {}
		self.fetch_page = {}
	
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
		file = open("indexfile.dat" , "r", encoding = 'UTF-8')
		for eachline in file:
			eachline = eachline.rstrip()
			current_term , indexlist = eachline.split('|')
			indexlist = indexlist.split(';')
			indexlist = [ele.split(':') for ele in indexlist]
			indexlist= [[int(ele[0]), list(map(int, ele[1].split(',')))] for ele in indexlist]
			self.mainindex[current_term] = indexlist
			#print(current_term)
			#print(indexlist)
		#print(self.mainindex)
		file.close()
	
	def whattypeof(self , type):
		if '"' in type:
			return "phase query"
		elif len(type.split()) >= 2:
			return "only text query"
		elif len(type.split()) == 1:
			return "one word query"
		else:
			return "not correctly written."
	
	def return_only_text_query_search(self , query):
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
			print("Here are your search results.")
			unique_id.sort()
			traverse_list = unique_id
			print(traverse_list)
			unique_id = '\n'.join((map(str,unique_id)))
			print(unique_id)
			while True:
				readall = input("Do you want to fetch the whole set of documents\n" + " Y " + " or " + " N " + "\n" )
				if readall == "Y":
					for x in traverse_list:
						y = str(x)
						print(self.fetch_page[y])
					return
				elif readall == "N":
					return
				else:
					print("You entered wrong keyword , search again")
			return
			
		
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
				Idindexlist = [ele[0] for ele in indexlist]
				traverse_list = Idindexlist
				#=print(Idindexlist)
				Idindexlist = '\n'.join((map(str,Idindexlist)))
				print("Here are your search results")
				print(Idindexlist)
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
						print("You entered wrong key , search again")
			
		else:
			self.return_only_text_query_search(query)
			return
	
	
	def return_phase_query_search(self , query):
		optimized_query = prev.get_important_terms(query)
		print(optimized_query)
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
				matches.sort()
				traverse_list = matches
				print("Here are your search results ")
				matches = '\n'.join(list(map(str,matches)))
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
				
	
	
	def queryindex(self):
		self.dofetching()
		prev.findstopwords()
		#print(self.fetch_page['16'])
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
			break
		
	

if __name__=="__main__":
	obj = QueryIndex()
	obj.queryindex()