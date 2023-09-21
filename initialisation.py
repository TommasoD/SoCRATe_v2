import numpy as np
import numpy.random as rd
import random


# initialise utility_matrix
def random_utility_initialise(items, users):
    support_matrix = rd.random_sample(size=(len(items), len(users)))
    dictionary_list = []
    for i in range(len(items)):
        dictionary_list.append(dict(zip(users, support_matrix[i])))

    utility_matrix = dict(zip(items, dictionary_list))
    return utility_matrix


def utility_initialise(users, users_d, knn, items):
    utility_matrix = {}
    print('Utility computation...')
    for u in users:
        if u in users_d:
            user_ind = users_d[u]

            pred, score = knn.recommend(user_ind, return_scores=True)

            for miss in range(0, len(items)):
                if not (miss in pred):
                    pred = np.append(pred, miss)

            # normalise scores
            s_min = min(score)
            s_max = max(score)
            if s_min != s_max:
                for s in range(len(score)):
                    score[s] = (score[s] - s_min) / (s_max - s_min)

            item_score = {}

            for j in range(len(pred)):
                item_score[items[pred[j]]] = score[pred[j]]

            utility_matrix[u] = item_score
            # swap user-item

    utility_matrix_items = {}
    print('Utility matrix swapping...')
    for i in items:
        user_score = {}
        for u in users:
            user_score[u] = utility_matrix[u][i]
        utility_matrix_items[i] = user_score

    return utility_matrix_items


# initialise availabilities
def initialise_availability(availabilities, budget):
    for key in availabilities.keys():
        availabilities[key] = budget


# initialise availabilities according to normal distribution
def normal_initialise_availability(availabilities, mean_availability):
    random.seed(0)
    for key in availabilities.keys():
        availabilities[key] = int(random.gauss(mean_availability, 0.1 * mean_availability))


# TO DO initialise in a more realistic way:
def item_initialise(user_size, items, high_budget=False):
    items_budget = []

    if high_budget:
        minimum = user_size // 2 - 10
        maximum = user_size // 2 + 10
        for i in range(len(items)):
            items_budget.append(rd.randint(minimum, maximum, size=1))
        return items_budget

    # get the distribution
    samples_b = rd.lognormal(0, 0.4, 10000)
    new_samples_log_b = []
    for i in samples_b:
        # new_samples_log_b.append(round((i - samples_b.min()) / (samples_b.max()) * user_size*5) + 1)
        new_samples_log_b.append(round((i - samples_b.min()) / (samples_b.max()) * user_size) + 1)

    # use log-normal for budget
    for i in range(len(items)):
        items_budget.append(rd.choice(new_samples_log_b, size=1).item())
    return items_budget


def change_utility(utility, popularity, n):
    sorted_popularity = dict(sorted(popularity.items(), key=lambda item: item[1], reverse=True))
    popular_items = list(sorted_popularity.keys())
    for i in range(n):
        key = popular_items[i]
        for user in utility[key]:
            utility[key][user] = 1.0
    return utility
