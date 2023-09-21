import copy
import random


def user_sorting(loss, hist_loss, users, weights, sorting_option):
    sort = {}
    sorted_users = {}

    if sorting_option == 'loss':
        for user in users:
            sort[user] = (weights[user][0] * loss[user][0]) + (weights[user][1] * loss[user][1])
        sorted_users = sorted(sort, key=sort.get, reverse=True)

    if sorting_option == 'historical':
        for user in users:
            sort[user] = loss[user][0] + loss[user][1]
            sort[user] += hist_loss[user]
        sorted_users = sorted(sort, key=sort.get, reverse=True)

    # random.seed(0)
    if sorting_option == 'random':
        sorted_users = users.copy()
        random.shuffle(sorted_users)

    return sorted_users
