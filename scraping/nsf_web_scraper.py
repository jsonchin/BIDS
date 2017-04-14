from bs4 import BeautifulSoup
from IPython.display import Image
import dateutil.parser as dparser
import pandas as pd
import re
import time
import urllib.request

nsf_base = 'https://nsf.gov'
nsf_active_grants = 'https://nsf.gov/funding/pgm_list.jsp?sel_org=NSF&status=1&ord=date&org=NSF&page='

curr_page = 1
bad_headers = ["REVISIONS AND UPDATES", "EDUCATIONAL OPPORTUNITY", "RELATED URLS", "RELATED PROGRAMS"]
headlines = []
due_dates_start = []
due_dates_end = []
synopses = []
links = []

while True:
    links_page = urllib.request.urlopen(nsf_active_grants + str(curr_page))
    links_soup = BeautifulSoup(links_page, "html5lib")
    all_links = links_soup.find_all("a", class_="atemphover")
    print(curr_page)
    if all_links:
        for alink in all_links:
            try:
                error_code = 0
                full_link = nsf_base + alink.get("href")
                if full_link in links:
                    pass
                grant_url = urllib.request.urlopen(full_link)
                grant_soup = BeautifulSoup(grant_url, "html5lib") 

                # Headline
                temp = grant_soup.find("span", class_="pageheadsubline")
                headline = temp.find_next_sibling("h2").text.partition("\n")[0]
                headlines.append(headline)
                error_code = 1

                # Date
                try:
                    temp = grant_soup.find("strong", text=re.compile("Full Proposal")).parent.text
                    temp_split = temp.split()
                    if "Window" in temp_split:
                        start_end = " ".join(temp_split).split("-")
                        start = dparser.parse(start_end[0], fuzzy=True).strftime('%Y-%m-%d')
                        end = dparser.parse(start_end[1], fuzzy=True).strftime('%Y-%m-%d')
                        due_dates_start.append(start)
                        due_dates_end.append(end)
                    else:
                        due_date = dparser.parse(temp, fuzzy=True).strftime('%Y-%m-%d')
                        due_dates_start.append("None")
                        due_dates_end.append(due_date)
                except:
                    try:
                        temp = grant_soup.find("strong", text=re.compile("DUE DATES"))
                        date = temp.parent.next_sibling.next_sibling.next_sibling.strip()
                        if not date:
                            raise ValueError("Date empty")
                        due_dates_start.append("None")
                        due_dates_end.append(due_date)
                    except:
                        #print("Not listed")
                        #print(full_link)
                        due_dates_start.append("Not listed")
                        due_dates_end.append("Not listed")
                        
                # Synopsis
                error_code = 2
                temp = grant_soup.find("strong", text=re.compile("SYNOPSIS"))
                synopsis = temp.parent.find_next_sibling('p').text
                for header in bad_headers:
                    if header in synopsis:
                        synopsis = temp.next_sibling.next_sibling.next_sibling.strip()
                synopses.append(synopsis)
                
                links.append(full_link)
                time.sleep(0.01)
            except:
                if error_code == 0:
                    print("Error code: 0")
                    print(nsf_base + alink.get("href"))
                elif error_code == 1:
                    print("Error code: 1")
                    print(nsf_base + alink.get("href"))
                    headlines.pop()
                elif error_code == 2:
                    print("Error code: 2")
                    print(nsf_base + alink.get("href"))
                    headlines.pop()
                    due_dates.pop()
    else:
        break
    curr_page += 1

df = pd.DataFrame()

df['Headline'] = headlines
df['Due Date Start'] = due_dates_start
df['Due Date End'] = due_dates_end
df['Description'] = synopses
df['Link'] = links

df.to_csv("nsf_grants.csv", sep="~", index=False)
