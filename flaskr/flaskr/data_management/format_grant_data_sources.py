import pandas as pd
import numpy
from datetime import datetime

import database_utilities as db_utils
import database_info as db_info

import html


"""
CREATE TABLE grants (
    grant_title VARCHAR(500),
    grant_description TEXT,
    grant_posted_date VARCHAR(10),
    grant_closing_date VARCHAR(10),
    grant_info_url VARCHAR(80),
    grant_sponsor TEXT,
    grant_award_floor TEXT,
    grant_award_ceiling TEXT,
    grant_db_insert_date VARCHAR(10),
    PRIMARY KEY(grant_title, grant_info_url)
);
"""

def filter_deadline_passed(date_str, curr_date_str):
    """
    Return True if record date_str is older/less than the curr_date_str
        For the case of null date_strs, return False (do not filter it)
    :param date_str:
    :param curr_date_str:
    :return:
    """
    try:
        return date_str >= curr_date_str
    except:
        return False

def unescape_str(s):
    """
    Remove weird characters here. Should find a better way of doing this
        but until then, remove characters one by one
    :param s:
    :return:
    """
    try:
        return html.unescape(s.replace('&#147;', '"') \
                             .replace('&#148;', '"') \
                             .replace('&#146;', "'") \
                             .replace('\xa0', '') \
                             .replace('’', "'") \
                             .replace('&lt;p&gt;', '') \
                             .replace('&quot;', '"') \
                             .replace('™', ''))
    except:
        return None

def format_grants_gov_data(file_name='temp_data/grants_gov.csv'):
    """
    :param file_name: path to grants gov csv file
    :return: pandas df with columns corresponding to grants_db_columns_names
    """
    df = pd.read_csv(file_name, sep='~', encoding='utf-8')

    def format_date_str(date_str):
        """
        '08-22-2014' -> '2014-08-22'
        """
        try:
            return date_str[-4:] + '-' + date_str[:5]
        except:
            return date_str

    df['CloseDate'] = df['CloseDate'].apply(format_date_str)
    curr_date_str = db_utils.get_current_date()
    df = df[df['CloseDate'].apply(lambda date_str: filter_deadline_passed(date_str, curr_date_str))]

    df['PostDate'] = df['PostDate'].apply(format_date_str)

    df['grants_gov_url'] = df['OpportunityID']\
            .apply(lambda id:'https://www.grants.gov/web/grants/view-opportunity.html?oppId={}'.format(id))

    df['grant_db_insert_date'] = curr_date_str

    l_cols = ['OpportunityTitle',
              'Description',
              'PostDate',
              'CloseDate',
              'grants_gov_url',
              'AgencyName',
              'AwardFloor',
              'AwardCeiling',
              'grant_db_insert_date']

    df = df[l_cols]
    df.columns = db_info.grants_db_column_names
    df['grant_title'] = df['grant_title'].apply(unescape_str)
    df['grant_description'] = df['grant_description'].apply(unescape_str)

    df = df.where(pd.notnull(df), None)

    return df

def format_nsf_data(file_name='temp_data/nsf.csv'):
    """
    :param file_name: path to nsf csv file
    :return: pandas df with columns corresponding to grants_db_columns_names
    """
    df = pd.read_csv(file_name, sep='~')

    curr_date_str = db_utils.get_current_date()
    df['Due Date End'][df['Due Date End'] == 'Not listed'] = None

    df = df[df['Due Date End'].apply(lambda date_str: filter_deadline_passed(date_str, curr_date_str))]

    df['AgencyName'] = 'National Science Foundation'
    df['AwardFloor'] = None
    df['AwardCeiling'] = None
    df['grant_db_insert_date'] = curr_date_str


    l_cols = ['Headline',
              'Description',
              'Due Date Start',
              'Due Date End',
              'Link',
              'AgencyName',
              'AwardFloor',
              'AwardCeiling',
              'grant_db_insert_date']

    df = df[l_cols]
    df.columns = db_info.grants_db_column_names
    df['grant_title'] = df['grant_title'].apply(unescape_str)
    df['grant_description'] = df['grant_description'].apply(unescape_str)

    df = df.where(pd.notnull(df), None)

    return df

def format_usda_data(file_name='temp_data/usda.csv'):
    """
    :param file_name: path to usda csv file
    :return: pandas df with columns corresponding to grants_db_columns_names
    """
    df = pd.read_csv(file_name, sep='~')

    curr_date_str = db_utils.get_current_date()
    df['Close Date'][df['Close Date'] == 'Not listed'] = None

    df = df[df['Close Date'].apply(lambda date_str: filter_deadline_passed(date_str, curr_date_str))]

    df['AgencyName'] = 'Department of Agriculture'
    df['grant_db_insert_date'] = curr_date_str

    def format_award_amount(s):
        try:
            return s.replace('$', '').strip()
        except:
            return s

    df['Award Range Floor'] = df['Award Range Floor'].apply(format_award_amount)
    df['Award Range Ceiling'] = df['Award Range Ceiling'].apply(format_award_amount)

    def format_str_date(s):
        """
        :param s: str Sunday, September 30, 2018
        :return: str 2018-09-30
        """
        try:
            return datetime.strptime(s[s.index(',') + 2:], '%B %d, %Y').strftime('%Y-%m-%d')
        except:
            return s

    df['Posted Date'] = df['Posted Date'].apply(format_str_date)
    df['Close Date'] = df['Close Date'].apply(format_str_date)


    l_cols = ['Headline',
              'Description',
              'Posted Date',
              'Close Date',
              'Link',
              'AgencyName',
              'Award Range Floor',
              'Award Range Ceiling',
              'grant_db_insert_date']


    df = df[l_cols]
    df.columns = db_info.grants_db_column_names
    df['grant_title'] = df['grant_title'].apply(unescape_str)
    df['grant_description'] = df['grant_description'].apply(unescape_str)

    df = df.where(pd.notnull(df), None)

    return df