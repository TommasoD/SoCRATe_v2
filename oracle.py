import argparse
import math
import pickle
import sys
import time
import random
import numpy as np

from assignment import item_assignment
from choice_model import choice_model
from initialisation import initialise_availability
from loss import top_n, loss_computation, top_n_availabilities, update_hist_loss
from rerank import re_rank
from synthetic_ds import create_synthetic_data, synthetic_utility, synthetic_recs, synthetic_price, \
    synthetic_utility_pl, synthetic_recs_pl
from weights import update_weights
from utils import write_to_file, convert, intersection

parser = argparse.ArgumentParser(description='Oracle')

parser.add_argument("--n_users", type=int, default=4)
parser.add_argument("--availability", type=int, default=1)
parser.add_argument("--iterations", type=int, default=15)
parser.add_argument("--m", type=int, default=20)
parser.add_argument("--run", type=int, default='1000000')
parser.add_argument("--compensation", type=str, default='item', choices=['item', 'user'])
parser.add_argument("--power_law", type=bool, default=False)
parser.add_argument("--adoption", type=str, default='top_k', choices=['top_k', 'random', 'utility'])
parser.add_argument("--granularity", type=str, default='fix', choices=['fix', 'group'])
parser.add_argument("--log", type=bool, default=False)

params, _ = parser.parse_known_args()

N_USERS = params.n_users
AVAILABILITY = params.availability
T = params.iterations
M = params.m
N_RUN = params.run
power_law = params.power_law
N = 5  # items recommended to the user
K = 3  # adopted items
MIN_ITEMS = N_USERS * (K * (T - 1) + N)  # minimum amount of items necessary
N_ITEMS = math.ceil(2 * MIN_ITEMS / AVAILABILITY)  # number of items in the system

assignment_strategy = params.compensation
choice_model_option = params.adoption
granularity = params.granularity
logging = params.log

folder = "./oracle/oracle-"
filename = str(N_USERS) + "u-" + str(T) + "iter-" + str(AVAILABILITY) + "av-" + str(N_RUN) + "r-" + \
           assignment_strategy + "-" + choice_model_option + "-" + granularity
if power_law:
    filename = filename + "-PL"

if logging:
    log = open(folder + filename + ".log", "w")
    sys.stdout = log

print(params)
print("Number of items: ", N_ITEMS)

alpha_1 = 0.5  # weight of objective functions item-dependant
alpha_2 = 0.5  # weight of utility
beta = 0.1  # parameter for weight update
gamma = 0.1  # parameter for weight update
delta = 0.1  # parameter for weight update
R = {}
OptR_hat = {}

# General Options
print("Choice model option: " + choice_model_option)
print("Assignment strategy: " + assignment_strategy)

items, users = create_synthetic_data(n_items=N_ITEMS, n_users=N_USERS, max_items=2 * N_ITEMS)
objective_functions_on_item = synthetic_price(items)
if power_law:
    print("Power law activated.")
    utility_matrix, utility_by_user = synthetic_utility_pl(items, users)
    recommendations = synthetic_recs_pl(utility_by_user, users)
else:
    recommendations = synthetic_recs(items, users)
    utility_matrix = synthetic_utility(recommendations, items, users)
write_to_file(recommendations, "obj_functions/recommendations_synth.json")
write_to_file(objective_functions_on_item, "obj_functions/objectives_synth.json")
write_to_file(utility_matrix, "obj_functions/utility_matrix_synth.json")

std_devs = []
std_dev_it = []
means = []
mean_it = []
keys = users

start_time = time.time()


def create_permutations(n_it, user_list, n_run):
    runs = []
    print("Computing runs...")
    for j in range(n_run):
        run = []
        for i in range(n_it):
            run.append(list(user_list))
            random.shuffle(user_list)
        runs.append(run)
    print("Runs done.")
    return runs


# User-group granularity management
length = len(users)
user_group_fast = users[:math.floor(length / 3)]
user_group_medium = users[:math.floor(length / 3 * 2)]
user_groups = [users, user_group_medium, user_group_fast]
group_order = [2, 1, 2, 0, 2, 1, 2, 0, 2, 1, 2, 0, 2, 1, 2]

for p in create_permutations(T, users, N_RUN):
    value = [alpha_1, alpha_2]
    weights = {key: list(value) for key in keys}

    value = [0, 0]
    losses = {key: list(value) for key in keys}
    historical_loss = {key: 0 for key in keys}

    availabilities = dict(zip(items, np.zeros(len(items), dtype=int)))
    initialise_availability(availabilities, AVAILABILITY)
    recs_it = pickle.loads(pickle.dumps(recommendations, -1))
    std_dev_it = []
    mean_it = []

    for t in range(0, T):
        users = p[t]

        if t:
            S = choice_model(R, K, recs_it, availabilities, choice_model_option, utility_matrix)
            weights = update_weights(weights, S, R, OptR_hat, objective_functions_on_item,
                                     utility_matrix, beta, gamma, delta, N)

        top_m_recommendations = top_n_availabilities(recs_it, M, availabilities)

        if granularity == 'group':
            g = group_order[t]
            users = intersection(users, user_groups[g])
            OptR = re_rank(top_m_recommendations, users, weights, objective_functions_on_item, utility_matrix)
            R = item_assignment(availabilities, OptR, users, N, assignment_strategy)
            OptR_hat = top_n(OptR, N)
            losses = loss_computation(R, OptR_hat, users, objective_functions_on_item, utility_matrix)
        else:
            OptR = re_rank(top_m_recommendations, users, weights, objective_functions_on_item, utility_matrix)
            R = item_assignment(availabilities, OptR, users, N, assignment_strategy)
            OptR_hat = top_n(OptR, N)
            losses = loss_computation(R, OptR_hat, users, objective_functions_on_item, utility_matrix)

        historical_loss = update_hist_loss(historical_loss, losses, weights)
        std_dev_it.append(np.std(list(historical_loss.values())))
        mean_it.append(np.mean(list(historical_loss.values())))

    std_devs.append(std_dev_it)
    means.append(mean_it)

write_to_file(means, folder + filename + "-mean" + ".json")
write_to_file(std_devs, folder + filename + "-std_dev" + ".json")

print('\n---MEAN MEAN---\nMinimum: ', min(np.mean([el for el in sublist]) for sublist in means),
      'Maximum: ', max(np.mean([el for el in sublist]) for sublist in means))
print('---STD_DEV MEAN---\nMinimum: ', min(np.std([el for el in sublist]) for sublist in means),
      'Maximum: ', max(np.std([el for el in sublist]) for sublist in means))
print('\n---STD_DEV MEAN---\nMinimum: ', min(np.mean([el for el in sublist]) for sublist in std_devs),
      'Maximum: ', max(np.mean([el for el in sublist]) for sublist in std_devs))
print('---STD_DEV STD_DEV---\nMinimum: ', min(np.std([el for el in sublist]) for sublist in std_devs),
      'Maximum: ', max(np.std([el for el in sublist]) for sublist in std_devs))

seconds = (time.time() - start_time)
print("\n---EXECUTION TIME: %s ---" % convert(seconds))
