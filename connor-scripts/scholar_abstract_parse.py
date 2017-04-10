# import scholar
from subprocess import Popen, PIPE
import sys
import os
import re
import urllib2
from bs4 import BeautifulSoup
import pdfminer
import slate
import string

"""
example use from command line:
$ python scholar_abstract_parse.py.py "Pieter Abbeel"

to use outside command line, call get_bag_of_words

"""

academic_paper_sections = set(["Abstract", "Introduction", "Intro", "Background", "History", \
	"Review-of-Literature", "Methodology", "Results", "Argument", "Critique", "Discussion", \
	"Conclusion", "Works Cited", "References","Materials and Methods", "Materials", "Methods"])
first_words = set(['Versions', 'URL', 'Title', 'Excerpt', 'Cluster', 'Citations', 'Year', 'PDF'])

def extract_urls(string):
	return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)

def get_bag_of_words(author):
	"""
	ARG1 - string - name of author
	RET - List of strings found in abstracts, introductions, and snippets of either
	""" 

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
					if extracted_abstract:
						number += 1
						got_abstract = True
		elif not got_abstract and first_word == "Excerpt":
			extracted_abstract = line.split()[1:] #don't want to include the word "Excerpt"
		if extracted_abstract:
			# remove punctuation and numbers, and append words from new abstract to list
			extracted_abstract = [word.translate(None, string.punctuation) for word in extracted_abstract if not word.isdigit()]
			wordlist += extracted_abstract
	print wordlist
	return " ".join(wordlist)

def download_file(download_url, number):
    #http://stackoverflow.com/a/24845366
    response = urllib2.urlopen(download_url)
    filename = author + str(number) + ".pdf"
    file = open(filename, 'w')
    file.write(response.read())
    file.close()
    print("Completed" + filename)
    return filename

def extract_abstract_from_url(url, number, delete_file = True):
	"""
	Downloads pdf, extracts words from abstract or intro, deletes pdf
	ARG1 - string - url of pdf to try to download
	ARG2 - number which is part of the name of the file, in case we wan't to keep the file
	RET - list of words, or None
	"""
	filename = download_file(url, number)
	with open(filename) as f:
  		doc= slate.PDF(f)
  		for page in doc:
  			if "Abstract" in page:
  				words_in_page = page.split()
  				words_to_return = keep_only_one_section(words_in_page, "Abstract")
  				if delete_file:
  					os.remove(filename)
 				return words_to_return
 			elif "Introduction" in page:
 				words_to_return = page.split()
 				words_to_return = keep_only_one_section(words_in_page, "Introduction")
 				if delete_file:
  					os.remove(filename)
 				return words_to_return

	print("No Abstract found in filename: " + str(filename))
	return None

def keep_only_one_section(wordlist, desired_section = "Abstract"):
	start_idx = wordlist.index(desired_section)
	for idx in range(start_idx, len(wordlist)):
		word = wordlist[idx]
		if word in academic_paper_sections and word != desired_section:
			return wordlist[start_idx + 1: idx]
	return wordlist
	


if __name__ == "__main__":
	author = sys.argv[1]
	get_bag_of_words(author)