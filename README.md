To run the flask app (be in the inner flaskr directory):

- export FLASK_APP=flaskr.py
- flask run


To initialize the database (be in /flask/flaskr/flaskr/data_management):

- Download the neccessary files from from https://drive.google.com/drive/u/1/folders/0B7Wc4Mfxs-1GM2Jrd2dhelBjNVU (since they're too big to fit on github) and place it into (/flask/flaskr/flask/data_management/temp_data)
- The following files are needed to initialize database:
    - faculty_vcr.csv
    - complete_cleaned_faculty_webpages.csv
    - grants_gov.csv
    - research_grant_history.csv
    - bids_data.csv
    - nsf.csv
    - usda.csv
    - glove.json
- Either change your local mysql access to user: root, password: pw or change the code in init_db.py and database.py
- python init_db.py
