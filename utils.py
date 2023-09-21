# libraries
import json
import os, os.path
import pandas as pd
import numpy as np
import sklearn.preprocessing as pp
import scipy.sparse as sparse
from meta_learner import Knn


# Individual Recommendation utility functions
def get_purchased(cust_ind, data, items):
    purchased_ind = data[cust_ind, :].nonzero()[1]
    purchased_list = []
    for i in purchased_ind:
        purchased_list.append(items[i])

    return purchased_list


def top_N_KNN(user, users_d, data, n, knn, items):
    if user in users_d:
        user_ind = users_d[user]

        pred, score = knn.recommend(user_ind, return_scores=True)
        # items_purchased = get_purchased(user_ind, data, items)
        # ensemble_products = set(items_purchased)
        ensemble_products = []

        for miss in range(0, len(items)):
            if not (miss in pred):
                pred = np.append(pred, miss)

        rec_list = []
        i = 0
        for k, ind in enumerate(pred):
            if i >= n:
                break
            else:
                item_id = items[ind]
                if item_id in ensemble_products:
                    continue
                else:
                    rec_list.append(item_id)
                    i = i + 1

        return rec_list


# Apply KNN recommender system to user, data and extract m items
def get_recommendations(users, users_d, data, m, knn, items):
    support_dict = {}
    for u in users:
        values = top_N_KNN(u, users_d, data, m, knn, items)
        support_dict[u] = values
    return support_dict


# Get users, items, sparse ratings matrix
def preprocessing(data_train):
    items = list(np.sort(data_train.ARTICLE_ID.unique()))  # all unique items
    users = list(np.sort(data_train.CUST_ID.unique()))  # all unique user
    rating = list(np.sort(data_train.FREQUENCY))
    # Get the associated row indices
    rows = data_train.CUST_ID.astype(pd.api.types.CategoricalDtype(categories=users)).cat.codes
    # Get the associated row indices
    cols = data_train.ARTICLE_ID.astype(pd.api.types.CategoricalDtype(categories=items)).cat.codes
    index_list = list(rows.values)
    items_2 = list(data_train.CUST_ID)
    users_d = dict()

    # preprocessing similarity matrix
    j = 0
    for i in items_2:
        if i not in users_d:
            users_d[i] = index_list[j]
        j = j + 1

    data = sparse.csr_matrix((rating, (rows, cols)), shape=(len(users), len(items)))
    return items, users, users_d, data


# Train new KNN recommender
def train_recommender(data):
    similarity_matrix = pp.normalize(data.tocsc(), axis=0)
    similarity_matrix = similarity_matrix.T * similarity_matrix

    knn = Knn.KNN(data)
    knn.fit(similarity_matrix, selectTopK=True, topK=10)
    return knn


# Safely open file folder
def safe_open_w(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, 'w')


# Save to an external file
def write_to_file(input_f, path):
    with safe_open_w(path) as write_file:
        json.dump(input_f, write_file)


# Convert seconds in format h:min:sec
def convert(sec):
    sec = sec % (24 * 3600)
    hour = sec // 3600
    sec %= 3600
    minutes = sec // 60
    sec %= 60
    return "%d:%02d:%02d" % (hour, minutes, sec)


def intersection(lst1, lst2):
    lst3 = [values for values in lst1 if values in lst2]
    return lst3

