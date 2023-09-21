# SoCRATe
SoCRATe is a framework to provide adaptive recommendations to users when items have limited availability. SoCRATe is relevant to several real-world applications, among which movie and task recommendations. SoCRATe has several appealing features: (i) watching users as they consume recommendations and accounting for user feedback in refining recommendations in the next round; (ii) implementing loss compensation strategies to make up for sub-optimal recommendations, in terms of accuracy, when items have limited availability; (iii) deciding when to re-generate recommendations on a need-based fashion. SoCRATe accommodates real users as well as simulated users to enable testing multiple recommendation choice models. To frame evaluation, SoCRATe introduces a new set of measures that capture recommendation accuracy, user satisfaction and item consumption over time. All these features make SoCRATe unique and able to adapt recommendations to user preferences in a resource-limited setting.

## Description
This repository contains the code for SoCRATe, and it allows to simulate compensation strategies on real-world and synthetic datasets, in a limited availability of items scenario.
Three datasets are available to be analysed, namely *[Amazon Movies and TV](https://jmcauley.ucsd.edu/data/amazon/)*, *[Amazon Digital Music](https://jmcauley.ucsd.edu/data/amazon/)* and *[Task Recommendation](https://link.springer.com/article/10.1007/s00778-022-00740-6)*, in addition to a synthetic dataset with a small custom number of users and items.

The main of the system is `orchestrator.py`. 
The desired dataset can be specified at line 42.
The user can select different options for the simulation. Among them:
- `choice_model_option` can be `top_k` (rank-based), `random`, `utility` (utility-based);
- `sorting_option` can be `no_sort` (baseline option), `random`, `loss`, `historical` (default value);
- `compensation_strategy` can be `round_robin`, `pref_driven`;
- `time-granularity` can be `fixed` (default value), `group` (user-group);
- `dataset` can be `synth` (synthetic), `az-music`, `az-movie`, `crowd`.

Additionally, for the synthetic dataset users can select the mean number of availability for the items in the simulation, the number of system iterations and more.  
Simulation output is saved in `system_output` under a folder named after the chosen simulation options (e.g., T15-Aitem-Crandom-Shistorical for a 15 iterations simulation, with assignment of items according to round-robin compensation strategy (`item`), choice model `random`, sorting option `historical`).  
The system also saves basic plots on the performance, showing loss and cumulative loss for certain specific users, under the `plots` folder.

## First Time Simulation
The system computes the optimal user recommendations, the utility matrix and the other objective functions at the beginning of the execution. This initialisation process can take some time, and depending on the dataset the output files may be too large to be uploaded on GitHub.
The first time, you can compute them directly in the system, by uncommenting lines 104-109. Resulting files are automatically saved under the folder `obj_functions`.  
Files for the synthetic and the *Task Recommendation* datasets are provided.

## Brute-force Comparison Execution
Add...

## Contacts
Please feel free to contact us for any question at <tommaso.dolci@polimi.it>
