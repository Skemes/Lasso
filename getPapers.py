import scholar
import nltk
import string
import pattern.en
import numpy as np

START_YEAR_DATE = 2010
MAX_NUM_PAGES = 15
NOUNS = ['NN', 'NP', 'NNS', 'JJ']
MAX_EXTRA_KWs = 10


def splitUnicodeData(charList, char):
	myS = ""
	for charElem in charList: myS += charElem
	try:
		myS = str(myS)
		return string.split(myS, char)
	except UnicodeEncodeError:
		return -1	

def getNounListFromScholar(catList, interestList):
	mySearcher = scholar.ScholarQuerier()

	interestString = ",".join(interestList)
	
	numKWs = MAX_EXTRA_KWs
	nounList = []
	wordDict = {}
	

	for phrase in catList:
		titleList = []

		#First, get titles
		myQuery = scholar.SearchScholarQuery()
		myQuery.set_num_page_results(MAX_NUM_PAGES)
		myQuery.set_phrase(phrase)
		myQuery.set_timeframe(start=START_YEAR_DATE)
		myQuery.set_include_patents(False)
		mySearcher.send_query(myQuery)
		articles = mySearcher.articles
		for article in articles:
			data = article.as_txt()
			data = splitUnicodeData(data, '\n')
			if(data != -1): #No encoding errors
				titleInformation = string.strip(data[0])
				if 'Title' in titleInformation:
					title = string.replace(titleInformation, 'Title', '')
					titleList.append(title)

		mySearcher.clear_articles()

		#Now, Let's label each of these by word type, gather the nouns in nounList
		for title in titleList:
			title = string.lower(title)
			text = nltk.tokenize.word_tokenize(title)
			wordLabelsList = nltk.pos_tag(text)
			for wordType in wordLabelsList:
				word, tag = wordType
				if tag in NOUNS:
					if tag == 'NNS': word = pattern.en.singularize(word)
					if word in wordDict: wordDict[word] +=1
					else: wordDict[word] = 1


	#Get the subset of words >= mean of the distribution
	#(it's going to be exponential undoubtedly, so the ones greater
	#are going to be fairly rare to somewhat represented
	wordCounts = np.array(wordDict.values())
	avg = np.mean(wordCounts)

	for k, v in wordDict.iteritems():
		if(v <= avg): nounList.append(k)

	print nounList


	#Now that we have our keywords, let's take these and use them in a custom Google Scholar Search
	myKWSearch = scholar.SearchScholarQuery()
	myKWSearch.set_words(interestList)
	myKWSearch.set_words_some(" ".join(nounList[:numKWs-1]))
	myKWSearch.include_citations = False
	myKWSearch.set_timeframe(start=START_YEAR_DATE)
	myKWSearch.set_num_page_results(MAX_NUM_PAGES)
	myKWSearch.set_timeframe(start=START_YEAR_DATE)

	mySearcher.send_query(myKWSearch)

	#Gather the results, grabbing title and authors
	titleClusters = {} #Organization: cluster: title pairs
	
	articles = mySearcher.articles
	for article in articles:
		title = ""
		clusterID = ""
		data = article.as_txt()
		data = splitUnicodeData(data, '\n')
		if(data != -1): #No encoding errors
			titleInformation = string.strip(data[0])
			if 'Title' in titleInformation:
				title = string.replace(titleInformation, 'Title', '')
				clusterInfo = string.strip(data[5]) #only get cluster info if we can get a title
				cluster = string.split(clusterInfo)[-1]
				if cluster in titleClusters: titleClusters[cluster] += [title]
				else: titleClusters[cluster] = [title]

	
	print titleClusters
	return 0
			
		
	

def main():
#1) Find nouns associated with Category of interest
	getNounListFromScholar(["Neural Network"], ["bacteria"])

	return 0

	

if __name__ == "__main__":
    main()
