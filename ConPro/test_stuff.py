# # import random
# # # print(all([True, True]))
# # # random.choice(range(1))
# # print(all([0, 0 ]))
# # # tasks_sequence = {1:["KEYSTART", "KEYFRAMES"], 2:["KEYMECH"]}
# # # print ([task_key for sequence_key in tasks_sequence.keys() for task_key in tasks_sequence[sequence_key] ])
# # def ala():
# #     return 1,3 , 4
# # print (ala())
# #
# # #
# # import numpy as np
# # import pandas as pd
# # pd.set_option('display.max_rows', 1000)
# # pd.set_option('display.max_columns', 1000)
# # def generat_path_file(filename_iw="init_inner_walls.csv", filename_ew="init_external_walls.csv",output_filename="init_route.csv" ):
# #     """
# #     Read two files external waslls and internal walls and generate the route (grid file) on the basis of this two files
# #     :param filename_iw: grid represent internal waslls file name IW mean interanl wall grid
# #     :param filename_ew: grid represent extanal waslls file name W mean external wall grid
# #     :return:
# #     """
# #     xymap_pd_iw = pd.read_csv("{}".format("ConPro/{}".format(filename_iw)), header=None)
# #     xymap_pd_iw.reset_index()
# #     xymap_pd_iw = xymap_pd_iw.set_axis(range(xymap_pd_iw.shape[0], 0, -1), axis='index')
# #     xymap_pd_iw = xymap_pd_iw.applymap(str)
# #     xymap_pd_ew = pd.read_csv("{}".format("ConPro/{}".format(filename_ew)), header=None)
# #     xymap_pd_ew.reset_index()
# #     xymap_pd_ew = xymap_pd_ew.set_axis(range(xymap_pd_ew.shape[0], 0, -1), axis='index')
# #     xymap_pd_ew = xymap_pd_ew.applymap(str)
# #     init_route = xymap_pd_iw.combine(xymap_pd_ew, np.maximum)
# #     init_route = init_route.replace("0", 1)
# #     init_route = init_route.replace("W", 0)
# #     init_route = init_route.replace("IW", 0)
# #     init_route = init_route.applymap(int)
# #     init_route.to_csv("{}".format("ConPro/{}".format(output_filename)), index=False, header=False)
# import pandas as pd
# from datetime import datetime
# from configparser import ConfigParser
# from statistics import mean
# import warnings
# import numpy as np
# import pandas as pd
# import scipy.stats as st
# import statsmodels.api as sm
# from scipy.stats._continuous_distns import _distn_names
# import matplotlib
# import matplotlib.pyplot as plt
# config = ConfigParser()
# def get_pdfunc(data=[1,2,2,2,2,3], plot = True, title="Durations in Possibly Working Zone", x_title="Duration"):
#
#     # data = pd.Series(sm.datasets.elnino.load_pandas().data.set_index('YEAR').values.ravel())
#     data = pd.Series(data)
#     matplotlib.rcParams['figure.figsize'] = (16.0, 12.0)
#     matplotlib.style.use('ggplot')
#     # Create models from data
#     def best_fit_distribution(data, bins=200, ax=None):
#         """Model data by finding best fit distribution to data"""
#         # Get histogram of original data
#         y, x = np.histogram(data, bins=bins, density=True)
#         x = (x + np.roll(x, -1))[:-1] / 2.0
#
#         # Best holders
#         best_distributions = []
#
#         # Estimate distribution parameters from data
#         for ii, distribution in enumerate([d for d in _distn_names if not d in ['levy_stable', 'studentized_range']]):
#
#             print("{:>3} / {:<3}: {}".format(ii + 1, len(_distn_names), distribution))
#             distribution_obj = getattr(st, distribution)
#
#             # Try to fit the distribution
#             try:
#                 # Ignore warnings from data that can't be fit
#                 with warnings.catch_warnings():
#                     warnings.filterwarnings('ignore')
#
#                     # fit dist to data
#                     params = distribution_obj.fit(data)
#
#                     # Separate parts of parameters
#                     arg = params[:-2]
#                     loc = params[-2]
#                     scale = params[-1]
#
#                     # Calculate fitted PDF and error with fit in distribution
#                     pdf = distribution_obj.pdf(x, loc=loc, scale=scale, *arg)
#                     sse = np.sum(np.power(y - pdf, 2.0))
#
#                     # if axis pass in add to plot
#                     try:
#                         if ax:
#                             pd.Series(pdf, x).plot(ax=ax)
#                         end
#                     except Exception:
#                         pass
#
#                     # identify if this distribution is better
#                     best_distributions.append((distribution_obj, params, sse, distribution))
#
#             except Exception:
#                 pass
#
#         return sorted(best_distributions, key=lambda x: x[2])
#
#
#     def make_pdf(dist_name, params, size=10000, dist_obj=None):
#         """Generate distributions's Probability Distribution Function """
#         # Separate parts of parameters
#         if dist_obj == None:
#             dist = getattr(st, dist_name)
#         arg = params[:-2]
#         loc = params[-2]
#         scale = params[-1]
#         # Get sane start and end points of distribution
#         start = dist.ppf(0.01, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.01, loc=loc, scale=scale)
#         end = dist.ppf(0.99, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.99, loc=loc, scale=scale)
#         # Build PDF and turn into pandas Series
#         x = np.linspace(start, end, size)
#         y = dist.pdf(x, loc=loc, scale=scale, *arg)
#         pdf = pd.Series(y, x)
#         return pdf
#
#     # numpy.random.choice(numpy.arange(1, 7), p=[0.1, 0.05, 0.05, 0.2, 0.4, 0.2])
#     # Load data from statsmodels datasets
#
#     # Plot for comparison
#     plt.figure(figsize=(12, 8))
#     ax = data.plot(kind='hist', bins=200, density=True, alpha=0.5,
#                    color=list(matplotlib.rcParams['axes.prop_cycle'])[1]['color'])
#
#     # Save plot limits
#     dataYLim = ax.get_ylim()
#
#     # Find best fit distribution
#     best_distibutions = best_fit_distribution(data, 200, ax)
#     best_dist = best_distibutions[0]
#     # print (best_dist[0], best_dist[1])
#
#     import time
#     start = time.time()
#     # Make PDF with best params
#     pdf = make_pdf(best_dist[3], best_dist[1])
#     end= time.time()
#     print ("st-end", end - start)
#     # matplotlib.pyplot.show()
#
#     if plot:
#         # Update plots
#         ax.set_ylim(dataYLim)
#         ax.set_title(title)
#         ax.set_xlabel(x_title)
#         ax.set_ylabel('Frequency')
#         # Display
#         plt.figure(figsize=(12, 8))
#         ax = pdf.plot(lw=2, label='PDF', legend=True)
#         data.plot(kind='hist', bins=50, density=True, alpha=0.5, label='Data', legend=True, ax=ax)
#         param_names = (best_dist[0].shapes + ', loc, scale').split(', ') if best_dist[0].shapes else ['loc', 'scale']
#         param_str = ', '.join(['{}={:0.2f}'.format(k, v) for k, v in zip(param_names, best_dist[1])])
#         dist_str = '{}({})'.format(best_dist[0].name, param_str)
#         five_bst_dist = []
#         for dist in best_distibutions[:5]:
#             param_names = (dist[0].shapes + ', loc, scale').split(', ') if best_dist[0].shapes else ['loc','scale']
#             param_str = ', '.join(['{}={:0.2f}'.format(k, v) for k, v in zip(param_names, best_dist[1])])
#             five_bst_dist.append('{}({})'.format(best_dist[0].name, param_str))
#
#
#         ax.set_title( title+'\n' + dist_str)
#         ax.set_xlabel(x_title)
#         ax.set_ylabel('Frequency')
#         # matplotlib.pyplot.show(block=False)
#         matplotlib.pyplot.show()
#     return pdf, dist_str, best_dist, five_bst_dist
#
# def init_read_worker_behavioral_data(filename="init_IPS.csv"):
#     """
#     Read behaviroal data for each trade worker
#     :param filename: this is the file name which contain timeline showing location of worker and duration in that location
#     :return: probablity distribution to go to specific zone and the probablity distribution of duration in that zone
#     """
#     # todo note that lower function here is made like spaghtti code... to be fixed
#     # todo when init the model generate behavioral files for each task/trade (let us say trade)
#     # todo add filter to the data to pick only relevant trade
#     # todo add filter to the data to pick only date range
#
#     project_directory = "ConPro/"
#     behavior_data_file = filename
#     # file_path = self.project_directory + behavior_data_file
#     file_path = project_directory + behavior_data_file
#     durations_dist = {}
#     df = pd.read_csv(file_path, sep=",")
#     resource_name = {
#         "A1":"plastering",
#         "A1 3rd delivery":"plastering",
#         "A1 and A2":"plastering",
#         "A2":"plastering",
#         "A2 3rd delivery":"plastering",
#         "АЗ":"plastering",
#         "A3 and A4":"plastering",
#         "A4":"plastering",
#         "A4 3rd delivery":"plastering",
#         "A5":"plastering",
#         "A6":"plastering",
#         "A6 3rd delivery":"plastering",
#         "A7":"plastering",
#         "A7 and A8":"painting",
#         "A8":"painting",
#         "A8 3rd delivery":"painting",
#         "bricklayer 1":"painting",
#         "bricklayer 2":"painting",
#         "carpenter 1":"painting",
#         "carpenter 2":"painting",
#         "foreman 1":"painting",
#         "foreman 2":"painting",
#         "General material":"painting",
#         "odd-job man":"painting",
#         "plasterer 1":"plastering",
#         "plasterer 2":"plastering",
#         "plasterer 3":"plastering",
#         "plumber 1":"plastering",
#         "plumber 2":"plastering"
#     }
#     df["Resource name"] = df["Resource name"].replace(resource_name)
#     print ("Resource name", df["Resource name"])
#     # Dictionary for replacement
#     gateways_zones = {0: 'Storage201', 32: 'A4', 33:"A4",35:"Elevator",
#                         36:"A7",37:"A6",38:"Storage204",39:"A8",40:"Corridor",
#                       41:"A3",42:"Staircase",43:"A5"}
#     # Replace values in the 'column_name' column using the dictionary
#     df['Gateway'] = df['Gateway'].replace(gateways_zones)
#     a = df.groupby('Gateway').count()
#     Activities_counts = df['Gateway'].value_counts()
#     Activities_counts_dic = dict(Activities_counts)
#     Activities_counts_dic_lower = {k.lower(): v for k, v in Activities_counts_dic.items()}  # lowercase the keys
#     total_inputs = sum(Activities_counts_dic_lower.values())
#     Activities_counts_dic_w = {key: value / total_inputs for (key, value) in Activities_counts_dic_lower.items()}
#     activities = [activity for activity in Activities_counts_dic_w if activity != ""]
#     wz = list(filter(lambda activity: bool(re.match(r'\b[A-Za-z]\d+\b', activity)), activities ))
#     nwz = list(filter(lambda activity: not bool(re.match(r'\b[A-Za-z]\d+\b', activity)), activities ))
#     Activities_counts_w_wz = [Activities_counts_dic_w[key] for key in wz]
#     Activities_counts_w_nwz = [Activities_counts_dic_w[key] for key in nwz]
#     p_wz = sum(Activities_counts_w_wz)
#     p_nwz = sum(Activities_counts_w_nwz)
#     presence = {"non_working_zone":p_nwz, "working_zone":p_wz}
#     # duration = datetime.strptime("1.00.31", '%H.%M.%S')
#     # total_seconds = duration.second + duration.minute * 60 + duration.hour * 3600
#
#     def convert_durations_to_seconds(input, string_format='%H.%M.%S'):
#         """
#         Take string of date time and convert it to datetime objects and then to seconds
#         :param input: string of date time 07.12.60
#         :param string_format: the format of the input string
#         :return: seconds which is converted from time (input)
#         """
#         duration = datetime.strptime(input, string_format)
#         total_seconds = duration.second + duration.minute * 60 + duration.hour * 3600
#         return total_seconds
#
#
#     # df['duration_seconds'] = df['Durations'].apply(convert_durations_to_seconds)
#     df['duration_seconds'] =  df['Durations'] * 60
#     for Activity in Activities_counts_dic.keys():
#         Work_Preparation = df[df["Gateway"] == Activity]
#         durations_dist[Activity.lower()] = list(Work_Preparation['duration_seconds'])
#     task_porb = Activities_counts_dic_w
#     durations_dist = durations_dist
#     # print (task_porb, durations_dist, activities)
#     return task_porb, durations_dist, activities
#
#
# if __name__ == "__main__":
#     import re
#     ignored_durations = 180
#     task_porb, durations_dist, activities = init_read_worker_behavioral_data()
#     activities = ['storage201', 'elevator', 'corridor', 'a4', 'a6', 'staircase', 'a3', 'a5', 'storage204', 'a8', 'a7']
#     wz = list(filter(lambda activity: bool(re.match(r'\b[A-Za-z]\d+\b', activity)), activities ))
#     nwz = list(filter(lambda activity: not bool(re.match(r'\b[A-Za-z]\d+\b', activity)), activities ))
#     wz_dist = [value for wz_key in wz for value in durations_dist[wz_key] if value < ignored_durations]
#     nwz_dist = [value for nwz_key in nwz  for value in durations_dist[nwz_key] if value < ignored_durations]
#     def get_current_path(target_file="config.ini"):
#         import os
#
#         # Get the current file's path
#         current_file_path = os.path.abspath(__file__)
#
#         # Determine the directory of the current file
#         current_directory = os.path.dirname(current_file_path)
#
#
#         # Construct the full path to the target file
#         file_path = os.path.join(current_directory, target_file)
#
#         # Print the contents of the file
#         return file_path
#
#     # Open and read the file
#     file_path = get_current_path(target_file="config.ini")
#     config.read(file_path, encoding='utf-8-sig')
#     print (config['pdf']['wz'])
#     if  config['pdf']['wz'] == "nothing":
#         pdf, dst_st,best_dist ,best_distibutions = get_pdfunc(wz_dist)
#         config['pdf']['wz'] = str(dst_st)
#         config['best_distibutions']['wz'] = str(best_distibutions)
#         pdf, dst_st,best_dist ,best_distibutions  = get_pdfunc(nwz_dist)
#         config['pdf']['nwz'] = str(dst_st)
#         config['best_distibutions']['nwz'] = str(best_distibutions)
#         with open(file_path, 'w') as configfile:
#             config.write(configfile)
#
#         # how many tasks can be started at the same time without finishing any?
#     # the probablity to go to other zone after entering specific zone
#     # more distinguish beteween different types of zone (not only wz, nonworking zone)
#     # a = eval('[(5,2), (10,  4)]')
#     # print (a)
#     # for x in a:
#     #     print (x)
#     # print("Hello, World!")
#     # generat_path_file()
#     # a = {"a":[4,5]}
#     # for list in a.values():
#     #     for n in list:
#     #         if n ==4:
#     #             list.remove(n)
#     # print (a)
#     # print ( 1 == 1 == 1 )
#
#
#
#     # print (durations_dist.keys())
#
#
# ########################################
#
#
# def pick_choice_pdfunc(pdfseries):
#     population = pdfseries.index
#     weights = pdfseries.values
#     print(choices(population, weights))
#     return choices(population, weights)[0]

# print (eval("(2,4,5)"))
# for i in range(0):
#     print("hi")
#     print (i)

a = 1

agents_attributes = {float:["imag"], int:["denominator", "imag"]}
agent_reporter = {
    type.__name__ + att: (a, type, att) for type,attributes_lists in agents_attributes.items() for att in attributes_lists
}
print (agent_reporter)
def get_attribute(agent, class_type, attribute):
    """
    For agent reporters in data collector
    return list of trade partners and None for other agents
    """
    if isinstance(agent, class_type):
        return getattr(agent,attribute)
    else:
        return None

get_attribute(a, int, "imag" )
# from operator import methodcaller
#
# import numpy as np
#
#
# func_list = ['conjugate']
# for func in func_list:
#     x = 2
#     f = methodcaller(func, x)
#     result = f(int)
#     print(result)

# att_to_print = [""]
# {
#                 "Trade": lambda a: get_trade(a, Worker, "trade"),
#             }