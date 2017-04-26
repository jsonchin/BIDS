import nltk.stem.wordnet as wordnet
import numpy as np
import string

from .data_management.database import *
from collections import defaultdict
from nltk.corpus import stopwords
from .utility import *
import pickle

sw = set(stopwords.words('english'))
wnl = wordnet.WordNetLemmatizer()
punc_trans = str.maketrans(string.punctuation, " " * len(string.punctuation))
num_trans = str.maketrans('', '', '123456789')


def get_top_k_faculty_tfidf(corpus, k=5):
    desc = corpus
    try:
        desc = desc.lower()
        desc = desc.translate(punc_trans)
        desc = desc.translate(num_trans)
        first = filter(lambda x: x not in sw, desc.split())
        cleaned = [wnl.lemmatize(x) for x in first]
    except:
        cleaned = ["Nothing"]

    cleaned = [' '.join(cleaned)]

    new_grant = grants_vectorizer.transform(cleaned).T

    similarities = np.dot(faculty_grants_matrix, new_grant)
    #max_product = np.max(similarities)
    similarities = similarities.toarray()
    similarities = similarities.reshape(similarities.shape[0], )
    #closest_grants = np.argsort(similarities.toarray(), axis=0)[-5*k:].reshape(5*k, )[::-1]
    closest_grants = np.argsort(similarities)[::-1]

    matches = set()
    faculty_matches = []
    for index in closest_grants:
        faculty = faculty_list[index]
        faculty_name = ' '.join(split_first_last_name(faculty)).lower()
        if faculty in matches:
            #print("Duplicate faculty")
            continue
        dist = similarities[index] # / max_product
        qr = get_faculty_vcr(faculty_name)
        rows = qr.rows
        col_names = qr.column_names
        if len(rows) != 0:
            d = {col: row for row, col in zip(rows[0], col_names)}
            d['dist'] = dist
            faculty_matches.append(d)
            matches.add(faculty)
        if len(faculty_matches) == k:
            break

    return faculty_matches

def get_faculty_vectorizer():
    with open('data_management/temp_data/faculty_vectorizer.pkl', 'rb') as input:
        return pickle.load(input)


def get_grants_vectorizer():
    with open('data_management/temp_data/grants_vectorizer.pkl', 'rb') as input:
        return pickle.load(input)


def create_faculty_grants_matrix(grants_vectorizer):
    faculty_grants = get_faculty_grants().rows
    corpus, faculty_list = [], []
    faculty_grants_set = defaultdict(set)
    for title, faculty in faculty_grants:
        if not title in faculty_grants_set[faculty]:
            corpus.append(title)
            faculty_list.append(faculty)
            faculty_grants_set[faculty].add(title)
    faculty_grants_matrix = grants_vectorizer.transform(corpus)
    return faculty_grants_matrix, faculty_list


def split_first_last_name(s):
    """
    Find highest two 'words', those are the first and last name by order
    """
    l = s.lower().split(' ')
    lengths = [len(w) for w in l]
    max_index = max(range(len(l)), key=lambda i: lengths[i])
    max_word = l[max_index]
    lengths[max_index] = -1

    max_index2 = max(range(len(l)), key=lambda i: lengths[i])
    max_word2 = l[max_index2]

    if max_index < max_index2:
        return max_word, max_word2
    else:
        return max_word2, max_word

faculty_vectorizer = get_faculty_vectorizer()
grants_vectorizer = get_grants_vectorizer()
faculty_grants_matrix, faculty_list = create_faculty_grants_matrix(grants_vectorizer)
