from collections import defaultdict
import math
import numpy as np
import scipy.io 
import sklearn

"""
Implements a naive content-based recommender.
Uses feature matrix from featurize.py (research_data.mat).
Data taken from research_grant_history_10_years.csv.
"""

research_data = scipy.io.loadmat("research_data")
feature_matrix = research_data["feature_matrix"]
pi_labels = research_data["pi_labels"]
title_labels = research_data["title_labels"]

# Hack shuffling
pi_dict = {}
for i in range(len(pi_labels)): 
    pi = pi_labels[i]
    feature_vector = feature_matrix[i]
    if pi not in pi_dict:
        pi_dict[pi] = []
        pi_dict[pi_labels[i]].append(feature_vector)
    else:
        pi_dict[pi].append(feature_vector)

for pi in pi_dict:
    np.random.shuffle(pi_dict[pi])

training_pi_labels = []
training_title_labels = []
training_feature_matrix = []
validation_pi_labels = []
validation_title_labels = []
validation_feature_matrix = []

# Create training and validation sets. Validation set is 1/3 of total.
for pi in pi_dict:
    validation_amt = math.ceil(len(pi_dict[pi]) / 3)
    for i in range(len(pi_dict[pi])):
        feature_vector = pi_dict[pi][i]
        if validation_amt > 0: 
            validation_pi_labels.append(pi)
            validation_feature_matrix.append(feature_vector)
            validation_amt -= 1
        else:
            training_pi_labels.append(pi)
            training_feature_matrix.append(feature_vector)

print("Training set size:", len(training_pi_labels))
print("Validation set size:", len(validation_pi_labels))

# Debugging: why is the data separated for 5 faculty?
#x = defaultdict(int)
#for i in range(1, len(pi_labels)):
#    if pi_labels[i - 1] != pi_labels[i] and pi_labels[i] in x:
#        print(i)
#        print(pi_labels[i])
#    else:
#        x[pi_labels[i]] += 1

#debug = open('debug.txt', 'w')
#for i in range(len(pi_labels)):
#    debug.write(pi_labels[i])
#    debug.write("\n")
#debug.close()


# Old hack to get exactly one piece of validation data per pi
"""
curr_pi = pi_labels[0]
for i in range(1, len(pi_labels)):
    pi = pi_labels[i]
    title = title_labels[i - 1]
    feature_vector = feature_matrix[i - 1]
    if curr_pi != pi:
        validation_pi_labels.append(curr_pi)
        validation_title_labels.append(title)
        validation_feature_matrix.append(feature_vector)
    else:
        training_pi_labels.append(curr_pi)
        training_title_labels.append(title)
        training_feature_matrix.append(feature_vector)
    curr_pi = pi

validation_feature_matrix.append(feature_matrix[-1])
validation_pi_labels.append(pi_labels[-1])
validation_title_labels.append(title_labels[-1])
"""

# Create faculty profiles
faculty_profiles = {}
for i in range(len(training_pi_labels)):
    faculty = training_pi_labels[i]
    research_profile = training_feature_matrix[i]
    if faculty in faculty_profiles:
        # A pretty bad way to update faculty profile
        # Maybe try normalizing
        faculty_profiles[faculty] += research_profile
    else:
        faculty_profiles[faculty] = research_profile

def test_recommendation(similarity_func, recommend_func):
    results = []
    for i in range(len(validation_pi_labels)):
        faculty = validation_pi_labels[i]
        research_profile = validation_feature_matrix[i]
        faculty_profile = faculty_profiles[faculty]
        similar_val = similarity_func(research_profile, faculty_profile)
        results.append(recommend_func(similar_val))
    return results

def five_threshold(val):
    if val > 4:
        return 1
    else:
        return 0

results = test_recommendation(np.dot, five_threshold)
print("Correct:", sum(results))
print("Total:", len(results))
print("Validation Error: ", 1 - (sum(results) / len(results)))

# Count amount of researchers with > (i + 1) grants
#for i in range(1, 10):
#    counter = defaultdict(int)
#    for pi in training_pi_labels:
#        counter[pi] += 1
#
#    count = 0
#    for x in counter:
#        if counter[x] == i:
#            count += 1
#    print(i, count)
