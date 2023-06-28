# import random
# # print(all([True, True]))
# # random.choice(range(1))
# print(all([0, 0 ]))
# # tasks_sequence = {1:["KEYSTART", "KEYFRAMES"], 2:["KEYMECH"]}
# # print ([task_key for sequence_key in tasks_sequence.keys() for task_key in tasks_sequence[sequence_key] ])
# def ala():
#     return 1,3 , 4
# print (ala())
#
# #
# import numpy as np
# import pandas as pd
# pd.set_option('display.max_rows', 1000)
# pd.set_option('display.max_columns', 1000)
# def generat_path_file(filename_iw="init_inner_walls.csv", filename_ew="init_external_walls.csv",output_filename="init_route.csv" ):
#     """
#     Read two files external waslls and internal walls and generate the route (grid file) on the basis of this two files
#     :param filename_iw: grid represent internal waslls file name IW mean interanl wall grid
#     :param filename_ew: grid represent extanal waslls file name W mean external wall grid
#     :return:
#     """
#     xymap_pd_iw = pd.read_csv("{}".format("ConPro/{}".format(filename_iw)), header=None)
#     xymap_pd_iw.reset_index()
#     xymap_pd_iw = xymap_pd_iw.set_axis(range(xymap_pd_iw.shape[0], 0, -1), axis='index')
#     xymap_pd_iw = xymap_pd_iw.applymap(str)
#     xymap_pd_ew = pd.read_csv("{}".format("ConPro/{}".format(filename_ew)), header=None)
#     xymap_pd_ew.reset_index()
#     xymap_pd_ew = xymap_pd_ew.set_axis(range(xymap_pd_ew.shape[0], 0, -1), axis='index')
#     xymap_pd_ew = xymap_pd_ew.applymap(str)
#     init_route = xymap_pd_iw.combine(xymap_pd_ew, np.maximum)
#     init_route = init_route.replace("0", 1)
#     init_route = init_route.replace("W", 0)
#     init_route = init_route.replace("IW", 0)
#     init_route = init_route.applymap(int)
#     init_route.to_csv("{}".format("ConPro/{}".format(output_filename)), index=False, header=False)



if __name__ == "__main__":
    # a = eval('[(5,2), (10,  4)]')
    # print (a)
    # for x in a:
    #     print (x)
    # print("Hello, World!")
    # generat_path_file()
    # a = {"a":[4,5]}
    # for list in a.values():
    #     for n in list:
    #         if n ==4:
    #             list.remove(n)
    # print (a)
    print ( 1 == 1 == 1 )
