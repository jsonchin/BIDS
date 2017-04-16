import urllib
import urllib.request
import os, csv
import json
from bs4 import BeautifulSoup
import pandas as pd
from IPython.display import Image
from IPython.display import HTML

def call-scraper():

	root = "https://nifa.usda.gov/"
	root_raw = urllib.request.urlopen(root).read()
	root_raw = root_raw.decode('UTF-8')

	search_0 = "https://nifa.usda.gov/page/search-grant?keywords=&fo=&cfda=&program=&status=All&page=0"
	search = "https://nifa.usda.gov/page/search-grant?keywords=&fo=&cfda=&program=&status=All&page="
	search_0_raw = urllib.request.urlopen(search_0)
	search_0_soup = BeautifulSoup(search_0_raw, "html5lib")

	headlines = []
	descriptions = []
	due_dates_start = []
	due_dates_end = []
	award_ranges = []
	grant_award_floors = []
	grant_award_ceilings = []
	percentages = []
	links = []
	limit = 1000
	current = 0
	page_limit = 25

	while page_limit:

    	search_raw = urllib.request.urlopen(search + str(current))
    	search_soup = BeautifulSoup(search_raw, "html5lib")
    	page = search_soup.find_all(lambda tag: tag.name == 'td')
    	page = [link.find('a') for link in page]
    	page = [link for link in page if link != None]
    
    	for alink in page:
        	try:
            	error_code = 0
            	full_link = root + alink.get("href")
            	links.append(full_link)

            	grant_url = urllib.request.urlopen(full_link)
            	grant_soup = BeautifulSoup(grant_url, "lxml") 
            	headline = grant_soup.find("h1", class_="node__title").text.partition("\n")[0]
            
            	headlines.append(headline)
            	due_date = grant_soup.find_all("span", class_="date-display-single")
            	due_date_start = due_date[0].text.partition("\n")[0]
            	due_date_end = due_date[1].text.partition("\n")[0]
            	
            	due_dates_start.append(due_date_start)
            	due_dates_end.append(due_date_end)
            	possible_award_range = grant_soup.find_all("div", class_="field field--spaced field--aligned")
            
            	percentage = "N/A"
            	if possible_award_range[-3].text.partition("\n")[0][0] == 'P' and possible_award_range[-3].text.partition("\n")[0][1] == 'e':
                	percentage = possible_award_range[-3].text.partition("\n")[0][31:]
            	percentages.append(percentage)
    
            	grant_award_floor = "N/A"
            	grant_award_ceiling = "N/A"
            	award_range = "N/A"
            	if possible_award_range[-1].text.partition("\n")[0][0] == 'R' and possible_award_range[-1].text.partition("\n")[0][1] == 'a':
                	award_range = possible_award_range[-1].text.partition("\n")[0][17:]
                	grant_award_floor, grant_award_ceiling = award_range.split("-")
            
            	grant_award_floors.append(grant_award_floor)
            	grant_award_ceilings.append(grant_award_ceiling)
            	award_ranges.append(award_range)
            
            	error_code = 1           
            	all_possible_description = grant_soup.find_all("p")
            	description = all_possible_description[-1].string
            	descriptions.append(description)
            
        	except:
            	if error_code == 0:
                	print("Error code: 0")
                	print(root + alink.get("href"))
            	elif error_code == 1:
                	print("Error code: 1")
                	print(root + alink.get("href"))
                	descriptions.append("No description for this grants available currently.")

    	current += 1
    	page_limit -= 1

    df = pd.DataFrame()
	df['Headline'] = headlines
	df['Description'] = descriptions
	df['Posted Date'] = due_dates_start
	df['Close Date'] = due_dates_end
	df['Percent of Applications Funded'] = percentages
	df['Award Range Floor'] = grant_award_floors
	df['Award Range Ceiling'] = grant_award_ceilings
	df['Link'] = links

	return df
