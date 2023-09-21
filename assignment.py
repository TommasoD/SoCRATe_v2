import copy


def preference_based_strategy(opt_r, availability, users, n):  # user-centric
    user_preferences = copy.deepcopy(opt_r)
    keys = users
    value = []
    r = {key: list(value) for key in keys}

    for user in users:
        for rec in range(n):
            current_item = user_preferences[user].pop(0)
            while availability[current_item] == 0:
                current_item = user_preferences[user].pop(0)
            r[user].append(current_item)  # append to R_u
            availability[current_item] -= 1

    return r


def round_robin_strategy(opt_r, availability, users, n):  # item-centric
    user_preferences = copy.deepcopy(opt_r)
    keys = users
    value = []
    r = {key: list(value) for key in keys}

    for rec in range(n):
        for user in users:
            current_item = user_preferences[user].pop(0)
            while availability[current_item] == 0:
                current_item = user_preferences[user].pop(0)
            r[user].append(current_item)  # append to R_u
            availability[current_item] -= 1

    return r


def item_assignment(item_availability, opt_r, sorted_users, n, item_centric):
    if item_centric == 'item':
        r = round_robin_strategy(opt_r, item_availability, sorted_users, n)
    elif item_centric == 'user':
        r = preference_based_strategy(opt_r, item_availability, sorted_users, n)
    else:
        r = preference_based_strategy(opt_r, item_availability, sorted_users, n)  # TO BE CHANGED
    return r
