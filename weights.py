import copy


def update_weights(weights, s, r, optR_hat, prices, utility_matrix, beta, gamma, delta, n):
    old_weights = copy.deepcopy(weights)

    for u in weights:
        if u in list(r.keys()):
            for item in s[u]:
                coefficient = beta / len(s[u])
                # for j in len(prices) do weight update
                update = coefficient * (prices[item] - old_weights[u][0])
                weights[u][0] += update

                update = coefficient * (utility_matrix[item][u] - old_weights[u][1])
                weights[u][1] += update

            # for j in len(prices) do weight update
            w_diff = weights[u][0] - old_weights[u][0]
            opt_sum = sum([prices[i] for i in optR_hat[u]])
            r_sum = sum([prices[i] for i in r[u]])
            abs_diff = abs((opt_sum - r_sum) / n)
            weights[u][0] = old_weights[u][0] + (w_diff * gamma * (1 - abs_diff))

            w_diff = weights[u][1] - old_weights[u][1]
            opt_sum = sum([utility_matrix[i][u] for i in optR_hat[u]])
            r_sum = sum([utility_matrix[i][u] for i in r[u]])
            abs_diff = abs((opt_sum - r_sum) / n)
            weights[u][1] = old_weights[u][1] + (w_diff * gamma * (1 - abs_diff))

            for idx, item in enumerate(r[u]):
                if item not in s[u]:
                    coefficient = ((n - idx) / n) * (delta / (n - len(s[u])))
                    # for j in len(prices) do weight update
                    weights[u][0] -= coefficient * (prices[item] - old_weights[u][0])
                    weights[u][1] -= coefficient * (utility_matrix[item][u] - old_weights[u][1])

            # sum of weights must be 1
            sum_of_weights = weights[u][0] + weights[u][1]
            weights[u][0] = weights[u][0] / sum_of_weights
            weights[u][1] = weights[u][1] / sum_of_weights

    return weights


# for u in weights.keys():
#     for i in S[u]:
#         weights[u][0] = weights[u][0] + ((beta / len(S[u])) * (prices[i] - weights[u][0]))
#         weights[u][1] = weights[u][1] + ((beta / len(S[u])) * (utility_matrix[i][u] - weights[u][1]))
#
#     weights[u][0] = old_weights[u][0] + ((weights[u][0] - old_weights[u][0]) * gamma *
#                                          (1 - abs((sum([prices[i] for i in optR_hat[u]]) / N) -
#                                                   (sum([prices[i] for i in R[u]]) / N))))
#     weights[u][1] = old_weights[u][1] + ((weights[u][1] - old_weights[u][1]) * gamma *
#                                          (1 - abs((sum([utility_matrix[i][u] for i in optR_hat[u]]) / N) -
#                                                   (sum([utility_matrix[i][u] for i in R[u]]) / N))))
#
#     for idx, i in enumerate(R[u]):
#         if i not in S[u]:
#             weights[u][0] -= (((N - idx) / N) * (delta / (N - len(S))) * (prices[i] - weights[u][0]))
#             weights[u][1] -= (((N - idx) / N) * (delta / (N - len(S))) * (utility_matrix[i][u] - weights[u][1]))
