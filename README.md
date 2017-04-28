## Berkeley Institute for Data Science: Data Science for Social Good Spring 2017 Project

Our team has developed a webapp for the Berkeley Research Development Office to use to automatically and effectively match research grants with Berkeley researchers and faculty.

### Data

Each research grant is a description of the grant which varies in length and specificity across grants.

Here's the type of research grant data we're dealing with:

The first two sentences of the description of [Innovations in Biological Imaging and Visualization](https://nsf.gov/funding/pgm_summ.jsp?pims_id=503473&org=NSF&sel_org=NSF&from=fund)
> The IBIV activity supports the development of novel approaches to the analysis of biological research images through the innovative "Ideas Lab" project development and review process. The analysis and visual representation of complex biological images present daunting challenges across all scales of investigation, from multispectral analysis of foliage or algal bloom patterns in satellite images, to automated specimen classification, and tomographic reconstructions in structural biology. 

Each faculty member has a bag of words we've scraped from VCResearch or from their personal webpages. Sometimes faculty members don't put a lot for their description or don't update their webpages.

Here's [John Denero](https://www2.eecs.berkeley.edu/Faculty/Homepages/denero.html)'s bag of words from his personal webpage
```python
['teaching', 'artificial', 'intelligence', 'education', 'educ', 'centers', 'artificial', 'intelligence', 'bair', 'teaching', 'schedule', 'foundations', 'data', 'science', 'mowefr', 'pimentel', 'completion', 'computer', 'science', 'decal', 'anova', 'teaching', 'computer', 'science', 'youth', 'soda', 'foundations', 'data', 'science', 'mowefr', 'completion', 'computer', 'science', 'eecs', 'natural', 'language', 'processing', 'tasks', 'related', 'statistical', 'machine', 'translation', 'cross-lingual', 'alignment', 'translation', 'model', 'estimation', 'translation', 'inference', 'lexicon', 'acquisition', 'unsupervised', 'grammar', 'induction', 'prior', 'spent', 'four', 'scientist', 'google', 'primarily', 'google', 'translate', 'serves', 'billion', 'translation', 'requests', 'refereed', 'naacl', 'acl', 'emnlp', 'conferences', 'author', 'composing', 'textbook', 'programming', 'computer', 'science', 'masters', 'philosophy', 'eecs']
```

Each faculty member also has a list of research grant titles that they were awarded (if any).


### Methodology

We used two methods to match research grants to faculty and faculty to research grants.

The first is using TFIDF (Term Frequency Inverse Doc Frequency) and past research grant awards.


The second is using [GloVe (Global Vectors for Word Representations)](https://nlp.stanford.edu/projects/glove/) without using past research grant awards. To match a faculty member to his or her k best research grants, we take their bag of words, convert each word to its GloVe representation (100 dimensional), then average the vectors. We do the same for each grant for their grant descriptions after cleaning and filtering them (removing stop words, punctuation, etc). Then we run K-nearest neighbors to find the k best research grants for the faculty member. This also works the same way for matching a research grant to the k-best faculty members. One benefit of this is the meaning or connotation of the faculty's interests and the grant's subject areas are captured. Similar words in GloVe have similar geometrical structure, that is, words such as "HIV" and "AIDS" have very similar vectors since they show up in very similar contexts. This means if the word "HIV" shows up a lot in a grant description but "AIDS" never does and if the word "AIDS" shows up in a faculty profile but "HIV" never does then the grant would still be most likely paired with that faculty member.

Using this, John Denero's first research grant match is with [Computational and Data-Enabled Science and Engineering in Mathematical and Statistical Sciences](https://www.grants.gov/web/grants/view-opportunity.html?oppId=289329). As an EECS professor that doesn't do research and that has been heavily involved in developing and growing the Data Science program here at Berkeley (developing and teaching DATA8), this is not an unreasonable grant matching. However, some more educational based research grants seem to be more appropriate from our perspective since he seems really really enthusiastic about CS education and helping his students succeed.


### Data Sources

We've used the ``requests`` python library and ``beautifulsoup`` to help gather the data.

For grants:
- [grants.gov](grants.gov)
- [nsf](nsf.gov)
- [usda](usda.gov)

For faculty members:
- [Berkeley VCResearch](vcresearch.berkeley.edu)
- Berkeley department personal faculty webpages
- Google Scholars
- Past research grant awards to faculty members


## Installation

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
