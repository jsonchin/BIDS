import pandas as pd
import numpy

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
    try:
        return date_str >= curr_date_str
    except:
        return False

def unescape_str(s):
    try:
        return html.unescape(s.replace('&#147;', '"') \
                             .replace('&#148;', '"') \
                             .replace('&#146;', "'") \
                             .replace('\xa0', '') \
                             .replace('’', "'") \
                             .replace('&lt;p&gt;', '') \
                             .replace('&quot;', '"'))
    except:
        return None

def format_grants_gov_data(file_name='temp_data/grants_gov.csv'):
    """
    :param file_name: path to grants gov csv file
    :return: pandas df with columns corresponding to grants_db_columns_names
    """
    df = pd.read_csv(file_name, sep='~', encoding='utf-8')

    def format_date_str(date_str):
        try:
            '08-22-2014'
            return date_str[-4:] + '-' + date_str[:5]
        except:
            return date_str

    df['CloseDate'] = df['CloseDate'].apply(format_date_str)
    curr_date_str = db_utils.get_current_time()[:10]
    df = df[df['CloseDate'].apply(lambda date_str: filter_deadline_passed(date_str, curr_date_str))]

    df['PostDate'] = df['PostDate'].apply(format_date_str)

    df['grants_gov_url'] = df['OpportunityID']\
            .apply(lambda id:'https://www.grants.gov/web/grants/view-opportunity.html?oppId={}'.format(id))

    df['grant_db_insert_date'] = db_utils.get_current_time()

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

    curr_date_str = db_utils.get_current_time()[:10]
    df['Due Date End'][df['Due Date End'] == 'Not listed'] = None

    df = df[df['Due Date End'].apply(lambda date_str: filter_deadline_passed(date_str, curr_date_str))]

    df['AgencyName'] = 'National Science Foundation'
    df['AwardFloor'] = None
    df['AwardCeiling'] = None
    df['grant_db_insert_date'] = db_utils.get_current_time()


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