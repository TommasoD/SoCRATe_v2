# SoCRATe
SoCRATe (**S**ystem f**o**r **C**ompensating **R**ecommendations with **A**vailability and **T**im**e**) is a framework to provide adaptive recommendations to users when items have limited availability.
SoCRATe watches user recommendation consumption and decides when to apply a loss compensation strategy to make up for sub-optimal recommendations (in terms of accuracy) due to limited item availability.
To frame evaluation, the system introduces a new set of measures that capture recommendation accuracy, user satisfaction and item consumption over time.
SoCRATe is relevant to several real-world applications, such as product and task recommendations.

## Description
This repository contains the code for SoCRATe, and it allows to simulate compensation strategies on real-world and synthetic datasets, in a limited item availability scenario.
Three real-world datasets are available to be analysed, namely *[Amazon Movies and TV](https://jmcauley.ucsd.edu/data/amazon/)*, *[Amazon Digital Music](https://jmcauley.ucsd.edu/data/amazon/)* and *[Task Recommendation](https://link.springer.com/article/10.1007/s00778-022-00740-6)*, in addition to a synthetic dataset with a smaller custom number of users and items.

The main file of the system is `orchestrator.py`, which can be executed from command line.
Different parameters for the simulation can be selected. Among them:
- `compensation` selects the compensation strategy: `round_robin` or `pref_driven`;
- `adoption` simulates how users adopt the recommended items: `top_k` (i.e., rank-based), `random`, `utility` (i.e., based on user utility);
- `sorting` defines the strategy for sorting users: `no_sort` (baseline option), `random`, `loss` (i.e., based on the previous iteration loss), `historical` (i.e., based on the historical user loss – default SoCRATe value);
- `granularity` chooses the time granularity: `fixed` (default value), `group` (i.e., users are divided into group);
- `dataset` option can be `synth` (synthetic), `az-music`, `az-movie`, `crowd`.

Additionally, the number of iterations to be analysed and the mean item availability can be selected as parameters.
Selecting the option for the synthetic dataset allows to also choose the number of items and users. The synthetic dataset is generated at runtime, but large synthetic datasets can also be saved in the under the `dataset` folder.

Simulation output is saved in `system_output` under a sub-folder named after the chosen simulation options (e.g., synth-T5-Aitem-Ctop_k-Shistorical for a 5 iterations simulation, with assignment of items according to round-robin compensation strategy (`item`), choice model `top_k`, sorting option `historical`). Two illustrative simulation outputs are available in this repository, reporting the execution of the system iteration by iteration.  

## First Time Simulation
The system computes the optimal user recommendations, the utility matrix and the other objective functions at the beginning of the execution. This initialisation process can take some time, and the output files for *Amazon Movies and TV* and *Amazon Music* are too large to be uploaded on GitHub.
The first time, you can compute them directly in the system, by uncommenting lines 142-148. Resulting files are automatically saved under the folder `obj_functions`.  
Files for the *Task Recommendation* dataset are provided.

## Brute-force Comparison Execution
To test the optimality of our solution, we designed a brute-force strategy that considers all possible orderings of users at each iteration to find the best one, i.e., the one that yields the highest loss compensation.
The execution is expected to be costly in terms of execution time, since it executes a high number of runs, but its best run is expected to be optimal or close to optimal.

To replicate this experiment, the file to be executed is `oracle.py`, again from command line.
The additional parameter `run` is available, to limit the number of runs when the possible combinations of users at each iteration becomes too large.
Our experiments considered 1000000 randomly selected runs.  

The system also saves logs and plots of the execution, comparing brute-force runs with an instance of SoCRATe with the same parameter configuration.
to allow the system to compare SoCRATe with the brute-force approach, you first need to execute SoCRATe from `orchestrator.py`, then execute `oracle.py`.
Plots and logs are saved under the `oracle` folder.

## Contacts
Please feel free to contact us at: <davide.azzalini@polimi.it>, <fabio.azzalini@polimi.it>, <chiara.criscuolo@polimi.it>, <tommaso.dolci@polimi.it>.
