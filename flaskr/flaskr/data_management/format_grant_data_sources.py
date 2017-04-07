import pandas as pd
import numpy

import database_utilities as db_utils
import database_info as db_info

import html


"""
grant_title TEXT,
grant_description TEXT,
grant_posted_date DATE,
grant_closing_date DATE,
grant_info_url TEXT,
grant_sponsor TEXT,
grant_award_floor TEXT,
grant_award_ceiling TEXT,
grant_db_insert_date DATE,
PRIMARY KEY(grant_title, grant_posted_date)
"""

"""
should get all columns except for the grant_db_insert_date
"""

def format_grants_gov_data(file_name='temp_data/grants_gov.csv'):
    """
    :param file_name: path to grants gov csv files
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

    def filter_deadline_passed(date_str):
        try:
            return date_str >= curr_date_str
        except:
            return False

    df = df[df['CloseDate'].apply(filter_deadline_passed)]

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

    def unescape_str(s):
        try:
            return html.unescape(s.replace('&#147;', '"')\
                                    .replace('&#148;', '"')\
                                    .replace('&#146;', "'"))
        except:
            return None

    df['OpportunityTitle'] = df['OpportunityTitle'].apply(unescape_str)
    df['Description'] = df['Description'].apply(unescape_str)

    df = df[l_cols]

    df.columns = db_info.grants_db_column_names

    df = df.where(pd.notnull(df), None)

    # df = df.drop_duplicates(['OpportunityTitle'])

    return df