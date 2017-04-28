import requests
from bs4 import BeautifulSoup
from lxml import etree
import zipfile
import os
import io

import datetime
import pytz

import pandas as pd

import dateutil.parser as dparser
import re
import time
import urllib.request
import urllib


def scrape_grants_gov():
    # http://www.grants.gov/help/html/help/index.htm#t=XML_Extract%2FXML_Extract.htm
    # http://www.grants.gov/web/grants/xml-extract.html

    #download the xml file
    date = str(datetime.datetime.now(pytz.timezone('US/Pacific')))[:10].replace('-', '') #20170328

    xhr_request_url = 'https://www.grants.gov/web/grants/xml-extract.html?p_p_id=xmlextract_WAR_grantsxmlextractportlet_INSTANCE_5NxW0PeTnSUa&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_cacheability=cacheLevelPage&p_p_col_id=column-1&p_p_col_pos=1&p_p_col_count=2&download=GrantsDBExtract{}v2.zip'.format(date)

    r = requests.get(xhr_request_url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    f = z.open(z.namelist()[0])

    root = etree.parse(f)
    COMMON_PREFIX = '{http://apply.grants.gov/system/OpportunityDetail-V1.0}'
    grant_trees = root.findall('{http://apply.grants.gov/system/OpportunityDetail-V1.0}OpportunitySynopsisDetail_1_0')
    rows = []
    headers = [ele.tag[len(COMMON_PREFIX):] for ele in grant_trees[0]]

    multiple_cols = set()

    for grant in grant_trees:
        d = {}
        for ele in grant:
            tag = ele.tag[len(COMMON_PREFIX):]
            if tag not in headers:
                headers.append(tag)

            if tag not in d:
                d[tag] = [ele.text]
            else:
                d[tag].append(ele.text)

        row = []
        for header in headers:
            if header not in d:
                row.append(None)
            else:
                if len(d[header]) > 1:
                    multiple_cols.add(header)
                row.append(','.join(d[header]))
        rows.append(row)

    df = pd.DataFrame(rows, columns=headers)
    df.to_csv('temp_data/grants_gov.csv', sep='~', index=False)



def scrape_nsf():
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
                        due_dates_start.pop()
                        due_dates_end.pop()
        else:
            break
        curr_page += 1

    df = pd.DataFrame()

    df['Headline'] = headlines
    df['Due Date Start'] = due_dates_start
    df['Due Date End'] = due_dates_end
    df['Description'] = synopses
    df['Link'] = links

    df.to_csv("temp_data/nsf.csv", sep="~", index=False)


def scrape_usda():
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
                if possible_award_range[-3].text.partition("\n")[0][0] == 'P' and \
                                possible_award_range[-3].text.partition("\n")[0][1] == 'e':
                    percentage = possible_award_range[-3].text.partition("\n")[0][31:]
                percentages.append(percentage)

                grant_award_floor = "N/A"
                grant_award_ceiling = "N/A"
                award_range = "N/A"
                if possible_award_range[-1].text.partition("\n")[0][0] == 'R' and \
                                possible_award_range[-1].text.partition("\n")[0][1] == 'a':
                    award_range = possible_award_range[-1].text.partition("\n")[0][17:]
                    grant_award_floor, grant_award_ceiling = award_range.split("-")

                grant_award_floors.append(grant_award_floor)
                grant_award_ceilings.append(grant_award_ceiling)
                award_ranges.append(award_range)

                error_code = 1
                all_possible_description = grant_soup.find_all("p")
                raw_description = all_possible_description[-1]
                description = all_possible_description[-1].text
                if raw_description.text == "":
                    description = grant_soup.find("html") \
                        .find("body").find("main").find("div", class_="layout-page clearfix") \
                        .find("div", class_="layout-constrain").find("div", class_="layout-listing__row clearfix") \
                        .find("div", class_="layout-page__main clearfix").find("article").text
                    updated_description = ""
                    for i in description:
                        if i != '.':
                            updated_description += str(i)
                        else:
                            updated_description += str(i)
                            break
                    description = updated_description
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

    df.to_csv("temp_data/usda.csv", sep="~", index=False)

def scrape_all():
    scrape_grants_gov()
    scrape_nsf()
    scrape_usda()


if __name__ == '__main__':
    scrape_all()





# def grants_gov_xml_to_csv():
#     # read the xml file and parse it
#     f = open('temp_data/grants_gov.xml', 'r')
#     root = etree.parse(f)
#     COMMON_PREFIX = '{http://apply.grants.gov/system/OpportunityDetail-V1.0}'
#     grant_trees = root.findall('{http://apply.grants.gov/system/OpportunityDetail-V1.0}OpportunitySynopsisDetail_1_0')
#     rows = []
#     headers = [ele.tag[len(COMMON_PREFIX):] for ele in grant_trees[0]]
#
#     multiple_cols = set()
#
#     for grant in grant_trees:
#         d = {}
#         for ele in grant:
#             tag = ele.tag[len(COMMON_PREFIX):]
#             if tag not in headers:
#                 headers.append(tag)
#
#             if tag not in d:
#                 d[tag] = [ele.text]
#             else:
#                 d[tag].append(ele.text)
#
#         row = []
#         for header in headers:
#             if header not in d:
#                 row.append(None)
#             else:
#                 if len(d[header]) > 1:
#                     multiple_cols.add(header)
#                 row.append(','.join(d[header]))
#         rows.append(row)
#         # print(row)
#         # if len(rows) > 5:
#         #     return
#
#     df = pd.DataFrame(rows, columns=headers)
#
#     for col in ('PostDate', 'CloseDate', 'LastUpdatedDate', 'ArchiveDate'):
#         df[col] = df[col].apply(format_date)
#
#     df.to_csv('temp_data/grants_gov.csv', sep='~', index=False)