import random
from random import sample
import numpy.random as rd


def create_synthetic_data(n_items, n_users, max_items):
    random.seed(0)
    user_array = []
    for i in range(n_users):
        new_user = "u" + str(i)
        user_array.append(new_user)

    item_array = []
    items_id = sample(range(1, max_items), n_items)
    for item in items_id:
        new_item = "#" + str(item)
        item_array.append(new_item)
    return item_array, user_array


def synthetic_price(items):
    rd.seed(0)
    price_list = rd.random_sample(size=(len(items))) / 10
    prices = dict(zip(items, price_list))
    return prices


def synthetic_recs(items, users):
    keys = users
    value = items
    recommendations = {key: list(value) for key in keys}
    return recommendations


def synthetic_utility(recommendations, items, users):
    utility_matrix_u = {}
    for user in users:
        u_recommendations = recommendations[user]
        item_score = {}

        for item in u_recommendations:
            score = (len(u_recommendations) - u_recommendations.index(item)) / len(u_recommendations)
            item_score[item] = score

        utility_matrix_u[user] = item_score

    utility_matrix_i = {}
    for i in items:
        user_score = {}
        for u in users:
            user_score[u] = utility_matrix_u[u][i]
        utility_matrix_i[i] = user_score

    return utility_matrix_i


def synthetic_recs_pl(utility_u, users):
    keys = users
    new_utility = {}
    for u in users:
        utility_ordered = dict(sorted(utility_u[u].items(), key=lambda item: item[1], reverse=True))
        # print(u, utility_ordered)
        new_utility[u] = utility_ordered
    recommendations = {key: list(new_utility[key]) for key in keys}
    return recommendations


def synthetic_utility_pl(items, users):
    random.seed(0)
    utility_matrix_u = {}
    percent = len(items) // 6
    print("Popular items: ", percent)
    popular_items = items[0:percent]
    semi_popular_items = items[percent:percent*2]
    unpopular_items = items[percent*2:]
    for user in users:
        # u_recommendations = items
        item_score = {}
        for item in popular_items:
            score = round(random.uniform(0.8, 1), 5)
            item_score[item] = score
        for item in semi_popular_items:
            score = round(random.uniform(0.6, 0.8), 5)  # 0.6, 0.8 standard
            item_score[item] = score
        for item in unpopular_items:
            score = round(random.uniform(0, 0.8), 5)  # 0, 0.8 standard
            item_score[item] = score

        utility_matrix_u[user] = item_score

    utility_matrix_i = {}
    for i in items:
        user_score = {}
        for u in users:
            user_score[u] = utility_matrix_u[u][i]
        utility_matrix_i[i] = user_score

    # print(popular_items)
    # for i in popular_items:
    #     print(i, utility_matrix_i[i])
    # for i in unpopular_items:
    #     print(i, utility_matrix_i[i])

    return utility_matrix_i, utility_matrix_u
