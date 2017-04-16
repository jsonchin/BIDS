from .database import remove_outdated_grants
from .scrape_data import scrape_all
from .init_db import init_db

# maybe should have these tasks within here instead of separate files
def run_daily_tasks():
    # need to clean database of out of date grants every day
    remove_outdated_grants()
    # scraping daily load of data
    scrape_all()
    # insert scraped data into database without dropping the table (insert on duplicate update)
    init_db()


