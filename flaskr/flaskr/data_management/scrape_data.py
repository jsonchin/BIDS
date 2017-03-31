import requests
from bs4 import BeautifulSoup
from lxml import etree
import zipfile
import os
import io

import datetime
import pytz

import pandas as pd


def scrape_grants_gov():


    # ## Parse grants.gov xml to csv delimited by ~

    # http://www.grants.gov/help/html/help/index.htm#t=XML_Extract%2FXML_Extract.htm
    #
    # http://www.grants.gov/web/grants/xml-extract.html


    #download the xml file and store it
    date = str(datetime.datetime.now(pytz.timezone('US/Pacific')))[:10].replace('-', '') #20170328

    xhr_request_url = 'https://www.grants.gov/web/grants/xml-extract.html?p_p_id=xmlextract_WAR_grantsxmlextractportlet_INSTANCE_5NxW0PeTnSUa&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_cacheability=cacheLevelPage&p_p_col_id=column-1&p_p_col_pos=1&p_p_col_count=2&download=GrantsDBExtract{}v2.zip'.format(date)

    r = requests.get(xhr_request_url)

    # with open('temp_data/grants_gov.zip', 'w') as f:
    #     f.write(r.text)

    # z = zipfile.ZipFile('temp_data/grants_gov.zip')
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

    return



    grants_gov_xml_to_csv()

def grants_gov_xml_to_csv():
    # read the xml file and parse it
    f = open('temp_data/grants_gov.xml', 'rb')
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



def scrape_all():
    scrape_grants_gov()


if __name__ == '__main__':
    scrape_all()