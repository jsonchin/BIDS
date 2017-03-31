import pandas as pd

import database_utilities as db_utils
import database_info as db_info


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

    df = df.where(pd.notnull(df), None)

    # df = df.drop_duplicates(['OpportunityTitle'])

    return df