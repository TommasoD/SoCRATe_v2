def loss_computation(r, opt_r_hat, users_list, prices, utility_matrix):
    keys = users_list
    value = []
    users_loss = {key: list(value) for key in keys}

    for user in users_list:
        # for all objective functions only based on item
        loss_obj1 = 0
        if user in list(r.keys()):
            for i in range(len(r[user])):
                r_item = r[user][i]
                opt_item = opt_r_hat[user][i]
                loss_obj1 += cut_above_zero(prices[opt_item] - prices[r_item])
        users_loss[user].append(loss_obj1)

    for user in users_list:
        # for all objective functions based on item and users
        loss_obj2 = 0
        if user in list(r.keys()):
            for i in range(len(r[user])):
                r_item = r[user][i]
                opt_item = opt_r_hat[user][i]
                loss_obj2 += cut_above_zero(utility_matrix[opt_item][user] - utility_matrix[r_item][user])
        users_loss[user].append(loss_obj2)

    return users_loss


def update_hist_loss(hist_loss, losses, weights):
    for user in losses:
        # user_loss = sum(losses[user])
        user_loss = (weights[user][0] * losses[user][0]) + (weights[user][1] * losses[user][1])
        hist_loss[user] += user_loss
    return hist_loss


def cut_above_zero(number):
    if number < 0:
        number = 0
    return number


def top_n(old_dict, n):
    # take top N from old_dict (used for opt_r and top_m_recommendations)
    new_dict = {}
    for u in old_dict:
        new_dict[u] = old_dict[u][0:n]
    return new_dict


def top_n_availabilities(old_dict, m, availabilities):
    keys = old_dict.keys()
    value = []
    new_dict = {key: list(value) for key in keys}
    for u in old_dict:
        i = 0
        while len(new_dict[u]) < m:
            item_id = old_dict[u][i]
            if availabilities[item_id] > 0:
                new_dict[u].append(item_id)
            i = i + 1
    return new_dict
