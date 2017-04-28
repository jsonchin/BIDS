The following requirements are needed (Python3):

```python
Flask==0.12.1
Jinja2==2.9.6
MarkupSafe==1.0
PyMySQL==0.7.11
Werkzeug==0.12.1
beautifulsoup4==4.5.3
bs4==0.0.1
click==6.7
configparser==3.5.0
flup6==1.1.1
html5lib==0.999999999
itsdangerous==0.24
lxml==3.7.3
mysqlclient==1.3.10
nltk==3.2.2
numpy==1.12.1
pandas==0.19.2
python-dateutil==2.6.0
pytz==2017.2
requests==2.13.0
scikit-learn==0.18.1
scipy==0.19.0
six==1.10.0
sklearn==0.0
webencodings==0.5.1
```

while in the first flaskr directory run to install the packages
```
pip install -r requirements.txt
```


To initialize the database (be in /flaskr/flaskr/data_management):

- Download the neccessary files from from https://drive.google.com/drive/u/1/folders/0B7Wc4Mfxs-1GM2Jrd2dhelBjNVU (since they're too big to fit on github) and place it into (/flaskr/flaskr/data_management/temp_data)
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

```
python init_db.py
```

To run the flask app (be in the inner flaskr directory):
```
export FLASK_APP=flaskr.py
flask run
```
