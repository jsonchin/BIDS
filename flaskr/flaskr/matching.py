import pandas as pd
import numpy as np
import json

import nltk
from nltk.corpus import stopwords
import string
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from .data_management.database import *

UNDEFINED_GLOVE_VEC = np.ones(100) * 10000

def text_to_bag(text):
    """
    Given a string, cleans (removes punctuation, white spaces, stop words, common dirty words)
        and splits the sentence into a bag of words
    :param text: string
    :return: list
    """
    try:
        text = text.lower()
        pattern = '[\r\t\n]'
        repl = ''
        text = re.sub(pattern, repl, text)

        pattern = '[=/\.~_\"“…*]'
        repl = ' '
        text = re.sub(pattern, repl, text)

        tokens = nltk.word_tokenize(text)

        names = set()
        faculty_names = [l[0] for l in get_faculty_names().rows]

        for names_l in map(lambda s: s.lower().split(' '), faculty_names):
            for name in names_l:
                names.add(name)
        stopwords = set(nltk.corpus.stopwords.words('english') + list(string.punctuation))
        common_dirty_words = set([
            'center-col',
            'id',
            'content',
            'img',
            'section',
            'page',
            'info', 'home',
            'top', 'directory', 'icon', 'envelope', 'click', 'reach', 'share', 'button',
            'navigation', 'www', 'com', 'html', 'link', 'http', 'edu', 'berkeley', 'website', 'webpage', 'https',
            'false', 'name',
            'email', 'phone', 'room', 'download', 'pdf', 'california', 'welcome',
            'university',  # remove this word or not?
            'printer-friendly', 'linkedin', 'profile', 'contact', 'address', 'biography',
            'alphabetical',  # maybe bad for linguistics
            'publications', 'selected', 'whatshot', 'place',
            'associate', 'assistant', 'researcher', 'research', 'area', 'professor', 'adjunct', 'lab', 'labs',
            'director', 'senior', 'summa', 'cum', 'laude', 'students', 'class', 'staff', 'emeritus', 'degree',
            'lecturer', 'executive', 'leadership', 'visiting', 'ext', 'status', 'duty', 'distinguished',
            'board', 'advisory', 'directors', 'graduating', 'majors', 'affiliate', 'member',
            'also', 'figure', 'group', 'study', 'interest', 'interests', 'interested', 'areas', 'expertise', 'pursuing',
                                                                                                             'name',
            'office', 'hours', 'tuesday', 'monday', 'wednesday', 'thursday', 'friday',
            'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',
            'november', 'december',
            'etcheverry', 'dwinelle', 'tan', 'latimer',
            'might', 'please', 'faculty', 'like',
            'duke', 'colombia', 'oxford', 'diego', 'yale', 'stanford', 'harvard', 'polytechnic', 'rensselaer',
            'kennedy', 'boston', 'michigan', 'purdue', 'colgate', 'northwestern',
            'curriculue', 'vitae', 'undergraduate', 'graduate',
            'found', 'working', 'held',
            'thought', 'main', 'e-mail', 'personal', 'appointment', 'press', 'cambridge',
            'became', 'prof', 'dot', 'provide', 'coming', 'soon', 'holds', 'hold', 'work', 'works',
            'links', 'kth', 'phd', 'include', 'homepage', 'curriculum', 'format', 'acrobat', 'reader', 'required',
            'editor', 'listing', 'department', 'born', 'cory',
            'courses', 'semester', 'course', 'title', 'syllabus', 'spring', 'fall', 'college',
            'academic', 'publishers', 'springer', 'authored', 'co-authored', 'review', 'papers', 'paper', 'published',
            'editorial', 'committee', 'selection', 'editors', 'editor', 'vol', 'journal',
            'dept', 'currently', 'using', 'focus', 'focuses', 'focused',
            'studying', 'ask', 'behind', 'going', 'still', 'really', 'another',
            'campus', 'online', 'location', 'vcresearch', 'major', 'universities', 'provided', 'operated',
            'tan', 'fax', 'recent', 'novel', 'current', 'search', 'based', 'method', 'methods',
            'technique',
            'various', 'used', 'use',
            'awards', 'prize', 'scholarship', 'scholarships', 'winner', 'recipient', 'honor', 'honors',
            'new', 'changed', 'get', 'example',
            'began', 'following', 'first', 'year', 'second', 'starting', 'served', 'award', 'introductory',
            'received', 'attended', 'joined', 'could', 'enable', 'many', 'involved', 'question', 'questions',
            'problem', 'problems', 'updates', 'center', 'give', 'written', 'extensively', 'along',
            'unique', 'gives', 'different', 'believe', 'shown', 'across', 'able', 'show', 'much', 'available',
            'towards', 'provides', 'loading', 'alloed', 'propose', 'proposed', 'similar', 'instance',
            'multiple', 'primary', 'secondary', 'identify', 'well', 'visit', 'complete', 'list', 'providing',
            'either', 'including', 'effects', 'effect', 'years', 'context', 'site', 'highly', 'would', 'better', 'ways',
            'via', 'xml', 'richards', 'opportunities', 'become', 'epub', 'underlying', 'given', 'span',
            'contribution', 'often', 'uses', 'importance', 'responsible', 'insights', "'kdb", 'edit',

        ])

        grants_common_words = set([
            'continue', 'funding', 'opportunity', 'announcement', 'purpose', 'foa', 'advancing', 'particularly', 'defining', 'observed', 'understanding', 'leading', 'priority', 'high', 'medium', 'achieve', 'program', 'seeks', 'submit', 'programs', 'knowledge', 'substantive', 'collaboration', 'scholars', 'fellowship', 'fellow', 'applicants', 'recognized', 'considerable', 'detailed', 'proposal', 'evaluated', 'applicant', 'qualified', 'members', 'encouraged', 'groups', 'apply', 'applied', 'grants', 'grant', 'awarded', 'award', 'organizations', 'proposing', 'engage', 'position', 'members', 'member', 'mission', 'missions', 'statement', 'goal', 'anticipated', 'bureau', 'necessary', 'notice', 'participants', 'participant', 'acquired', 'individuals', 'populations', 'consequences', 'population', 'student', 'earn', 'two', 'one', 'three', 'individual', 'eligible', 'approved', 'must', 'topic', 'significant', 'least', 'most', 'fellows', 'aims', 'methodology', 'applicability',
        ])


        common_dirty_words = common_dirty_words | names | grants_common_words

        l = []
        for token in tokens:
            if token in stopwords or token in common_dirty_words:
                continue
            if len(token) <= 2:
                continue
            contains_num = False
            for i in range(0, 10):
                if str(i) in token:
                    contains_num = True
                    break
            if contains_num:
                continue

            l.append(token)
        return l
    except Exception as e:
        print(e)
        return []

def bag_to_vec(sentence):
    """
    Given a list of words (sentence), return a vector that averages the glove vectors of each word in the sentence
    :param sentence: list
    :return: numpy array of dimension 100
    """
    vec = 0
    try:
        for word in sentence:
            try:
                if word in glove_d:
                    vec += glove_d[word]
            except:
                pass
        if type(vec) == int:
            return UNDEFINED_GLOVE_VEC  # should never be chosen
        else:
            return vec / len(sentence)
    except:
        return UNDEFINED_GLOVE_VEC

def initialize_glove():
    glove_d = {}
    with open('data_management/temp_data/glove.json', 'r') as f:
        json_d = json.load(f)
        for word in json_d:
            glove_d[word] = np.array(json_d[word])
    return glove_d

def initialize_faculty():
    qr = get_faculty_webpages()
    col_names = qr.column_names
    rows = np.array(qr.rows)

    df_faculty = pd.DataFrame(data=rows, columns=col_names)

    def split_sentence(s):
        try:
            return s.split(' ')
        except:
            return s

    df_faculty['glove_vec'] = df_faculty['faculty_webpage_content'].apply(split_sentence).apply(bag_to_vec)

    df_faculty['faculty_webpage_content'][~df_faculty['faculty_webpage_content'].notnull()] = ''

    return df_faculty

def initialize_tfidf_vectorizer():
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_vectorizer.fit(df_faculty['faculty_webpage_content'])
    return tfidf_vectorizer

def sentences_to_vec(sentences):
    vecs = []
    vocab_index_map = tfidf_vectorizer.vocabulary_
    tfidf = tfidf_vectorizer.transform(sentences).todense()
    for i in range(len(sentences)):
        sentence = sentences[i]
        words = sentence.split(' ')
        vec = 0
        count = 0
        for word in set(words):
            try:
                vec += glove_d[word] * tfidf[i, vocab_index_map[word]]
                count += 1
            except Exception as e:
                pass
        if type(vec) == int:
            vecs.append(np.zeros(100)) #np.nan
        else:
            vecs.append(vec)
    return vecs

def initialize_grants():
    qr = get_all_grants()
    col_names = qr.column_names
    rows = np.array(qr.rows)

    df_grants = pd.DataFrame(data=rows, columns=col_names)

    df_grants['glove_vec'] = df_grants['grant_description'].apply(text_to_bag).apply(bag_to_vec)
    return df_grants

def initialize_faculty_vecs():
    df_faculty['glove_vec'] = sentences_to_vec(df_faculty['faculty_webpage_content'].values)

def initialize_grant_vecs():
    df_grants['glove_vec'] = sentences_to_vec(
            df_grants['grant_description'].apply(text_to_bag).apply(lambda s:' '.join(s)))





# should make this more general
# given a cleaned bag of words (could be faculty or grant), return the closest k faculty

# do the same for grants
# given a cleaned bag of words (could be faculty or grant), return the closest k grants
def get_k_closest_faculty(corpus, k=5):
    """
    Given a corpus and how many faculty to match with,
        returns a list of information about the faculty

    Utilizes GloVE embeddings, takes average of glove vectors of sentences for both the corpus and the faculty,
    then uses kNearestNeighbors to find the top k faculty matches

    :param grant_d: dictionary with keys: (grant_title - str, grant_description - str)
    :param k: integer
    :return: list of dictionaries (keys are vcr columns)
    """
    corpus_bag = text_to_bag(corpus)

    corpus_vec = bag_to_vec(corpus_bag)


    knn = NearestNeighbors(n_neighbors=k, n_jobs=-1)
    knn.fit(df_faculty['glove_vec'][~df_faculty['glove_vec'].isnull()].values.tolist())

    dists, indicies = knn.kneighbors(corpus_vec)
    indicies = indicies[0]
    dists = dists[0]

    faculty_matches = [df_faculty['faculty_name'].iloc[i] for i in indicies]
    faculty_matches_info = []

    for i in range(len(faculty_matches)):
        faculty_name = faculty_matches[i]
        dist = dists[i]
        faculty_vcr_qr = get_faculty_vcr(faculty_name)
        d = {col:row for row, col in zip(faculty_vcr_qr.rows[0], faculty_vcr_qr.column_names)}
        d['dist'] = dist
        faculty_matches_info.append(d)


    return faculty_matches_info

def get_k_closest_grants(corpus, k=5):
    """
    Given a corpus and how many grants to match with,
        returns a list of information about the grants

    Utilizes GloVE embeddings, takes average of glove vectors of sentences for both the corpus and the grants,
    then uses kNearestNeighbors to find the top k grant matches

    :param grant_d: dictionary with keys: (grant_title - str, grant_description - str)
    :param k: integer
    :return: list of dictionaries (keys are vcr columns)
    """
    corpus_bag = text_to_bag(corpus)

    print(corpus_bag)

    corpus_vec = bag_to_vec(corpus_bag)

    knn = NearestNeighbors(n_neighbors=k, n_jobs=-1)
    knn.fit(df_grants['glove_vec'][~df_grants['glove_vec'].isnull()].values.tolist())

    dists, indicies = knn.kneighbors(corpus_vec)
    indicies = indicies[0]
    dists = dists[0]

    grant_matches = [df_grants.iloc[i] for i in indicies]
    grant_matches_info = []

    for i in range(len(grant_matches)):
        row = grant_matches[i]
        grant_info_d = {col: row_val for col, row_val in zip(df_grants.columns.values, row.values)}
        grant_info_d['dist'] = dists[i]
        grant_matches_info.append(grant_info_d)

    return grant_matches_info


glove_d = initialize_glove()
df_faculty = initialize_faculty()
# tfidf_vectorizer = initialize_tfidf_vectorizer()
df_grants = initialize_grants()
# initialize_faculty_vecs()
# initialize_grant_vecs()