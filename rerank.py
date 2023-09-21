def re_rank(rec, users, weights, prices, utility_matrix):
    keys = users
    value = []
    opt_r = {key: list(value) for key in keys}

    for user in users:
        rank = {}
        for r in rec[user]:
            rank[r] = (weights[user][0] * prices[r]) + (weights[user][1] * utility_matrix[r][user])

        # WHAT RE-RANK STRATEGY DO WE WANT TO USE...
        opt_r[user] = sorted(rank, key=rank.get, reverse=True)
    return opt_r
