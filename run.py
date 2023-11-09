import sys
import pandas as pd
import matplotlib.pyplot as plt
import mesa
from ConPro.model import ConPro
from ConPro.server import server
from mesa.batchrunner import batch_run
import pickle
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(style="ticks", color_codes=True)
from statistics import stdev, mean
from datetime import datetime, time, timedelta
import json
import itertools
import pandas as pd
import pathlib
import glob

# print(glob.glob('.'))
import unicodedata
import re
import random
import os
from multiprocessing import freeze_support

# Analysis
def assess_results(results, single_agent):
    # Make dataframe of results
    print("to be added later")
    pass


# Run the model

def single_run():
    print("Running Single Model")
    # instantiate the model
    model = ConPro()
    # run the model
    model.run_model()
    # Get results
    model_results = model.datacollector.get_model_vars_dataframe()
    # Convert to make similar to batch_run_results
    model_results["Step"] = model_results.index
    agent_results = model.datacollector.get_agent_vars_dataframe()
    agent_results = agent_results.reset_index()
    # assess the results
    assess_results(model_results, agent_results)

def create_directory():
    results_path = "resultsOnetime/" + datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    output_path = "./" + results_path + "/"
    # print (output_path)
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, results_path)
    #    print (final_directory, os.path.exists(final_directory))
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
    results_path = "resultsOnetime/" + "Results"
    output_path1 = "./" + results_path + "/"
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, results_path)
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
    return output_path


####

#####

Scenarios1 = {
    "n_plastering_workers" : [2],
    "n_painting_workers" : [2],
    "zone_max_worker" : [2],
    "zone_max_trades" : [2],
    "zone_max_visitor" : [10000],
    "KEYSTART_max" : [2],
    "KEYFRAMES_max" : [2],
    "KEYMECH_max" : [2],
    "KEYELEC_max" : [2],
    "KEYINSU_max" : [2],
    "KEYSTUD_max" : [2],
    "KEYPAINTING_max" : [2],
    "KEYFINISHING_max" : [2],
    "KEYEND_max" : [2],
    "work_duration" : [3],
    "work_duration_min" : [1],
    "work_duration_max" : [4],
    # "tasks_sequence" : [{1: ["KEYSTART"]}],
    "tasks_sequence": [{1: ["KEYSTART", "KEYFRAMES"], 2: ['KEYMECH'], 3: ['KEYELEC'], 4: ["KEYINSU"], 5: ["KEYSTUD"], 6: ["KEYPAINTING"], 7: ["KEYFINISHING"], 8: ["KEYEND"]}],
    "simulation_speed_microsec":[15000000], #1500000 1.5 sec   #15000000 15 sec
    "one_behavior_file":[True],
"palstering_worker_skills":[{"KEYMECH": 100, "KEYSTART": 100, "KEYINSU": 100, "KEYPAINTING": 100, "KEYEND": 100}],
"painting_worker_skills":[{"KEYFRAMES": 200, "KEYELEC": 200, "KEYSTUD": 150, "KEYFINISHING": 122}],
    "drywalls_points": [
        [
        # [[3,118],[19,118], "dry_wall5"],
        # [[19,119],[19,127], "dry_wall5"],
        [[2, 23], [12, 23], "dry_wall3"],
        [[12, 11], [12, 22], "dry_wall3"],
        # [[11, 11], [2, 11], "dry_wall4"],
        # [[12, 10], [15, 10], "dry_wall1"],
        #  [[43,33],[43,38], "dry_wall7"]]
    ]
    ],
}

Scenarios2 = {
    "n_plastering_workers" : [2],
    "n_painting_workers" : [2],
    "zone_max_worker" : [2],
    "zone_max_trades" : [2],
    "zone_max_visitor" : [10000],
    "KEYSTART_max" : [2],
    "KEYFRAMES_max" : [2],
    "KEYMECH_max" : [2],
    "KEYELEC_max" : [2],
    "KEYINSU_max" : [2],
    "KEYSTUD_max" : [2],
    "KEYPAINTING_max" : [2],
    "KEYFINISHING_max" : [2],
    "KEYEND_max" : [2],
    "work_duration" : [3],
    "work_duration_min" : [1],
    "work_duration_max" : [4],
    # "tasks_sequence" : [{1: ["KEYSTART"]}],
    "tasks_sequence": [{1: ["KEYSTART", "KEYFRAMES"], 2: ['KEYMECH'], 3: ['KEYELEC'], 4: ["KEYINSU"], 5: ["KEYSTUD"], 6: ["KEYPAINTING"], 7: ["KEYFINISHING"], 8: ["KEYEND"]}],
    "simulation_speed_microsec":[15000000], #1500000 1.5 sec   #15000000 15 sec
    "one_behavior_file":[True],
"palstering_worker_skills":[{"KEYMECH": 100, "KEYSTART": 100, "KEYINSU": 100, "KEYPAINTING": 100, "KEYEND": 100,"KEYFRAMES": 200, "KEYELEC": 200, "KEYSTUD": 150, "KEYFINISHING": 122}], #
"painting_worker_skills":[{"KEYMECH": 100, "KEYSTART": 100, "KEYINSU": 100, "KEYPAINTING": 100, "KEYEND": 100,"KEYFRAMES": 200, "KEYELEC": 200, "KEYSTUD": 150, "KEYFINISHING": 122}],
    "drywalls_points": [
        [
        # [[3,118],[19,118], "dry_wall5"],
        # [[19,119],[19,127], "dry_wall5"],
        [[2, 23], [12, 23], "dry_wall3"],
        [[12, 11], [12, 22], "dry_wall3"],
        # [[11, 11], [2, 11], "dry_wall4"],
        # [[12, 10], [15, 10], "dry_wall1"],
        #  [[43,33],[43,38], "dry_wall7"]]
    ]
    ]
}

Scenarios3 = {
    "n_plastering_workers" : [2],
    "n_painting_workers" : [2],
    "zone_max_worker" : [2],
    "zone_max_trades" : [2],
    "zone_max_visitor" : [10000],
    "KEYSTART_max" : [1,2],
    "KEYFRAMES_max" : [1,2],
    "KEYMECH_max" : [1,2],
    "KEYELEC_max" : [1,2],
    "KEYINSU_max" : [1,2],
    "KEYSTUD_max" : [1,2],
    "KEYPAINTING_max" : [1,2],
    "KEYFINISHING_max" : [1,2],
    "KEYEND_max" : [1, 2],
    "work_duration" : [3],
    "work_duration_min" : [1],
    "work_duration_max" : [4],
    # "tasks_sequence" : [{1: ["KEYSTART"]}],
    "tasks_sequence": [{1: ["KEYSTART", "KEYFRAMES"], 2: ['KEYMECH'], 3: ['KEYELEC'], 4: ["KEYINSU"], 5: ["KEYSTUD"], 6: ["KEYPAINTING"], 7: ["KEYFINISHING"], 8: ["KEYEND"]}],
    "simulation_speed_microsec":[15000000], #1500000 1.5 sec   #15000000 15 sec
    "one_behavior_file":[True],
"palstering_worker_skills":[{"KEYMECH": 100, "KEYSTART": 100, "KEYINSU": 100, "KEYPAINTING": 100, "KEYEND": 100}],
"painting_worker_skills":[{"KEYFRAMES": 200, "KEYELEC": 200, "KEYSTUD": 150, "KEYFINISHING": 122}],
    "drywalls_points": [
        [
        # [[3,118],[19,118], "dry_wall5"],
        # [[19,119],[19,127], "dry_wall5"],
        [[2, 23], [12, 23], "dry_wall3"],
        [[12, 11], [12, 22], "dry_wall3"],
        # [[11, 11], [2, 11], "dry_wall4"],
        # [[12, 10], [15, 10], "dry_wall1"],
        #  [[43,33],[43,38], "dry_wall7"]]
    ]
    ],
}

######
# At the end of each model run, calculate the fraction of trees which are Burned Out

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def append_df(condition=False):
    "combine resulted excel file into"
    file_path = pathlib.Path(__file__).parent.absolute()
    project_path = file_path.parent
    li = []
    # print (file_path)
    for file_name in glob.iglob("resultsOnetime/*/" + '*.xlsx', recursive=True):
        #        print (file_name)
        if "model" in file_name:
            df = pd.read_excel(file_name, header=0)
            if condition:
                df = df[df["Trade"] == "plastering"]
            li.append(df)
    frame = pd.concat(li, axis=0, ignore_index=True)
    filename = 'Results' + datetime.now().strftime("%m_%d_%Y_%H_%M_%S") + '.xlsx'
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, "resultsOnetime", "Results", filename)
    frame.to_excel(final_directory)


def runner(variable_par_ls, iterations=1, max_steps=1000, number_processes=None,

           data_collection_period=1, variable_params=Scenarios1):
    agent_reporters = {"AgentCapacity": "agent_name", "current_datetime": "current_datetime"}
    variable_par_dic = dict(zip(variable_params.keys(), [[i] for i in variable_par_ls]))  # make dic from two lists,
    #    print (variable_par_dic)
    results = batch_run(ConPro, parameters=variable_par_dic,
                        iterations=iterations,
                        max_steps=max_steps,
                        number_processes=number_processes,
                        data_collection_period=data_collection_period,
                        display_progress=True)
    results_df = pd.DataFrame(results)
    # results_filtered = results_df[(results_df.Step == max_steps) & (results_df.Trade == "painting")]
    results_filtered = results_df
    # results_filtered = results_df
    output_path = create_directory()
    filenamemodel = output_path + 'model_' + datetime.now().strftime("%m-%d%-Y_%H_%M_%S")
    results_filtered.to_pickle(output_path + "data.pkl")
    results_filtered.to_excel(filenamemodel + ".xlsx")
    #    results_filtered = results_df[(results_df.AgentID == 0) & (results_df.Step == 100)]
    #    N_values = results_filtered.N.values
    #    gini_values = results_filtered.Gini.values
    #    plt.scatter(N_values, gini_values)
    #    # First, we filter the results
    #    one_episode_wealth = results_df[(results_df.N == 10) & (results_df.iteration == 2)]
    #    # Then, print the columns of interest of the filtered data frame
    #    print(
    #        one_episode_wealth.to_string(
    #            index=False, columns=["Step", "AgentID", "Wealth"], max_rows=25
    #        )
    #    )
    #    # For a prettier display we can also convert the data frame to html, uncomment to test in a Jupyter Notebook
    #    # from IPython.display import display, HTML
    #    # display(HTML(one_episode_wealth.to_html(index=False, columns=['Step', 'AgentID', 'Wealth'], max_rows=25)))
    #    results_one_episode = results_df[
    #        (results_df.N == 10) & (results_df.iteration == 1) & (results_df.AgentID == 0)
    #    ]
    #    print(results_one_episode.to_string(index=False, columns=["Step", "Gini"], max_rows=25))

def main(iterations=10, max_steps=30000, variable_params=Scenarios1, data_collection_period =3):  # variable_params=SiteA1 SiteB SiteA
    List_of_Variables = []
    for keys, item in variable_params.items():
        List_of_Variables.append(item)
    list_combination = list(itertools.product(*List_of_Variables))
    variable_par_dic = {}
    start = datetime.now()
    for variable_par_ls in list_combination:
        variable_par_ls = list(variable_par_ls)
        data_collection_period = min(max_steps, data_collection_period)
        runner(variable_par_ls, iterations, max_steps=max_steps, number_processes=None, data_collection_period=data_collection_period, variable_params=variable_params)
    append_df(condition=False)
    print("Finished in: {:.2f}s".format((datetime.now() - start).total_seconds()))

if __name__ == '__main__':
    # args = sys.argv[1:]
    args = ["runserver"]

    if args[0] == "runserver":
        server.launch()
    elif "Single" in args[0]:
        single_run()

    elif "batch" in args[0]:
        print("Conducting a Batch Run")
        freeze_support()
        # main(iterations=1, max_steps=1, variable_params=Scenarios1)
        # main(iterations=2, max_steps=10000, variable_params=Scenarios2, data_collection_period=3)
        main(iterations=2, max_steps=1000, variable_params=Scenarios2, data_collection_period=10)

    elif "results" in args[0]:
        append_df(condition=True)
