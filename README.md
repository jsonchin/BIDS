To run the flask app (be in the inner flaskr directory):

- export FLASK_APP=flaskr.py
- run flask


To initialize the database (be in /flask/flaskr/flaskr/data_management):

- Download grants_gov.csv from https://drive.google.com/drive/u/1/folders/0B7Wc4Mfxs-1GM2Jrd2dhelBjNVU (since it's too big to fit on github) and place it into (/flask/flaskr/flask/data_management/temp_data)
- Either change your local mysql access to user: root, password: pw or change the code in init_db.py and database.py
- python init_db.py
