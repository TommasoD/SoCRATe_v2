import math
import sys
import time
import numpy as np
import pandas as pd
import json
import argparse

# Parameters
from assignment import item_assignment
from choice_model import choice_model
from initialisation import initialise_availability
from loss import top_n, loss_computation, top_n_availabilities, update_hist_loss
from plot import plot_system, oracle_plot, distribution_plot
from rerank import re_rank
from synthetic_ds import create_synthetic_data, synthetic_utility, synthetic_recs, synthetic_price, synthetic_recs_pl, \
    synthetic_utility_pl
from user_sorting import user_sorting
from weights import update_weights
from utils import write_to_file, preprocessing, train_recommender, convert, intersection

parser = argparse.ArgumentParser(description='Orchestrator')

parser.add_argument("--n_users", type=int, default=4)
parser.add_argument("--availability", type=int, default=1)
parser.add_argument("--iterations", type=int, default=15)
parser.add_argument("--m", type=int, default=20)
parser.add_argument("--compensation", type=str, default='round_robin', choices=['round_robin', 'pref_driven'])
parser.add_argument("--adoption", type=str, default='top_k', choices=['top_k', 'random', 'utility'])
parser.add_argument("--sorting", type=str, default='historical', choices=['no_sort', 'random', 'loss', 'historical'])
parser.add_argument("--granularity", type=str, default='fix', choices=['fix', 'group'])
parser.add_argument("--dataset", type=str, default='synth', choices=['az-music', 'az-movie', 'crowd', 'synth'])
parser.add_argument("--power_law", type=bool, default=False)
parser.add_argument("--log", type=bool, default=False)

params, _ = parser.parse_known_args()

N_USERS = params.n_users
mean_availability = params.availability  # average availability across items
assignment_strategy = "item" if params.compensation == "round_robin" else "user"  # compensation strategy adopted
choice_model_option = params.adoption  # choice model adopted
sorting_option = params.sorting  # sorting option adopted
time_granularity = params.granularity  # time granularity under analysis
dataset_abbr = params.dataset  # dataset in use
power_law = params.power_law  # type of preferences: same for all or realistic
logging = params.log

T = params.iterations  # number of iterations of SoCRATe
M = params.m  # number of items returned by the single-user recommender (does only change performance of the system)
N = 5  # number of items recommended to the user
K = 3  # number of adopted items
alpha_1 = 0.5  # weight of objective functions item-dependant
alpha_2 = 0.5  # weight of utility
beta = 0.1  # parameter for weight update
gamma = 0.1  # parameter for weight update
delta = 0.1  # parameter for weight update
R = {}
OptR_hat = {}

start_time = time.time()

folder = "./oracle/orchestrator-"
filename = str(N_USERS) + "u-" + str(T) + "iter-" + str(mean_availability) + "av-1000000r-" + \
           assignment_strategy + "-" + choice_model_option + "-" + time_granularity
if power_law:
    filename = filename + "-PL"
if logging:
    log = open(folder + filename + ".log", "a")
    sys.stdout = log

MIN_ITEMS = N_USERS * (K * (T - 1) + N)  # minimum amount of items necessary
N_ITEMS = math.ceil(2 * MIN_ITEMS / mean_availability)  # number of items in the system

print(params)
data_file_path = ''
metadata_file_path = ''

# Dataset-related options
if dataset_abbr == "az-music":
    data_file_path = 'datasets/reviewsAmazonMusicRecommenderSystem.csv'
    metadata_file_path = 'datasets/metadataAmazonMusicRecommenderSystem.csv'
    M = 450  # tuned to the nature of the dataset
    mean_availability = 150  # optimal value for T=15
elif dataset_abbr == "az-movie":
    data_file_path = 'datasets/reviewsAmazonMoviesRecommenderSystem.csv'
    metadata_file_path = 'datasets/metadataAmazonMoviesRecommenderSystem.csv'
    M = 150
    mean_availability = 30  # optimal value for T=15
elif dataset_abbr == "crowd":
    data_file_path = 'datasets/reviewsCrowdsourcing.csv'
    metadata_file_path = 'datasets/metadataCrowdsourcing.csv'
    M = 200
    mean_availability = 5  # optimal value for T=15

# SYSTEM LOGIC STARTS FROM HERE

test_name = "T{}-A{}-C{}-S{}".format(T, assignment_strategy, choice_model_option, sorting_option)
if dataset_abbr == 'synth':
    test_name = 'synth-' + test_name
    print("Dataset: synthetic")
    if power_law:
        print("Power Law: activated")
        test_name = test_name + "-PL"
else:
    test_name = dataset_abbr + '-' + test_name
    print("Dataset: " + dataset_abbr)

if time_granularity == "group":
    test_name = 'group-' + test_name

if dataset_abbr == 'synth':  # use synthetic dataset
    items, users = create_synthetic_data(n_items=N_ITEMS, n_users=N_USERS, max_items=2 * N_ITEMS)
    objective_functions_on_item = synthetic_price(items)
    if power_law:
        utility_matrix, utility_by_user = synthetic_utility_pl(items, users)
        recommendations = synthetic_recs_pl(utility_by_user, users)
    else:
        recommendations = synthetic_recs(items, users)
        utility_matrix = synthetic_utility(recommendations, items, users)
    write_to_file(recommendations, "obj_functions/recommendations_synth.json")
    write_to_file(objective_functions_on_item, "obj_functions/objectives_synth.json")
    write_to_file(utility_matrix, "obj_functions/utility_matrix_synth.json")
else:
    # Data preprocessing
    data_train = pd.read_csv(data_file_path).groupby(
        ['CUST_ID', 'ARTICLE_ID'])['RATING'].mean().reset_index(name='FREQUENCY')
    items, users, user_indexes, ratings = preprocessing(data_train)

    # Create and train a new single-user recommender
    knn_recommender = train_recommender(ratings)

    # Initialise objective functions + utility + recommendations
    print("Loading objective functions...")
    with open("obj_functions/objectives_{}.json".format(dataset_abbr)) as read_file:
        objective_functions_on_item = json.load(read_file)
    with open("obj_functions/utility_matrix_{}.json".format(dataset_abbr)) as read_file:
        utility_matrix = json.load(read_file)
    print("Loading recommendations...")
    with open("obj_functions/recommendations_{}.json".format(dataset_abbr)) as read_file:
        recommendations = json.load(read_file)

    # # UNCOMMENT IF OBJECTIVES, UTILITY MATRIX AND RECOMMENDATIONS ARE NOT YET COMPUTED
    # objective_functions_on_item = price_initialise(metadata_file_path)
    # write_to_file(objective_functions_on_item, "obj_functions/objectives_{}.json".format(dataset_abbr))
    # utility_matrix = utility_initialise(users, user_indexes, knn_recommender, items)
    # write_to_file(utility_matrix, "obj_functions/utility_matrix_{}.json".format(dataset_abbr))
    # recommendations = get_recommendations(users, user_indexes, ratings, len(items), knn_recommender, items)
    # write_to_file(recommendations, "obj_functions/recommendations_{}.json".format(dataset_abbr))

print('\n# Users:', len(users))
print('# Items:', len(items), "\n")

# Users ID for plotting results
length = len(users)
plot_users = [users[0], users[length // 3], users[length // 3 * 2], users[length - 1]]

# Separate users into groups for user-group time granularity
# In a real-case scenario users can be split according to their history (more tasks done = faster consumer)
user_group_fast = users[:math.floor(length / 3)]
user_group_medium = users[:math.floor(length / 3 * 2)]
user_groups = [users, user_group_medium, user_group_fast]
# all users 3 times, fast+medium 7 times, fast users 15 times
group_order = [2, 1, 2, 0, 2, 1, 2, 0, 2, 1, 2, 0, 2, 1, 2]
if time_granularity == 'group':
    print(user_groups)
    print("\n")

# Initialise weights + loss
keys = users
value = [alpha_1, alpha_2]
weights = {key: list(value) for key in keys}

value = [0, 0]
losses = {key: list(value) for key in keys}
historical_loss = {key: 0 for key in keys}

folder_name = "system_output/" + test_name + "/"

# Assign availability to each item
availabilities = dict(zip(items, np.zeros(len(items), dtype=int)))
initialise_availability(availabilities, mean_availability)
# normal_initialise_availability(availabilities, mean_availability)
write_to_file(availabilities, folder_name + "availabilities0.json")
write_to_file(weights, folder_name + "weights0.json")

# --------- ITERATIONS START ---------

s_mean = []
s_std = []

for t in range(0, T):
    print('Iteration', t + 1)  # for each iteration except the first one, execute choice model and weight update
    if t:
        # Compute adopted items
        S = choice_model(R, K, recommendations, availabilities, choice_model_option, utility_matrix)

        # write_to_file(S, folder_name + "adopted_items" + str(t) + ".json")
        write_to_file(availabilities, folder_name + "availabilities" + str(t) + ".json")

        # Update weights
        weights = update_weights(weights, S, R, OptR_hat, objective_functions_on_item,
                                 utility_matrix, beta, gamma, delta, N)
        write_to_file(weights, folder_name + "weights" + str(t) + ".json")

    # Take first M recommendations
    top_m_recommendations = top_n_availabilities(recommendations, M, availabilities)  # defined in loss.py

    # From here split into two directions: fixed time granularity and user-group
    if time_granularity == 'group':
        g = group_order[t]
        OptR = re_rank(top_m_recommendations, user_groups[g], weights, objective_functions_on_item, utility_matrix)
        write_to_file(OptR, folder_name + "OptR" + str(t) + ".json")

        if sorting_option != 'no_sort':
            users = user_sorting(losses, historical_loss, users, weights, sorting_option)
            user_groups[g] = user_sorting(losses, historical_loss, user_groups[g], weights, sorting_option)
        write_to_file(users, folder_name + "sorted_users" + str(t) + ".json")

        R = item_assignment(availabilities, OptR, user_groups[g], N, assignment_strategy)
        OptR_hat = top_n(OptR, N)  # get top N from OptR (function is defined in loss.py)
        losses = loss_computation(R, OptR_hat, users, objective_functions_on_item, utility_matrix)
    else:  # fixed time granularity
        OptR = re_rank(top_m_recommendations, users, weights, objective_functions_on_item, utility_matrix)
        write_to_file(OptR, folder_name + "OptR" + str(t) + ".json")

        if sorting_option != 'no_sort':
            users = user_sorting(losses, historical_loss, users, weights, sorting_option)
        write_to_file(users, folder_name + "sorted_users" + str(t) + ".json")

        R = item_assignment(availabilities, OptR, users, N, assignment_strategy)
        OptR_hat = top_n(OptR, N)  # get top N from OptR (function is defined in loss.py)
        losses = loss_computation(R, OptR_hat, users, objective_functions_on_item, utility_matrix)

    historical_loss = update_hist_loss(historical_loss, losses, weights)
    s_std.append(np.std(list(historical_loss.values())))
    s_mean.append(np.mean(list(historical_loss.values())))
    write_to_file(losses, folder_name + "losses" + str(t) + ".json")
    write_to_file(historical_loss, folder_name + "hist_loss" + str(t) + ".json")

# Save plot analysis
# plot_system(T, plot_users, utility_matrix, objective_functions_on_item, test_name)

# Print mean and standard deviation
print('\nVector of std_dev: ', ["{:.5f}".format(i) for i in s_std])
print('Average std_dev SoCRATe: {:.5f}'.format(np.mean(s_std)))
print('Deviation std_dev SoCRATe: {:.5f}'.format(np.std(s_std)))

print('\nVector of means: ', ["{:.5f}".format(i) for i in s_mean])
print('Average mean SoCRATe: {:.5f}'.format(np.mean(s_mean)))
print('Deviation mean SoCRATe: {:.5f}'.format(np.std(s_mean)))

# Save diagrams
# try:
#     path = "./oracle/oracle-" + str(N_USERS) + "u-" + str(T) + "iter-" + str(mean_availability) + "av-1000000r-" + \
#            assignment_strategy + "-" + choice_model_option + "-" + time_granularity
#     title = str(N_USERS) + "u-" + str(T) + "iter-" + str(mean_availability) + "av-1000000r-" + assignment_strategy + \
#             "-" + choice_model_option + "-" + time_granularity
#     if power_law:
#         path = path + "-PL"
#         title = title + "-PL"
#     path_std = path + "-std_dev.json"
#     path_mean = path + "-mean.json"
#     print("\nFile path: ", path)
#     oracle_plot(path_std, title, np.mean(s_std))
#     distribution_plot(path_std, title, np.mean(s_std), 'Average Std-Dev')
#     # distribution_plot(path_mean, title, np.mean(s_mean), 'Average Mean')
#
#     if logging:
#         # load oracle runs
#         with open(path_std) as json_file:
#             std_oracle = json.load(json_file)
#         with open(path_mean) as json_file:
#             mean_oracle = json.load(json_file)
#
#         support1 = list(np.mean([el for el in sublist]) for sublist in mean_oracle)
#         support2 = list(np.std([el for el in sublist]) for sublist in mean_oracle)
#         support3 = list(np.mean([el for el in sublist]) for sublist in std_oracle)
#         support4 = list(np.std([el for el in sublist]) for sublist in std_oracle)
#
#         print('\n---AVERAGE OF MEANS---\nMinimum: ', min(support1), 'Maximum: ', max(support1), 'Mean: ',
#               np.mean(support1))
#         print('---STD_DEV OF MEANS---\nMinimum: ', min(support2), 'Maximum: ', max(support2), 'Mean: ',
#               np.mean(support2))
#         print('\n---AVERAGE OF STD_DEV---\nMinimum: ', min(support3), 'Maximum: ', max(support3), 'Mean: ',
#               np.mean(support3))
#         print('---STD_DEV OF STD_DEV---\nMinimum: ', min(support4), 'Maximum: ', max(support4), 'Mean: ',
#               np.mean(support4))
#
# except FileNotFoundError:
#     print("No oracle experiment found.")

seconds = (time.time() - start_time)
print("\n---EXECUTION TIME: %s ---" % convert(seconds))
