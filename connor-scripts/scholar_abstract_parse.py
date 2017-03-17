# import scholar
from subprocess import Popen, PIPE
import sys
import os
import re
import urllib2
from bs4 import BeautifulSoup
import pdfminer
import slate

"""
example use from command line:
$ python scholar_abstract_parse.py.py "Pieter Abbeel"

"""

first_words = set(['Versions', 'URL', 'Title', 'Excerpt', 'Cluster', 'Citations', 'Year', 'PDF'])

def extract_urls(string):
	return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)

def this_main(author):
	# call scholar.py script and pipe output into file
	query_string = 'python scholar.py --author ' + author
	p = Popen(['python', 'scholar.py', '--author', author], stdout=PIPE, stderr=PIPE, stdin=PIPE)
	script_output = p.stdout.read()
	# split up output of scholar.py into lines and read line by line
	lines = script_output.split("\n")
	number = 0
	downloads_tried = set()
	wordlist = []
	for line in lines:
		#identify first word of the line to figure out what the line contains
		words = line.split(" ")
		words = [word for word in words if word != ""]
		first_word = words[0] if words else ""

		#when we see "Title", we know we've gotten to a new entry
		if first_word == "Title":
			# reset search
			extracted_abstract = ""
			got_abstract = False

		"""
		We prefer to take abstract in full from link/file
		But if there is not link/file, use excerpt
		Thankfully, opportunities for the file always come before excerpt
		Only use excerpt if we haven't already extracted from link/file
		"""
		urls = extract_urls(line)
		if urls:
			for url in urls:
				
				if url.count(":") > 1:
					p = re.compile('https://+')
					multiple_urls = ["http://" + word for word in p.split(url) if word and "scholar.google.com" not in word]
				else:
					multiple_urls = [url]
				
				for url in multiple_urls:
					if ".pdf" in url and url not in downloads_tried:
						print("downloading " + url)
						downloads_tried.add(url)
						try:
							extracted_abstract = extract_abstract_from_url(url, number)
							got_abstract = True
						except Exception as e:
							print("got error: " + str(e) + " downloading from " + url)
					else:
						# print(url + " isn't a pdf")
						extract_from_webpage(url)
					if extracted_abstract:
						number += 1
						got_abstract = True
		elif not got_abstract and first_word == "Excerpt":
			extracted_abstract = line.split()
		if extracted_abstract:
			wordlist += extracted_abstract
	print wordlist
	return wordlist

def download_file(download_url, number):
    #http://stackoverflow.com/a/24845366
    response = urllib2.urlopen(download_url)
    filename = author + str(number) + ".pdf"
    file = open(filename, 'w')
    file.write(response.read())
    file.close()
    print("Completed" + filename)
    return filename

def extract_abstract_from_url(url, number):
	filename = download_file(url, number)
	with open(filename) as f:
  		doc= slate.PDF(f)
  		for page in doc:
  			if "Abstract" in page:
  				words_to_return = page.split()
 				return words_to_return
 			elif "Introduction" in page or "Intro" in page:
 				words_to_return = page.split()
 				return words_to_return
	print("No Abstract found in filename: " + str(filename))
	return None
	# parse pdf


def extract_from_webpage(url):
	pass
# 	# http://stackoverflow.com/a/13087415
# 	response = urllib2.urlopen(url)
# 	response_string = str(response.read())
# 	soup = BeautifulSoup(response_string)
# 	page = soup.find_all('div')
# 	for thing in page:
# 		print(thing, type(thing))
# 	print(page)


	
	return ""
if __name__ == "__main__":
	author = sys.argv[1]
	this_main(author)