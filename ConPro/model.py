
import numpy as np
import pandas as pd
import math
from statistics import mean
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
import mesa
from .agent_externalwall import ExternalWall
from .agent_innerwall import InnerWall
from .agent_route import Route
from .agent_worker import Worker
from .agent_drywall import Drywall
from .agent_zone import Zone
from .agent_zone_label import ZoneLabel
from .agent_dummy_drywall import DummyDrywall
from .init_read_tasks import read_csv, filter_cols, read_task

# Helper Functions
from datetime import datetime, time, timedelta
from copy import copy
import random
import os
# from .init_data_read_tasks import read_tasks

def generate_drywall_points(drywalls_points = [
        ]
):
    """
    create dry walls from dictionary
     input :
    drywalls_points = [
    [[34,33],[43,33], "D1"],
    [[43,33],[43,38], "D1"],
    # [[65,33],[65,38], "D2"],
    ]
    output:
{'D1': {(43, 33, 0), (34, 33, 0), (35, 33, 0), (38, 33, 0), (42, 33, 0), (39, 33, 0), (43, 34, 0),
(36, 33, 0), (43, 35, 0), (43, 36, 0), (40, 33, 0), (43, 37, 0), (37, 33, 0), (41, 33, 0), (43, 38, 0)},
'D2': {(43, 33, 0), (43, 34, 0), (43, 35, 0), (43, 36, 0), (43, 37, 0), (43, 38, 0)}}
    :param points:
    :return:
    """
    result = {}
    for line in drywalls_points:
        st, end, key = line[0], line[1], line[2]  # [34,33],[43,33]
        created_grids = result.get(key, set())
        index_to_increase = 1 if st[0] == end[0] else 0
        range_list = range(min(st[index_to_increase], end[index_to_increase]),
                           max(st[index_to_increase], end[index_to_increase]) + 1)
        grids = [[st[0], y] for y in range_list] if index_to_increase else [[x, st[1]] for x in range_list]
        for grid in grids:
            created_grids.add(tuple(grid))
        result[key] = created_grids
    return result

def flatten(list_of_lists):
    """
    helper function for model datacollector for trade price
    collapses agent price list into one list
    """
    return [item for sublist in list_of_lists for item in sublist]

def geometric_mean(list_of_prices):
    """
    find the geometric mean of a list of prices
    """
    return np.exp(np.log(list_of_prices).mean())

def get_trade(agent):
    """
    For agent reporters in data collector
    return list of trade partners and None for other agents
    """
    if isinstance(agent, Worker):
        return agent.trade
    else:
        return None

def get_utilization(model):
    """
    get utilizations of workers
    return list of trade partners and None for other agents
    """
    ut = [worker.utilization for workers_list in model.workers_agents.values() for worker in workers_list]
    if ut:
        return mean(ut)

def get_left(model, key):
    """
    get the amount of work left for each task
    :param model: 
    :return: 
    """
    amount_left = []
    tasks_keys = flatten(model.tasks_sequence.values())
    for drywalls_list in model.drywalls_agents.values():
        for drywall in drywalls_list:
            if key in  tasks_keys:
                amount_left.append(drywall.tasks[key]['amount'])
    return sum(amount_left)
    
def get_idle(model):
    """
    For agent reporters in data collector
    return list of trade partners and None for other agents
    """
    idle = [worker.idle_percentage for workers_list in model.workers_agents.values() for worker in workers_list]
    if idle:
        return mean(idle)

# add to template
# self.grid._remove_agent(agent.pos, agent)#remove the agent from the grid of the model
# self.schedule.remove(agent)#remove the agent from the schedule of the model
#todo: is there a way to get the agent by calling its unique id check scheduler ?
#todo: worker bheavior
#todo: tasks call worker, worker assgined to task
#todo: trade time to finnish (avg_production_rate(keytask)/total_work(keytask)_left)
#todo: trade utilization

class ConPro(mesa.Model):
    """
    Agent-based simulation model for construction processes
    """
    project_directory = "ConPro/"
    x_init_worker = 10
    y_init_worker = 2
    weekdays = { 0:"Monday",1:"Tuesday", 2:"Wednesday", 3:"Thursday",4:"Friday",5:"Saturday",6:"Sunday"}
    grids_size = 16  # 16 grids per square meter
    trades_tasks_keys = {'KEYSTART': ["plastering"], 'KEYFRAMES': ["painting"], 'KEYMECH': ["plastering"],
                    'KEYELEC': ["painting"],
                    'KEYINSU': ["plastering"], 'KEYSTUD': ["painting"], 'KEYPAINTING': ["plastering"],
                    'KEYFINISHING': ["painting"], 'KEYEND': ["plastering"]}
    colors = {"plastering": "green", "painting": "red"}

    def __init__(
        self,
        # new
        seed=random.randrange(4294967294),
        project_startdate=datetime(2021, 12, 31, 7, 0, 0, 0),
        simulation_startdate=datetime(2022, 5, 16, 6, 0, 0, 0),  # site B (2021, 10, 11), site A electrician 2022-05-16
        simulation_speed_microsec=1500000,  # 1500000 1.5sec # 15000000 15 sec
        start_day=800,
        start_hour=6,
        workingday_minutes=510,
        coffe_break_start=540,
        coffe_break_start_min=520,
        coffe_break_start_max=570,
        coffe_break2_start=840,
        coffe_break2_start_min=820,
        coffe_break2_start_max=870,
        coffe_break_duration=12,
        coffe_break_duration_min=10,
        coffe_break_duration_max=30,
        smoke_duration=10,
        smoke_duration_min=5,
        smoke_duration_max=15,
        lunchbox_duration=6,
        lunchbox_duration_min=3,
        lunchbox_duration_max=10,
        lunch_break_start=660,
        lunch_break_start_max=690,
        lunch_break_start_min=630,
        picking_material_duration=15,
        picking_material_duration_min=10,
        picking_material_duration_max=35,
        break_duration=15,
        break_duration_min=5,
        break_duration_max=30,
        lunch_break_duration=30,
        lunch_break_duration_min=25,
        lunch_break_duration_max=45,
        wc_duration=10,
        wc_duration_max=20,
        wc_duration_min=7,
        arrival_time_mode=420,
        arrival_time_min=450,  # 390
        arrival_time_max=390,
        leave_time_mode=900,
        leave_time_min=870,
        leave_time_max=930,
        running_steps=100000,
        running=True,
        # end new
        width=132, # width of csv grid files
        height=132, # height of csv grid files,
        n_plastering_workers=1,
        n_painting_workers=1,
        behavior_files=None,
            
    ##########
    #
    #varaiables to change
    #
    ##########
        one_zone_one_trade=False,
        zone_max_worker=1,
        zone_max_trades=1,
        zone_max_visitor=10000,
        KEYSTART_max=2,
        KEYFRAMES_max=2,
        KEYMECH_max=2,
        KEYELEC_max=2,
        KEYINSU_max=2,
        KEYSTUD_max=2,
        KEYPAINTING_max=2,
        KEYFINISHING_max=2,
        KEYEND_max=2,
        drywall_max_workers=10000000000000,
        work_duration=1,
        work_duration_min=0.5,
        work_duration_max=1.2,
        drywalls_points=None,
            # trades_tasks=None,
        tasks_sequence=None,
        palstering_worker_skills=None,
        painting_worker_skills=None,
        one_behavior_file=True,
        dwwz=None
    ):
        if dwwz is None:
            dwwz = list()
        if palstering_worker_skills is None:
            palstering_worker_skills = {"KEYMECH": 100, "KEYSTART": 100, "KEYINSU": 100, "KEYPAINTING": 100, "KEYEND": 100}

        if painting_worker_skills is None:
            painting_worker_skills = {"KEYFRAMES": 200, "KEYELEC": 200, "KEYSTUD": 150, "KEYFINISHING": 122}
        # if trades_tasks is None:
        #     trades_tasks = {'KEYSTART': ["plastering"], 'KEYFRAMES': ["painting"], 'KEYMECH': ["plastering"], 'KEYELEC': ["painting"],
        #      'KEYINSU': ["plastering"], 'KEYSTUD': ["painting"], 'KEYPAINTING': ["plastering"],
        #      'KEYFINISHING': ["painting"], 'KEYEND': ["plastering"]}

        self.one_behavior_file = one_behavior_file
        if behavior_files is None and self.one_behavior_file:
            behavior_files = { key:"init_behavior_file.csv".format(key) for key in self.trades_tasks_keys.keys()}
        else:
            behavior_files = {key: "init_behavior_file_{key}.csv".format(key) in self.trades_tasks_keys.keys()}
        if tasks_sequence is None:
            tasks_sequence = {1: ["KEYSTART", "KEYFRAMES"], 2: ['KEYMECH'], 3: ['KEYELEC'], 4: ["KEYINSU"], 5: ["KEYSTUD"],6: ["KEYPAINTING"], 7: ["KEYFINISHING"], 8: ["KEYEND"]}
            # tasks_sequence = {1:["KEYSTART", "KEYFRAMES"]}#{1:["KEYSTART", "KEYFRAMES"], 2:['KEYMECH'], 3:['KEYELEC']} # , 2:['KEYMECH'], 3:['KEYELEC'], 4:["KEYINSU"],5:["KEYSTUD"], 6:["KEYPAINTING"], 7:["KEYFINISHING"], 8:["KEYEND"]}
        if drywalls_points is None:
            drywalls_points=[
                # [[3,118],[19,118], "dry_wall5"],
                # [[19,119],[19,127], "dry_wall5"],
                [[11, 11], [2, 11], "dry_wall4"],
                [[12, 10], [15, 10], "dry_wall1"],
                #  [[43,33],[43,38], "dry_wall7"]
                [[2, 23], [12, 23], "dry_wall3"],
                [[12, 11], [12, 22], "dry_wall3"]]
        # self.trades_tasks = trades_tasks
        self.dwwz = dwwz # drywall_working_zones
        print ("self.dwwz", self.dwwz)
        self.painting_worker_skills = painting_worker_skills
        self.palstering_worker_skills = palstering_worker_skills
        self.behavior_files = behavior_files
        self.tasks_sequence = tasks_sequence
        self.completed_drywalls = 0
        self.grids_per_meter = 8
        self.max_task_workers ={'KEYSTART':KEYSTART_max , 'KEYFRAMES':KEYFRAMES_max , 'KEYMECH':KEYMECH_max ,
                          'KEYELEC': KEYELEC_max,
                          'KEYINSU':KEYINSU_max , 'KEYSTUD':KEYSTUD_max , 'KEYPAINTING':KEYPAINTING_max ,
                          'KEYFINISHING':KEYFINISHING_max , 'KEYEND':KEYEND_max}
        self.zone_max_worker = zone_max_worker
        self.zone_max_trades = zone_max_trades
        self.zone_max_visitor = zone_max_visitor
        self.drywall_max_workers = drywall_max_workers
        self.one_zone_one_trade = one_zone_one_trade
        self.current_id = 0
        self.xymap_changed = True
        self.task_id = 1
        # production rate KEYMECH is measured in u/h.
        self.workers = {
                      "plastering":{"n":n_plastering_workers,"production_rate":palstering_worker_skills,
                                    "behavior_files":behavior_files, 'color':self.colors["plastering"]},
                      "painting":{"n":n_painting_workers, "production_rate":painting_worker_skills,
                                  "behavior_files":behavior_files,
                                  "color":self.colors["painting"]},
                      }
        self.passed_working_time = start_day
        self.width = width
        self.height = height
        self.running = True
        self.agent_id = 0
        self.drywalls_points = drywalls_points
        self.today = simulation_startdate.day
        self.start_hour = start_hour
        self.status = "before working hours"
        self.project_startdate = project_startdate
        self.simulation_startdate = simulation_startdate
        self.current_datetime = simulation_startdate
        self.today_minutes = 0
        self.running = running
        self.start_day = start_day
        self.workingday_minutes = workingday_minutes  # working minutes in one day
        self.this_day_start_date = datetime(simulation_startdate.year, simulation_startdate.month, simulation_startdate.day, 0 ,0 ,0 )
        self.this_week = str(simulation_startdate.year)+"-"+str(simulation_startdate.isocalendar()[1])
        self.this_date = str(simulation_startdate.year)+"-"+str(simulation_startdate.isocalendar()[1])+"-"+self.dayNumber_to_Text(simulation_startdate.weekday())
        self._seed = random.randrange(4294967294)
        np.random.seed(self._seed)## set numpy to have the same seed like the model        project_startdate = datetime(2021, 12, 31, 7, 0, 0, 0),
        self.simulation_speed_microsec = simulation_speed_microsec  # 1500000 #1.5sec
        self.simulation_speed_sec = self.simulation_speed_microsec/1000000
        self.simulation_speed_min = self.simulation_speed_sec/60
        self.simulation_speed_h = self.simulation_speed_sec / 24
        self.wc_duration = wc_duration
        self.wc_duration_max = wc_duration_max
        self.wc_duration_min = wc_duration_min
        self.picking_material_duration = picking_material_duration
        self.picking_material_duration_max = picking_material_duration_max
        self.picking_material_duration_min = picking_material_duration_min
        self.smoke_duration = smoke_duration
        self.smoke_duration_min = smoke_duration_min
        self.smoke_duration_max = smoke_duration_max
        self.break_duration = break_duration
        self.break_duration_min = break_duration_min
        self.break_duration_max = break_duration_max
        self.work_duration = work_duration
        self.work_duration_min = work_duration_min
        self.work_duration_max = work_duration_max
        self.arrival_time_mode = arrival_time_mode
        self.arrival_time_max = arrival_time_max
        self.arrival_time_min = arrival_time_min
        self.lunch_break_duration = lunch_break_duration
        self.lunch_break_duration_min = lunch_break_duration_min
        self.lunch_break_duration_max = lunch_break_duration_max
        self.coffe_break_duration = coffe_break_duration
        self.coffe_break_duration_min = coffe_break_duration_min
        self.coffe_break_duration_max = coffe_break_duration_max
        self.coffe_break_start = coffe_break_start
        self.coffe_break_start_min = coffe_break_start_min
        self.coffe_break_start_max = coffe_break_start_max
        self.coffe_break2_start = coffe_break2_start
        self.coffe_break2_start_min = coffe_break2_start_min
        self.coffe_break2_start_max = coffe_break2_start_max
        self.lunch_break_start = lunch_break_start
        self.lunch_break_start_min = lunch_break_start_min
        self.lunch_break_start_max = lunch_break_start_max
        self.lunchbox_duration = lunchbox_duration
        self.lunchbox_duration_min = lunchbox_duration_min
        self.lunchbox_duration_max = lunchbox_duration_max
        self.leave_time_mode = leave_time_mode
        self.leave_time_max = leave_time_max
        self.leave_time_min = leave_time_min
        self.running_steps = running_steps
        self.zones = set()
        self.zones_colors = dict()
        self.visit_BR_first = False
        self.arrival_zone_name = "elevator"
        self.break_zone_name = "staircase"
        # initiate activation schedule
        self.schedule = mesa.time.RandomActivationByType(self)
        # initiate mesa grid class
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=False)
        # initiate datacollector
        self.workers_agents = dict() # {"plastering": [], "painting":[]} -> {trade:[workers]}
        self.drywalls_agents = dict() # {"dry_wall1":[], "dry_wall2":} -> {}
        self.dummy_drywalls_agents = dict()
        self.zones_agents = dict() #{"cooridor":[], "storage202":[]} -> {zone_name:[agents]}
        self.available_tasks = dict() # {"KEYMECH":[dry_wall1, dry_wall2]} # added by drywall object
        self.not_available_tasks = dict()
        self.available_workers = self.workers_agents.copy()
        self.tasks_stats = dict() # {"KEYMECH":{"total_amount":142, "completed_amount":50, "avg_production_rate":543(u/h)}}
        self.number_of_drywalls = 0
        self.drywalls_in_zone = dict()
        self.get_status()
        self.time_jump()
        self.set_zone_max_workers()
        
        #
        #Intitialize/create intitial agents from grid files csv
        #
        self.init_agents()
        self.init_read_worker_behavioral_data()
        self.determine_scenario_name()
        # self.print_object_attributes(self) # model
        # self.print_object_attributes(list(self.workers_agents.values())[0][0])  # model
        # self.print_object_attributes(list(self.drywalls_agents.values())[0][0])  # model

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "get_seed": lambda m: ConPro.get_seed(m),
                "Worker": lambda m: m.schedule.get_type_count(Worker),
                "Utilization": lambda m: get_utilization(m),
                "Idle": lambda m: get_idle(m),
                "KEYSTART": lambda m: get_left(m, "KEYSTART"),
                "KEYFRAMES": lambda m: get_left(m, "KEYFRAMES"),
                "KEYMECH": lambda m: get_left(m, "KEYMECH"),
                "KEYELEC": lambda m: get_left(m, "KEYELEC"),
                "KEYINSU": lambda m: get_left(m, "KEYINSU"),
                "KEYSTUD": lambda m: get_left(m, "KEYSTUD"),
                "KEYPAINTING": lambda m: get_left(m, "KEYPAINTING"),
                "KEYFINISHING": lambda m: get_left(m, "KEYFINISHING"),
                "KEYEND": lambda m: get_left(m, "KEYEND"),
                "scenario":lambda m: m.scenario,
                "completed_in":lambda m:m.schedule.steps
            },
            agent_reporters={
                "Trade": lambda a: get_trade(a)
            }
        )

    def is_route_file_generated(self, filename="init_route.csv"):
        """
        chek if the route file is already generated
        :return:
        """
        # print (output_path)
        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, "ConPro",filename)
        #    print (final_directory, os.path.exists(final_directory))
        if os.path.isfile(final_directory):
            return True
        else:
            return False

    def set_zone_max_workers(self):
        """
        zone max workers should be related to the tasks max worker
        :return:
        """
        self.zone_max_worker = max(self.max_task_workers.values())

    def is_task_pickable(self, task):
        """
        check if the task_key that assgined as avialbe by drywall can be considered avaialbe based on constrainets
        :return:
        """
        task["constraints"] = set()
        zone = self.zones_agents[task["zone_name"]][0]
        drywall = self.drywalls_agents[task["drywall"]][0]
        if zone.is_trades_full() or zone.is_workers_full() or zone.is_visitors_full():
            task["constraints"].add("zone")
            # # remove all drywalls in this zone from avaialbe
            # print("availabe tasks", self.available_tasks, self.available_tasks[self.selected_task_key])
            # self.remove_zone_works(zone.name)
            # print("availabe tasks, after", self.available_tasks,
            #       self.available_tasks[self.selected_task_key])
        if drywall.is_drywall_max_n_worker():  #
            # remove this drywall from availabe
            task["constraints"].add("drywall")
            # self.remove_drywall(drywall.name)
        if drywall.is_task_max_n_worker(task):
            task["constraints"].add("task")
        if task["constraints"]:
            # print (task["task_id"],"task is not pickable", task["constraints"], task)
            return False
        else:
            task["constraints"] = set()
            return task
            # self.remove_task(self.selected_task_key, self.task_index)

    def is_occupied(model, pos=(0, 0), occupants_number=4):
        """
        determine if the cell is occupied by more than specific number of agents
        :param model:
        :param pos:
        :param occupants_number:
        :return:
        """
        this_cell = model.grid.get_cell_list_contents([pos])
        return len(this_cell) >= occupants_number

    def move_agent(self, pos):
        """
        Move agent from to the pos
        :param pos: x, y position to move agent to
        """
        self.model.grid.move_agent(self, pos)

    def print_object_attributes(self, object):
        """
        This can be used to see the content of each object/agent for testing porpuses mainly when intialization
        :param object: the object that you want to print all the attributes for
        """
        print(len(dir(object)) - 25)
        # for attribute in dir(object):
        #     print(attribute, getattr(object, attribute))

    def is_value_close(self, value, value1, rel_to=1e-02):
        """
        compare two float values and consider them equal if they are close enough
        :param value: float value
        :param value1: float value1
        :param rel_to: to which decimal point
        :return: true if values are close
        """
        return math.isclose(value, value1, rel_tol=rel_to)

    def init_read_worker_behavioral_data(self, filename="init_behavior_file.csv"):
        """
        Read behaviroal data for each trade worker
        :param filename: this is the file name which contain timeline showing location of worker and duration in that location
        :return: probablity distribution to go to specific zone and the probablity distribution of duration in that zone
        """
        #todo note that lower function here is made like spaghtti code... to be fixed
        behavior_data_file = filename
        file_path = self.project_directory + behavior_data_file
        durations_dist = {}
        df = pd.read_csv(file_path, sep=",")
        a = df.groupby('Activity Classification').count()
        Activities_counts = df['Activity Classification'].value_counts()
        Activities_counts_dic = dict(Activities_counts)
        Activities_counts_dic_lower = {k.lower(): v for k, v in Activities_counts_dic.items()} # lowercase the keys
        total_inputs = sum(Activities_counts_dic_lower.values())
        Activities_counts_dic_w = {key: value / total_inputs for (key, value) in Activities_counts_dic_lower.items()}
        # duration = datetime.strptime("1.00.31", '%H.%M.%S')
        # total_seconds = duration.second + duration.minute * 60 + duration.hour * 3600

        def convert_durations_to_seconds(input, string_format='%H.%M.%S'):
            """
            Take string of date time and convert it to datetime objects and then to seconds
            :param input: string of date time 07.12.60
            :param string_format: the format of the input string
            :return: seconds which is converted from time (input)
            """
            duration = datetime.strptime(input, string_format)
            total_seconds = duration.second + duration.minute * 60 + duration.hour * 3600
            return total_seconds

        df['duration_seconds'] = df['Duration'].apply(convert_durations_to_seconds)
        for Activity in Activities_counts_dic.keys():
            Work_Preparation = df[df["Activity Classification"] == Activity]
            durations_dist[Activity.lower()] = list(Work_Preparation['duration_seconds'])
        task_porb = Activities_counts_dic_w
        durations_dist = durations_dist
        activities = [activity for activity in Activities_counts_dic_w if activity != ""]
        return task_porb, durations_dist, activities

    def init_agents(self):
        """
        Initialize all agents that are used in this simulatin
        :param :
        :return:
        """
        if not self.is_route_file_generated():
            self.generat_path_file()
        self.init_external_wall_agents()
        self.init_inner_wall_agents()
        self.init_path()
        self.init_zones_agents()
        # self.init_route_agents()
        self.init_xymap()
        self.init_worker_agents()
        self.intit_drywalls()
        self.init_zones_labels_agents()

    def init_worker_agents(self, filename="init_behavior_file.csv" ):
        """
        intialize/create workers agents
        :param filename: text file represent grids contain type of wall in each grid
        :return:
        """
        for worker_type, worker_info in self.workers.items():
            for n_workers in range(worker_info['n']):
                x, y = self.x_init_worker, self.y_init_worker
                # production rate is given in u/h
                production_rate_step = {key:production_rate*self.simulation_speed_h for key, production_rate in worker_info["production_rate"].items()}
                worker = Worker(self.agent_id, self, (x, y), trade=worker_type,  production_rate=production_rate_step,
                                behavior_files=worker_info["behavior_files"], color=worker_info["color"], arrival=0 )
                behaviors_by_key = dict()
                for key in worker_info["behavior_files"].keys():
                    task_porb, durations_dist, activities = self.init_read_worker_behavioral_data(worker_info["behavior_files"][key])
                    behaviors_by_key[key] = {"task_porb":task_porb, "durations_dist":durations_dist, "activities":activities}
                worker.behaviors_by_key = behaviors_by_key
                # print ("worker_behaviors_by_key", behaviors_by_key)
                # worker.task_porb, worker.durations_dist, worker.activities = self.init_read_worker_behavioral_data(worker_info["behavior_file"])
                self.add_agent(worker, worker.pos) # to grid and scheduale
                # add workers to dictionary to keep track of them, access them
                self.workers_agents[worker_type] = self.workers_agents.get(worker_type, [])
                self.workers_agents[worker_type].append(worker)

    def intit_drywalls(self):
        """
        create drywalls grids agents
        :return:
        """
        #todo: add task id, attribute if task aquired
        drywalls_lines = generate_drywall_points(self.drywalls_points)
        filename = "init_tasks_comma.csv"
        df = read_csv(filename="ConPro/{}".format(filename))
        df = df.set_index('task_name')
        cols = filter_cols(df, filter_key="KEY")
        for name, points in drywalls_lines.items():
            for index, point in enumerate(points):
                zone = df.loc[name, "zone"].lower()
                zone_pos = self.zones_agents[zone][0].pos
                tasks={key: {} for key in cols}
                for phase in cols:
                    print(self.dwwz, "lksjdflksdfj")
                    tasks[phase]["amount"] = df.loc[name, phase]
                    tasks[phase]["start_date"] = df.loc[name, "start_date"]
                    tasks[phase]["end_date"] = df.loc[name, "end_date"]
                    tasks[phase]["task_id"] = self.task_id
                    tasks[phase]["drywall_id"] = self.agent_id
                    tasks[phase]["aquired"] = False
                    tasks[phase]["pos"] = point
                    tasks[phase]["drywall"] = name
                    tasks[phase]["finished"] = False
                    tasks[phase]["zone_name"] = zone
                    tasks[phase]["zone_pos"] = zone_pos
                    tasks[phase]["phase_key"] = phase
                    tasks[phase]["max_n_worker"] = self.max_task_workers[phase] #todo: determine max number of woerks for each tasks
                    tasks[phase]["n_worker"] = 0 #todo: determine max number of woerks for each tasks
                    tasks[phase]["status"] = "pickable"
                    tasks[phase]["constraints"] = set()
                    self.task_id += 1
                if index == 0:#create only one grid for drywall other grids are dummy drywalls (copy the state of the drywall)

                    drywall = Drywall(self.agent_id, self, pos=point, name=name, tasks=tasks, zone=zone, hasStarted=False, current_workers=set())
                    self.add_agent(drywall, drywall.pos)
                    # self.update_xymap(drywall.pos, value=0)
                    # keep track of dry_walls in the model
                    self.drywalls_agents[name] = self.drywalls_agents.get(name, [])
                    self.drywalls_agents[name].append(drywall)
                    # each drywall is considered a smaller zone/space inside a bigger zone (tack area)
                    # self.drywalls_in_zone[name] = self.drywalls_by_zone.get(name, set())
                    # self.drywalls_in_zone[name].add()
                    parent_zone = self.zones_agents[zone][0]
                    zone = Zone(self.agent_id, self, pos=point, name=name, parent_zone=parent_zone)
                    self.add_agent(zone, zone.pos)
                    self.zones.add(name)
                    # keep track of zones in the model
                    self.zones_agents[name] = self.zones_agents.get(name, [])
                    self.zones_agents[name].append(zone)
                    self.number_of_drywalls += 1
                    self.dwwz.append(parent_zone.name)
                    parent_zone.working_zone = True
                    print (self.dwwz, "self.dwwz")
                else:
                    dummy_drywall = DummyDrywall(self.agent_id, self, pos=point,  drywall=drywall, name=name)
                    self.add_agent(dummy_drywall, dummy_drywall.pos)
                    # self.update_xymap(dummy_drywall.pos, value=0)
                    # keep track of dry_walls in the model
                    self.dummy_drywalls_agents[name] = self.dummy_drywalls_agents.get(name, [])
                    self.dummy_drywalls_agents[name].append(dummy_drywall)

    def add_agent(self, agent, pos=(0,0)):
        """
        add agent to the grid
        :param agent: object of type agent
        :param pos: position on the grid to agent on
        :return:
        """
        self.schedule.add(agent)
        self.grid.place_agent(agent, pos)
        self.agent_id = self.next_id()

    def get_neighbors(self, pos=(0,0), moore=True, include_center=True, radius=1 ):
        """
        add agent to the grid
        :param pos: object of type agent
        :param moore: If True, return Moore neighborhood (including diagonals) else If False, return Von Neumann neighborhood
        :param radius: radius: radius, in cells, of neighborhood to get. One mean look one cell away
        :return: list of positions of neighbors cell
        """
        neighbors = [ i for i in self.grid.get_neighborhood(pos, moore, include_center, radius)]

    def get_unoccupied_neighbors(self, pos=(0,0), moore=True, include_center=True, radius=1):
        """
        add agent to the grid
        :param pos: object of type agent
        :param moore: If True, return Moore neighborhood (including diagonals) else If False, return Von Neumann neighborhood
        :param radius: radius: radius, in cells, of neighborhood to get. One mean look one cell away
        :return: list of positions of unoccupied neighbors cell
        """
        neighbors = [i for i in self.grid.get_neighborhood(pos, moore, include_center, radius) if not self.is_occupied(i)]

    def remove_agent(self, agent, pos=(0,0)):
        """
        remove agent from the grid
        :param agent: object of type agent
        :param pos: position on the grid to agent on
        :return:
        """
        self.grid.remove_agent(agent.pos, agent) #remove the agent from the grid of the model
        self.schedule.remove(agent) #remove the agent from the schedule of the model

    def to_findpatharrayxy(self, x, y):
        """"
         fix the grid from array (y, x) start and positive y pointing down to mesa grid coordination system (x, y) and y pointing up
        :param x: x coordinate of the position (integer)
        :param y: y coordinate of the position (integer)
        :return: grid point (1, 100) become ( 0, 1 ) if the height of the girds is 100        :param x: x coordinate of the position (integer)
        :param y: y coordinate of the position (integer)
        :return: position with y=0 is on the left top (positive y pointing down)
        """
        return (x, self.height-1-y)

    def to_arrayxy(self, pos=(0, 0)):
        """"
        fix the grid from mesa grid which start in the left-bottom corner to array which 1. switch x and y (x=0, y=1) become ( something, x=0 )
        and 2. start from top left corner so something is grid height-1-y in other words
        fix the grid from mesa grid coordination system (x, y) and y pointing up to array (y, x) start and positive y pointing down
        :param x: x coordinate of the position (integer)
        :param y: y coordinate of the position (integer)
        :return: grid point (1, 100) become ( 0, 1 ) if the height of the girds is 100
        """
        return (self.height-1-pos[1], pos[0])

    def generate_random_color(self):
        """
        generate random color
        :return: random color
        """
        hexadecimal = ["#" + ''.join([self.random.choice('ABCDEF0123456789') for i in range(6)])]
        return hexadecimal[0]

    def init_zones_agents(self, filename="init_zones.csv" ):
        """
        intialize/creat zone agents
        :param filename: text file represent grids contain type of zone in each grid
        :return:
        """
        # read in landscape file from supplmentary material
        zone_key = np.genfromtxt("ConPro/{}".format(filename), delimiter=",", dtype="|U10")
        ##########
        #
        # in numpy y come first and x come after [[1,2],[2,4]]. and y start from up, unlike mesa from down
        #
        ###########
        max_array_x = zone_key.shape[1]
        max_arry_y = zone_key.shape[0]
        for _, x, y in self.grid.coord_iter():
            if x < max_array_x and y < max_arry_y:
                cell_content = zone_key[self.height-1-y, x].lower()
                if cell_content!= "0":
                    cell_content = cell_content.lower()
                    zone = Zone(self.agent_id, self, (x, y), name=cell_content)
                    self.add_agent(zone, zone.pos)
                    self.zones.add(cell_content)
                    # keep track of zones in the model
                    self.zones_agents[cell_content] = self.zones_agents.get(cell_content, [])
                    self.zones_agents[cell_content].append(zone)

    def init_zones_labels_agents(self, filename="init_zones.csv"):
        """
        intialize/creat zone labels agents
        :param filename: text file represent grids contain type of zone in each grid
        :return:
        """
        # read in landscape file from supplmentary material
        zone_key = np.genfromtxt("ConPro/{}".format(filename), delimiter=",", dtype="|U10")
        ##########
        #
        # in numpy y come first and x come after [[1,2],[2,4]]. and y start from up, unlike mesa from down
        #
        ###########
        max_array_x = zone_key.shape[1]
        max_arry_y = zone_key.shape[0]
        for _, x, y in self.grid.coord_iter():
            if x < max_array_x and y < max_arry_y:
                cell_content = zone_key[self.height - 1 - y, x].lower()
                if cell_content != "0":
                    cell_content = cell_content.lower()
                    zone_label = ZoneLabel(self.agent_id, self, (x-1, y), name=cell_content)
                    self.add_agent(zone_label, zone_label.pos)
                    # keep track of zones in the model
                    self.zones_agents[cell_content] = self.zones_agents.get(cell_content, [])
                    self.zones_agents[cell_content].append(zone_label)

    def print_new_zones_colors(self, zones):
        """
        used to print random colors for each zone (use it once and paste the generated dictioary to zone agent)
        :param zones: set containing the names of the zones
        """
        zones_colors = {zone:self.generate_random_color() for zone in self.zones}


    def init_external_wall_agents(self, filename="init_external_walls.csv" ):
        """
        intialize/creat wall agents
        :param filename: text file represent grids contain type of wall in each grid
        :return:
        """
        # read in landscape file from supplmentary material
        wall_key = np.genfromtxt("ConPro/{}".format(filename), delimiter=",", dtype="|U5")
        ##########
        #
        # in numpy y come first and x come after [[1,2],[2,4]]. and y start from up, unlike mesa from down
        #
        ###########
        max_array_x = wall_key.shape[1]
        max_arry_y = wall_key.shape[0]

        for _, x, y in self.grid.coord_iter():
            if x < max_array_x and y < max_arry_y:
                wall = wall_key[self.height-1-y, x]
                if wall=="W":
                    wall = ExternalWall(self.agent_id, self, (x, y))
                    self.add_agent(wall, wall.pos)

    def init_xymap(self, filename="init_route.csv"):
        """
        Generate pandas grid and set index axis (y) to reverse the indexes (last row index/y = 0)
        :param filename:
        :return:
        """
        self.xymap_pd = pd.read_csv("{}".format("ConPro/{}".format(filename)), header=None)
        self.xymap_pd.reset_index()
        self.xymap_pd = self.xymap_pd.set_axis(range(self.xymap_pd.shape[0], 0, -1), axis='index')

    def generat_path_file(self, filename_iw="init_inner_walls.csv", filename_ew="init_external_walls.csv",
                          output_filename="init_route.csv"):
        """
        Read two files external waslls and internal walls and generate the route (grid file) on the basis of this two files
        :param filename_iw: grid represent internal waslls file name IW mean interanl wall grid
        :param filename_ew: grid represent extanal waslls file name W mean external wall grid
        :return:
        """
        xymap_pd_iw = pd.read_csv("{}".format("ConPro/{}".format(filename_iw)), header=None)
        xymap_pd_iw.reset_index()
        xymap_pd_iw = xymap_pd_iw.set_axis(range(xymap_pd_iw.shape[0], 0, -1), axis='index')
        xymap_pd_iw = xymap_pd_iw.applymap(str)
        xymap_pd_ew = pd.read_csv("{}".format("ConPro/{}".format(filename_ew)), header=None)
        xymap_pd_ew.reset_index()
        xymap_pd_ew = xymap_pd_ew.set_axis(range(xymap_pd_ew.shape[0], 0, -1), axis='index')
        xymap_pd_ew = xymap_pd_ew.applymap(str)
        init_route = xymap_pd_iw.combine(xymap_pd_ew, np.maximum)
        init_route = init_route.replace("0", 1)
        init_route = init_route.replace("W", 0)
        init_route = init_route.replace("I", 0)
        init_route = init_route.applymap(int)
        init_route.to_csv("{}".format("ConPro/{}".format(output_filename)), index=False, header=False)
        # self.init_route=init_route.to_csv(index=False, header=False)
        # print(self.init_route)

    def init_path(self, filename="init_route.csv" ):
        """
        Initialize path created in init_route.csv 1 is wall and 0 is path
        :return:
        """
        # read in the map file from supplmentary material
        self.xymap_arr = np.genfromtxt("ConPro/{}".format(filename), delimiter=",", dtype="|U5")
        # self.xymap_arr = np.genfromtxt(self.init_route, delimiter=",", dtype="|U5")



    def update_xymap(self, pos=(0, 0), value=1):
        """
        Add or remove obstacle to the map
        :param pos: the position where to change the value
        :param value: the value of the cell in that position
        """
        pos = self.to_arrayxy(pos)
        self.xymap_arr [pos[0], pos[1]] = value
        self.xymap_changed = True

    def init_route_agents(self):
        """
        intialize/creat route agents
        :param filename: text file represent grids contain type of wall in each grid
        :return:xymap_arr: numpy array that contain the path grids. grid value 0 mean
        the more the value above 1 the more the importance of this grid in finding path
        """

        ##########
        #
        # in numpy y come first and x come after [[1,2],[2,4]]. and y start from up, unlike mesa from down
        #
        ###########
        for _, x, y in self.grid.coord_iter():
            wall = self.xymap_arr[self.height-1-y, x]
            if wall=="1":
                wall = Route(self.agent_id, self, (x, y))
                self.add_agent(wall, wall.pos)

    def init_inner_wall_agents(self, filename="init_inner_walls.csv" ):
        """
        intialize/creat wall agents
        :param filename: text file represent grids contain type of wall in each grid
        :return:
        """
        # read in landscape file from supplmentary material
        wall_key = np.genfromtxt("ConPro/{}".format(filename), delimiter=",", dtype="|U5")
        ##########
        #
        # in numpy y come first and x come after [[1,2],[2,4]]. and y start from up, unlike mesa from down
        #
        ###########
        max_array_x = wall_key.shape[1]
        max_arry_y = wall_key.shape[0]
        for _, x, y in self.grid.coord_iter():
            if x < max_array_x and y < max_arry_y:
                wall = wall_key[self.height-1-y, x]
                if wall=="I":
                    wall = InnerWall(self.agent_id, self, (x, y))
                    self.add_agent(wall, wall.pos)

    def find_path(self, start=(0, 0), end=(0, 0)):
        """
        this function find the path of
        :return:
        """
        if self.xymap_changed:
            matrix = self.xymap_arr
            self.gridd = Grid(matrix=matrix)
        start = self.to_findpatharrayxy(start[0], start[1])
        end = self.to_findpatharrayxy(end[0], end[1])
        start = self.gridd.node(start[0], start[1])
        end = self.gridd.node(end[0], end[1])
        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        path, runs = finder.find_path(start, end, self.gridd)
        if path:
            fixed_path = [(x, self.height-1-y) for x, y in path]
            return fixed_path
        return None


    def randomize_workers(self):
        """
        helper function for self.step()

        puts workers in randomized list for step function
        """
        # workers_shuffle = list(self.schedule.agents_by_type[Trader].values())
        # self.random.shuffle(workers_shuffle)
        #
        # return traders_shuffle
        # new
        pass

    def time_jump(self):
        """
        Change the date if it's weekend or if all workers has left the site
        :return:
        """
        if self.status == "after working hours":
            workers = [agent for agent in self.schedule.agents if type(agent) is Worker]
            numberOfWorkers = len(workers)
            workersOut = 0
            for worker in workers:
                if worker.status == self.arrival_zone_name and worker.intention == self.arrival_zone_name:
                    workersOut += 1

            if workersOut == numberOfWorkers:
                self.current_datetime = self.current_datetime + timedelta(days=1)
                self.current_datetime = self.current_datetime.replace(hour=self.start_hour, minute=0)

        if self.current_datetime.weekday() == 5:
            self.current_datetime = self.current_datetime + timedelta(days=2)
            self.this_week = str(self.current_datetime.year) + "-" + str(self.current_datetime.isocalendar()[1])
            self.this_date = str(self.current_datetime.year) + "-" + str(
                self.current_datetime.isocalendar()[1]) + "-" + self.dayNumber_to_Text(
                self.current_datetime.weekday())
        elif self.current_datetime.weekday() == 6:
            self.current_datetime = self.current_datetime + timedelta(days=1)
            self.this_week = str(self.current_datetime.year) + "-" + str(self.current_datetime.isocalendar()[1])
            self.this_date = str(self.current_datetime.year) + "-" + str(
                self.current_datetime.isocalendar()[1]) + "-" + self.dayNumber_to_Text(
                self.current_datetime.weekday())

    def update_this_day_start_date(self):
        """update the reference date of this day so all other times are calculated according to this reference"""
        if self.today != self.current_datetime.day:
            self.today = self.current_datetime.day
            self.this_day_start_date = datetime(self.current_datetime.year, self.current_datetime.month,
                                                self.current_datetime.day, 0, 0, 0)

    def dayNumber_to_Text(self, day):
        """
        Convert day to number
        :param day: day of the week in string for example "mon"
        :return:
        """
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        return days[day]

    def determine_scenario_name(self):
        """
        Determine the scenario name of the simulation as parameter of the model
        :return:
        """
        scenario_name = list()
        #scenario_name = [key[3]+str(value) for key,value in self.max_task_workers.items()]
        n_of_workers = sum([value for key,value in self.max_task_workers.items() if key in flatten(list(self.tasks_sequence.values())) ])
        scenario_name.append(str(n_of_workers))
        scenario_name.append("-T{}".format(self.zone_max_trades))
        scenario_name.append("-Z{}".format(self.zone_max_worker))
        if len(self.painting_worker_skills) > 6:
            scenario_name.append("-t")
        if  len(self.palstering_worker_skills) > 6:
            scenario_name.append("-l")



        if self.tasks_sequence == {1: ["KEYSTART", "KEYFRAMES"], 2: ['KEYMECH'], 3: ['KEYELEC'], 4: ["KEYINSU"], 5: ["KEYSTUD"],6: ["KEYPAINTING"], 7: ["KEYFINISHING"], 8: ["KEYEND"]}:
            scenario_name.append("-Q1")

        elif self.tasks_sequence == {1: ["KEYSTART"]}:
            scenario_name.append("-Q2")

        if self.one_behavior_file :
            scenario_name.append("-O")
        self.scenario = "".join(scenario_name)
        return self.scenario

    @staticmethod
    def get_seed(model):
        """
        return the current seed of the model
        :param model: ConPro model
        :return: current seed (int)
        """
        return model._seed

    def get_days(self):
        """
        get the number of passed days
        :return:
        """
        return ((self.current_datetime - self.simulation_startdate).days)

    def set_all_available_tasks(self):
        """
        Loop through all drywalls and set the available tasks
        :return:
        """
        #todo: this is temporary object not need to add self. Consider this
        #todo: same apply to available_task in  drwyall
        #todo: CHECK MAX NUMBER OF WORKERS in each zone
        #todo: check max number of workers for each drywall or maybe this each drywall can take care of it
        self.available_tasks = dict()
        for drywall_name, drywall_agent_list in self.drywalls_agents.items():
            drywall_agent = drywall_agent_list[0]
            if drywall_agent.available_tasks:
                for task_key in drywall_agent.available_tasks:
                    drywall_task = drywall_agent.tasks[task_key]
                    model_task = self.is_task_pickable(drywall_task)
                    if model_task:
                        self.available_tasks[task_key] = self.available_tasks.get(task_key, [])
                        if task_key and model_task not in self.available_tasks[task_key]:
                            self.available_tasks[task_key].append(model_task)

        # print ("self.available_tasks", self.available_tasks)

    def get_today_minutes(self):
        """
        calculate the number of minutes passed since the start of the day
        :return: minutes passed for each day
        """
        return (self.current_datetime - self.this_day_start_date).seconds / 60

    def get_total_minutes(self):
        """
        Get the passed working minutes since the start of the simulation
        :return:
        """
        start = self.simulation_startdate.date()
        end = self.current_datetime.date()
        return np.busday_count(start, end)  # return total numbers of days

    def get_status(self):
        """
        The current status on site for example "working hours" or "coffe break"
        :return: string the status on site
        """
        if self.get_today_minutes() < self.arrival_time_mode:
            self.status = "before working hours"
        elif self.get_today_minutes() >= self.coffe_break_start and self.get_today_minutes() <= (
                self.coffe_break_start + self.coffe_break_duration):
            self.status = "coffe break"
        elif self.get_today_minutes() >= self.coffe_break2_start and self.get_today_minutes() <= (
                self.coffe_break2_start + self.coffe_break_duration):
            self.status = "coffe break"
        elif (self.get_today_minutes() >= self.lunch_break_start) and self.get_today_minutes() <= (
                self.lunch_break_start + self.lunch_break_duration):
            self.status = "lunch break"
        elif self.get_today_minutes() > (self.leave_time_mode):
            self.status = "after working hours"
        else:
            self.status = "working"
        return self.status

    def utility_functions_material_pk_dur(self):
        """
         the duration needed to pick a material
        :param :
        :return: duration to pick material in minutes
        """
        time = self.random.triangular(self.picking_material_duration_min, self.picking_material_duration,
                                      self.picking_material_duration_max)
        return time

    def utility_functions_breakduration(self, max):
        """
         the duration of break
        :param max: maximum possilbe duration (duration can't be more than time left for break)
        :return: duration to pick material in seconds
        """
        time = self.random.triangular(self.break_duration_min, self.break_duration, self.break_duration_max)
        return max if (max and time > max) else time

    def utility_functions_placing_lunchbox(self):
        """
         the tiem to put the lunch box
        :param :
        :return: duration to put the lunch box when arriving to site
        """
        time = self.random.triangular(self.lunchbox_duration_min, self.lunchbox_duration,
                                      self.lunchbox_duration_max)
        return time

    def utility_functions_workduration(self, max):
        """
         duration in working location
        :param max: is the maximum duration possible untile the coming major event (coffe break, ...etc)
        :return: duration of the time that will be spent in working location in minutes
        """
        time = self.random.triangular(self.work_duration_min, self.work_duration, self.work_duration_max)
        return max if (max and time > max) else time

    def utility_functions_selectbreakType(self):
        """
         select the type of next break
        :param :
        :return: the type of the next break
        """
        breakList = [self.break_zone_name, self.break_zone_name]
        return (self.random.choices(breakList, cum_weights=(1, 10), k=1)[0])

    def utility_functions_arrival(self, arrival):
        """
         arrival time
        :param arrival: the time that this trade is supposed to arrive at
        :return: the arrival time in minutes
        """
        self.arrival_time = self.random.triangular(self.arrival_time_min - arrival,
                                                   self.arrival_time_mode - arrival,
                                                   self.arrival_time_max - arrival)
        return self.arrival_time

    def utility_functions_leave(self, arrival):
        """
         leave time
        :param arrival: the time that this trade is supposed to arrive on in minutes (since 00:00 am)
        :return: the leave time in minutes
        """
        leave_time = self.random.triangular(self.leave_time_min - arrival, self.leave_time_mode - arrival,
                                            self.leave_time_max - arrival)
        return leave_time

    def utility_functions_lunchbreak(self):
        """
         lunch break duration
        :param :
        :return: lunch break duration in minutes
        """
        lunch_break_time = self.random.triangular(self.lunch_break_duration_min, self.lunch_break_duration,
                                                  self.lunch_break_duration_max)
        return lunch_break_time

    def utility_functions_lunchbreak_start(self, arrival):
        """
         lunch break start
        :param arrival: the time that this trade is supposed to arrive on in minutes (since 00:00 am)
        :return: lunch break start in minutes
        """
        lunch_break_start_time = self.random.triangular(self.lunch_break_start_min - arrival,
                                                        self.lunch_break_start - arrival,
                                                        self.lunch_break_start_max - arrival)
        return lunch_break_start_time

    def utility_functions_lunchbreak_duration(self):
        """
         lunch break duration
        :param :
        :return: lunch break duration in minutes
        """
        lunchbreak_duration_time = self.random.triangular(self.lunch_break_duration_min, self.lunch_break_duration,
                                                          self.lunch_break_duration_max)
        return lunchbreak_duration_time

    def utility_functions_coffe_break_start(self, arrival):
        """
         coffe break start
        :param arrival: the time that this trade is supposed to arrive on in minutes (since 00:00 am)
        :return: lunch break start in minutes
        """
        coffe_break_start_time = self.random.triangular(self.coffe_break_start_min - arrival,
                                                        self.coffe_break_start - arrival,
                                                        self.coffe_break_start_max - arrival)
        return coffe_break_start_time

    def utility_functions_coffe_break2_start(self, arrival):
        """
         coffe break start
        :param arrival: the time that this trade is supposed to arrive on in minutes (since 00:00 am)
        :return: lunch break start in minutes
        """
        coffe_break_start_time = self.random.triangular(self.coffe_break2_start_min - arrival,
                                                        self.coffe_break2_start - arrival,
                                                        self.coffe_break2_start_max - arrival)
        return coffe_break_start_time

    def utility_functions_coffe_break_duration(self):
        """
         coffe break duration
        :param :
        :return: lunch break duration in minutes
        """
        coffe_break_duration_time = self.random.triangular(self.coffe_break_duration_min, self.coffe_break_duration,
                                                           self.coffe_break_duration_max)
        return coffe_break_duration_time

    # endnew

    def run_agent_step_bytype(self, type=Worker):
        """
        return the step function for different agnets
        :param motypedel: Class name represent the agent of the agent
        :return:
        """
        for agent in self.schedule.agents_by_type[type].values(): # loop over agents of specific type
            agent.step()

    def get_agents_by_type(self):
        """
        Get agents by their Class name and store/cash the objects in model dictionary
        :return:
        """
        pass

    def increase_n_workers(self, selected_task_key, task_index):
        """
        increaase the number of workers working ono specific task for a give task
        :return:
        """
        self.available_tasks[selected_task_key][task_index]["n_worker"] = \
        self.available_tasks[selected_task_key][task_index]["n_worker"] + 1

    def decrease_n_workers(self, selected_task_key, task_index):
        """
        decrease the number of workers working ono specific task for a give task
        :return:
        """
        self.available_tasks[selected_task_key][task_index]["n_worker"] = \
        self.available_tasks[selected_task_key][task_index]["n_worker"] - 1

    def increase_completed_drywall(self):
        """
        return the number of completed drywalls
        :return:
        """
        self.completed_drywalls += 1

    def get_completed_drywalls(self):
        """
        get the number fo completed drywall
        :return: integre of the number of completed drywalls
        """
        return self.completed_drywalls

    def is_all_drywalls_completed(self):
        """
        check if all drywalls are completed
        :return:
        """
        if self.get_completed_drywalls() >= self.number_of_drywalls:
            return True
        else :
            return False

    def remove_zone_works(self, zone):
        """
        Remove  tasks from availabe tasks in the zone that got congested
        self.available_tasks = {task_key:[{task1} , {task 2}]}
        :param zone:number of visitors to zone block workers ability to work
        :return:
        """
        for tasks_lists in self.available_tasks.values():#[[{}, {}], [{},{}]]
            for task in tasks_lists:
                if task["zone_name"] == zone:
                    task["constraints"].add("zone")


    def remove_task(self, task_key, task_index):
        """
        Remove tasks from avaialbe tasks if number of workers exceeded the maximum for this task
        :param task_key: task key (KEYMECH)
        :param task_index: task index in avaialbe tasks
        :return:
        """
        self.available_tasks[task_key][task_index]["constraints"].add("task")  # remove this task from avilable


    def remove_drywall(self, drywall):
        """
        Remove all tasks of the drywall
        :param drywall: name of drywall to be removed
        :return:
        """
        for tasks_list in self.available_tasks.values():
            for task in tasks_list:
                if task["drywall"] == drywall:
                    task["constraints"].add("drywall")

    def step(self):
        """
        Unique step function that does staged activation of agents
        """
        self.run_agent_step_bytype(Drywall)
        self.run_agent_step_bytype(DummyDrywall)
        self.set_all_available_tasks()
        # self.assgin_tasks_to_workers()
        self.run_agent_step_bytype(Worker)
        self.run_agent_step_bytype(Zone)

        self.schedule.steps += (
            1  # important for data collector to track number of steps
        )
        self.schedule.time +=1
        self.get_status()
        self.current_datetime = self.current_datetime + timedelta( microseconds=self.simulation_speed_microsec)  # add five seconds
        self.time_jump()
        self.update_this_day_start_date()
        self.get_total_minutes()
        if self.status in ["working"]:
            self.passed_working_time += (self.simulation_speed_microsec / 1000000) / 60
        # collect data
        self.datacollector.collect(self)

        if self.schedule.steps > self.running_steps:
            self.running = False


        if self.is_all_drywalls_completed():
            print("all completed")
            self.run_agent_step_bytype(Drywall)
            self.run_agent_step_bytype(DummyDrywall)
            self.set_all_available_tasks()
            self.run_agent_step_bytype(Worker)
            self.run_agent_step_bytype(Zone)
            self.running = False


        # collect model level data
        # self.datacollector.collect(self)

    def run_model(self, step_count=1000):
        for i in range(step_count):
            self.step()

#todo:sanity check to verify code is working as expected
 #    assert self.n_painting_workers > 0 # the model has painint worker