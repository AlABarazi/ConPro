import math
import mesa
from datetime import timedelta
# Helper function
def get_distance(pos_1, pos_2):
    """
    Calculate the Euclidean distance between two positions
    """
    
    x1, y1 = pos_1
    x2, y2 = pos_2
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx**2 + dy**2)
# todo: worker set current trade for picked bim_element
class Worker(mesa.Agent):
    """
    This agent represent the worker agent, in this project bim_element worker is modeled
    In futuer development, this should be a parent class where all other workers type can be considered child to it.
    """
    def __init__(
        self,
        unique_id,
        model,
        pos,
        moore=False,
        #target_space, elevator
        moving=False,
            production_rate=None,
            behavior_files=None,
        trade="plastering",
        arrival=0,
        # task_porb={},
        # durations_dist={},
        # activities=[],
        behaviors_by_key=None,
        color="#20FA50",
        name="",
        carrying_materials=False,
        current_floor=1,
        dst_floor=1,
        arrived=False,
        gotToday=False,
        FullfillingIntention=False, # moving is enough 
        intentionExpire = 0, 
        workTimeSet=False, 
        utilization=0,
        t_at_workplace=0, 
        IntentionStartTime=0, 
        IntentionFullfilmentTime=0,
        total_intentions=0, 
        t_at_site=0,
        target_space = None,
        selected_task_key = None,
        bim_element_name = None,
        bim_element = None,

    ):
        super().__init__(unique_id, model)
        if production_rate is None:
            production_rate = dict()
        if behavior_files is None:
            behavior_files = dict()
        if behaviors_by_key is None:
            behaviors_by_key = dict()
        if target_space == None:
            target_space = None
        if selected_task_key == None:
            selected_task_key = None
        if bim_element_name == None:
            bim_element_name = None
        if bim_element == None:
            bim_element = None
        self.bim_element_name = bim_element_name
        self.walk_speed = self.model.init_walk_speed
        self.pos = pos
        self.name = name
        self.moore = moore
        self.trade = trade
        self.arrival=arrival
        self.moving = moving
        self.production_rate = production_rate
        self.behaviors_by_key = behaviors_by_key
        # self.task_porb = task_porb
        # self.durations_dist = durations_dist
        # self.activities = activities
        self.color = color
        self.visual = {
            "Shape": self.trade+".png",
            "Filled": "true",
            "r": 1,
            "Layer": 0,
            "Color": color,
            "w" : 3,
            "h" : 3,
            "scale" :3,
        "text":"",
        "text_color":"black",
            "heading_x":1,
            "heading_y":1
        }
        self.isNewVisual = True
        self.path = []
        self.destination = (20, 20)
        self.grid_per_sec = self.model.grids_per_meter*self.walk_speed
        self.grid_per_step =  round(self.grid_per_sec*self.model.simulation_speed_sec)  # one grid/step to be calculated based on workers instial speed and simulation speed
        self.agent_name = ""
        self.carrying_materials = carrying_materials
        self.current_floor = current_floor
        self.dst_floor = dst_floor
        self.arrived = arrived
        self.gotToday = gotToday
        self.workTimeSet = workTimeSet
        self.utilization = utilization
        self.t_at_workplace = t_at_workplace
        self.IntentionStartTime = IntentionStartTime
        self.intentionExpire = intentionExpire
        self.IntentionFullfilmentTime = IntentionFullfilmentTime
        self.FullfillingIntention = FullfillingIntention  # moving is enough
        self.total_intentions = total_intentions
        self.t_at_site = t_at_site
        self.times_in_spaces = {}
        self.times_for_intentions = {}
        self.intention_start_time = 0
        self.intention_fullfilment_time = 0
        self.intention_fullfilled = True
        self.times_for_intentions_peak = {}
        self.intention_start_time_peak = 0
        self.intention_fullfilment_time_peak = 0
        self.intention_fullfilled_peak = True
        self.arrived = arrived
        self.current_step = self.model.current_datetime
        self.duration = 0
        self.gotToday = gotToday
        self.arrival = arrival
        self.mytimes = {"finish":None,
        "duration":None} # do not initialize this inside init function
        self.carry_lunch_box = False
        self.picking_material_duration = 0
        self.picking_material_duration_min = 0
        self.picking_material_duration_max = 0
        self.mytimes["arrival_time"] = 0
        self.mytimes["coffe_break_start"] = 0
        self.mytimes["coffe_break2_start"] = 0
        self.mytimes["lunch_break_start"] = 0
        self.mytimes["leave_time"] = 0
        self.mytimes["coffe_break_duration"] = 0
        self.mytimes["coffe_break2_duration"] = 0
        self.mytimes["lunch_break_duration"] =  0
        self.mytimes["placing_lunchbox_duration"] = 0
        self.mytimes["mt_picking_du"] = 0
        self.behavior_files = behavior_files
        self.status = self.model.arrival_zone_name # elevator
        self.intention = self.model.arrival_zone_name
        self.total_time_idle = 0
        self.idle_percentage = 0
        self.selected_task_key = None
        self.bim_element = bim_element
        self.target_space = target_space
        self.last_t_at_workplace = 0
        self.arrival_time = 0
        self.coffe_break_start = 0
        self.coffe_break2_start = 0
        self.leave_time = 0
        self.coffe_break_duration = 0
        self.coffe_break2_duration = 0
        self.lunch_break_duration = 0
        self.placing_lunchbox_duration = 0
        self.mt_picking_du = 0
        self.start = 0
        self.finish = 0
        self.duration = 0
        self.start_datetime = self.model.this_day_start_date
        self.finish_datetime = self.model.this_day_start_date
        # endnew
    def change_visual(self):
        """
        how agent visualize itself on the grid. used in server.py file in  def Agent_portrayal(agent):
        """
        #self.visual["Color"] = "pink"
        pass

    def read_route(self):
        pass

    def find_path(self, start, end):
        """
        move the agent from its position to other point
        :return:
        """
        return self.model.find_path(start, end)

    def move(self):
        """
        Move the agnet to the new destination (one the destination is not equal to current postion this function will be activated)
        :return:
        """
        if self.pos != self.destination:
            if not self.path:
                self.path = self.find_path(self.pos, self.destination)
            if self.path:
                n_grids_to_move = min(self.grid_per_step, len(self.path))
                next_grid = self.path[n_grids_to_move-1]
                self.model.grid.move_agent(self, next_grid)
                del self.path[:n_grids_to_move]
        elif self.pos == self.destination:
            self.path = []
            #[(startx,starty), point1, point2, end_point]

    def set_status(self):
        """
        set the staut of the worker based on its
        :return:
        """
        if self.isArrivedtoSpace():
            self.status = self.intention
        elif self.isMoving():
            self.status = "moving"


    def isMoving(self):
        """
        determine if worker is moving
        :return:
        """
        if self.pos != self.destination:
            self.moving = True
        else :
            self.moving = False
        return self.moving

    def set_random_destination(self):
        """
        used to set the new destination of worker
        :return:
        """
        if self.pos == self.destination or self.path==None:
            rand_end_x = self.model.random.randint(0, self.model.width-1)
            rand_end_y = self.model.random.randint(0, self.model.height-1)
            rand_end = (rand_end_x, rand_end_y)
            self.destination = rand_end

    def get_today_minutes(self):
        """
        Get the passed minutes since the starting of the day at 12 am 
        :return: minutes as float
        """
        return self.model.get_today_minutes()

    def set_arrival_time(self):
        """
        use utility function to set the arrival time of this worker
        :return: time in minutes
        """
        self.arrival_time = self.model.utility_functions_arrival(self.arrival)
        return self.arrival_time

    def set_coffeBr_time(self):
        """
        use utility function to set the coffe break time of this worker since the starting of the day at 12 am 
        :return: time in minutes
        """
        self.coffe_break_start = self.model.utility_functions_coffe_break_start(self.arrival)
        return self.coffe_break_start

    def set_coffeBr2_time(self):
        """
        use utility function to set the coffe break2 time of this worker since the starting of the day at 12 am 
        :return: time in minutes
        """
        self.coffe_break2_start = self.model.utility_functions_coffe_break2_start(self.arrival)
        return self.coffe_break2_start
    
    def set_lunchBr_time(self):
        """
        use utility function to set the lunch brake time of this worker since the starting of the day at 12 am 
        :return: time in minutes
        """
        self.lunch_break_start = self.model.utility_functions_lunchbreak_start(self.arrival)
        return self.lunch_break_start
    
    def set_leave_time(self):
        """
        use utility function to set the leave time of this worker since the starting of the day at 12 am 
        :return: time in minutes
        """
        self.leave_time = self.model.utility_functions_leave(self.arrival)
        return self.leave_time
    
    def set_coffeBr_duration(self):
        """
        use utility function to set the duration time for the coffe break for this worker
        :return: time in minutes
        """
        self.coffe_break_duration = self.model.utility_functions_coffe_break_duration()
        return self.coffe_break_duration

    def set_coffeBr2_duration(self):
        """
        use utility function to set the duration time for the coffe break2 for this worker
        :return: time in minutes
        """
        self.coffe_break2_duration = self.model.utility_functions_coffe_break_duration()
        return self.coffe_break2_duration

    def set_lunchBr_duration(self):
        """
        use utility function to set the duration time for the lunch break for this worker
        :return: time in minutes
        """
        self.lunch_duration = self.model.utility_functions_lunchbreak_duration()
        return self.lunch_duration

    def set_material_pk_du(self):
        """
        use utility function to set the duratoin time of material picking for this worker
        :return: time in minutes
        """
        self.mt_picking_du = self.random.triangular(self.picking_material_duration_min, self.picking_material_duration , self.picking_material_duration_max)
        return self.mt_picking_du
        
    def set_lunchbox_duration(self):
        """
        use utility function to set the duratoin time of placing lunch box for this worker
        :return: time in minutes
        """
        self.placing_lunchbox_duration= self.model.utility_functions_placing_lunchbox()
        return self.placing_lunchbox_duration

    def decide_times(self):
        """
        Set arrival and leave time for this worker. Also set breaks start times and their durations in minutes (since the starting of the day at 12 am )
        :return:
        """
        self.mytimes["arrival_time"] =  self.set_arrival_time() #modify # 360
        self.utility_functions_select_intention()
        self.mytimes["coffe_break_start"] = self.set_coffeBr_time()
        self.mytimes["coffe_break2_start"] = self.set_coffeBr2_time()
        self.mytimes["lunch_break_start"] = self.set_lunchBr_time()
        self.mytimes["leave_time"] = self.set_leave_time()
        self.mytimes["coffe_break_duration"] = self.set_coffeBr_duration()
        self.mytimes["coffe_break2_duration"] = self.set_coffeBr2_duration()
        self.mytimes["lunch_break_duration"] =  self.set_lunchBr_duration()
        self.mytimes["placing_lunchbox_duration"] = self.set_lunchbox_duration()
        self.mytimes["mt_picking_du"] = self.set_material_pk_du()
        # self.arrival_time = self.mytimes["arrival_time"] # this is just to make extracting data easier in agent_reporter
        # self.coffe_break_start = self.mytimes["coffe_break_start"]
        # self.coffe_break2_start = self.mytimes["coffe_break2_start"]
        # self.leave_time = self.mytimes["leave_time"]
        # self.coffe_break_duration = self.mytimes["coffe_break_duration"]
        # self.coffe_break2_duration = self.mytimes["coffe_break2_duration"]
        # self.lunch_break_duration = self.mytimes["lunch_break_duration"]
        # self.placing_lunchbox_duration = self.mytimes["placing_lunchbox_duration"]
        # self.mt_picking_du = self.mytimes["mt_picking_du"]

    def isArrived(self):
        """
        check if the worker has arrived to site based on the times set by decide_times function
        :return: status of arrival
        """
        if self.get_today_minutes() > self.mytimes["leave_time"] and self.status == self.model.arrival_zone_name:
            self.arrived = False
        elif self.get_today_minutes() > self.mytimes["arrival_time"]:
            self.arrived = True
        else:
            self.arrived = False
        return self.arrived

    def isToday(self):
        """
        check if the current day has ended
        :return: True if the day is ended
        """
        return self.today == self.model.current_datetime.day

    def get_newday_times(self):
        """
        generate new times for arrival, leave, breaks and durations if new day has started or if times were not already set
        :return:
        """
        if not self.gotToday:
            self.today = self.model.current_datetime.day
            self.decide_times()
            self.gotToday = True
        elif not self.isToday():
            self.gotToday = False
            self.carry_lunch_box = True
            self.get_newday_times()

    def isItMyCoffeBreak2(self):
        """
        check if it is coffe break2 for this worker
        :return: True if it is coffe break time
        """
        Cffe_Br_end = self.mytimes["coffe_break2_start"]+self.mytimes["coffe_break2_duration"]
        return  self.get_today_minutes() >= self.mytimes["coffe_break2_start"] and  self.get_today_minutes() <= Cffe_Br_end

    def isItMyCoffeBreak(self):
        """
        check if it is coffe break for this worker
        :return: True if it is coffe break time
        """
        Cffe_Br_end = self.mytimes["coffe_break_start"]+self.mytimes["coffe_break_duration"]
        return  self.get_today_minutes() >= self.mytimes["coffe_break_start"] and self.get_today_minutes() <= Cffe_Br_end

    def isItMyLeavingTm(self):
        """
        check if it is the leaving time for this worker
        :return: True if it is leaving  time
        """
        return  self.get_today_minutes() > self.mytimes["leave_time"]

    def isItMyLunchTm(self):
        """
        check if it is lunchtime for this worker
        :return: True if it is lunch break time
        """
        Lunch_Br_end = self.mytimes["lunch_break_start"]+self.mytimes["lunch_break_duration"]
        return  self.get_today_minutes() > self.mytimes["lunch_break_start"] and  self.get_today_minutes() <= Lunch_Br_end

    def isSameIntention(self, intention):
        """
        Compare the current intention of worker with the new intention (to avoid keeep assgining same intention in every step)
        :param intention: the intention that the worker want to do
        :return: True if the new intention is equal to the current one
        """
        return self.intention == intention

    def canChangeIntention(self):
        """
        Determine if the worker can change intnetion (is arrive, not fullfiling an intention and has arrive to the target space/destination, and the intention has not expired (i.e. due to long waiting))
        :return: True if worker can change intention
        """
        if self.isIntentionExpired():
            return True
        elif  self.isArrived() and self.isArrivedtoSpace() and not self.isFullfillingIntention() and self.isIntentionExpired():
            return True
        else :
           return False

    def setNextDurVar(self, type):
        """
        Set how long the duration for next intention (i.e. in break rooms or in working place)
        :param type: type of intention BRR -> abbreviation for break room
        :return:
        """
        self.mytimes["start"] = self.getTimeArrivedToPlace()#time
        self.mytimes["duration"] = self.get_duration(type= type)
        self.mytimes["finish"] = self.getFinishTime()
        self.start = self.mytimes["start"]
        self.duration = self.mytimes["duration"]
        self.finish = self.mytimes["finish"]
        self.start_datetime = self.model.this_day_start_date + timedelta(minutes=self.start)
        self.finish_datetime = self.model.this_day_start_date + timedelta(minutes=self.finish)

    def get_duration(self,type):
        """
        get the duration of an activity/intention based on its type in minutes
        :param type: type of activity or intention
        :return: the duration of intention or activity
        """
        max_duration = self.max_working_time_duration()
        if type == self.model.break_zone_name:
            self.duration = self.model.utility_functions_breakduration(max_duration)

        elif type == "out_of_work_zone":
            self.mytimes["duration"] = max(self.mytimes["duration"], max_duration)
            self.duration = self.mytimes["duration"] # check this
        else:
            self.duration = self.model.utility_functions_workduration(max_duration) # in minutes
        return self.duration

    def getTimeArrivedToPlace(self):
        """
        get the time when worker arrived to the intended place in minutes
        :return: the time
        """
        return self.get_today_minutes()

    def getFinishTime(self):
        """
        get the time when worker should finish the activity/intention in minutes (since 12 am of this days)
        :return:
        """
        return self.mytimes["start"] + self.mytimes["duration"]

    def isAtWorkPlace(self):
        """
        Check if worker is at his wagon
        :return: True if worker is in the wagon
        """
        if self.bim_element:
            return self.pos == self.bim_element.pos#self.bim_element.tasks[self.selected_task_key]["zone_pos"] # self.status == self.intention and
        else :
            return False

    def isAtBreakSpace(self):
        """
        check if worker is in break space
        :return: return true if worker is in break space
        """
        return self.status == self.intention and self.model.break_zone_name in self.status

    def max_working_time_duration(self):
        """
        The worker has intention start time that can't be fulfilled due to system latency and waitings, thus this function alter the duration
        i.e. worker can't work for 30 minutes when the time left for his next break is 5 minutes.
        :return: how many mintues left for the next event, so the set duration can't be more than the minutes left until the next even
        """
        durations_till_main_breaks = [self.mytimes[key] - self.get_today_minutes() for key in self.mytimes.keys() if key in ["lunch_break_start", "coffe_break_start", "coffe_break2_start", "leave_time" ] ]
        durations_till_main_breaks = [i for i in durations_till_main_breaks if i >= 0]
        durations_till_main_breaks.sort()
        if durations_till_main_breaks:
            durations_till_main_breaks = durations_till_main_breaks[0]
        return durations_till_main_breaks if durations_till_main_breaks else 0

    def set_type_of_next_break(self):
        """
        determien the type of the next break (smoking, talking, telephone, wc, other)
        :return: the type of the next break
        """
        return self.model.utility_functions_selectbreakType()

    def isArrivedtoSpace(self):
        """
        determine if the worker arrived to space when intention == status or when worker position is equal to destination position
        :return:
        """
        if self.destination == self.pos:
            return True
        else :
            return False

    def assgin_intention(self, intention):
        """
        assgine new intention/activity for the worker
        :param intention:
        :return:
        """
        if not self.isSameIntention(intention):
            self.intention = intention

    def isFullfillingIntention(self):
        """
        check if the worker is still fullfilling intention i.e. moving to work space or waiting for elevator or wating to enter a crowded room
        :return: True if the intention of worker has fullfiled
        """
        return self.FullfillingIntention

    def hasFoundTargetSpace(self):
        """
        worker search for space to go based on intention, this function check if worker found the space looked for
        :return: True if the worekr found the space
        """
        if self.target_space.name == self.intention:
            return True
        else:
            return False

    def setIntentionExpireAt(self, start, duration):
        """
        Determine the time when the intention expire
        :param start: the start time of intention in minutes
        :param duration: the duration of intention in minutes
        :return:
        """
        self.intentionExpire = start + duration

    def isIntentionExpired(self):
        """
        check if intention/activity time has expired so person/worker can set new one
        :return: True if the current time in minutes is more than the time when the intention should expire
        """
        return self.get_today_minutes() > self.intentionExpire

    def hasLunchBox(self):
        """
        is the worker still has lunch box (if scenario include this option)
        :return:
        """
        return  self.carry_lunch_box and self.model.visit_BR_first

    def change_intention(self):
        """
        used to determine the intention of the worker (and set intention for now also )
        :return: #todo: should return the intention so other function set intention will be used to set intention
        """
        if self.isItMyLeavingTm():
            self.intention = self.model.arrival_zone_name
            self.setIntentionExpireAt(0,0)
        elif self.isItMyCoffeBreak() :
            self.intention = self.model.break_zone_name
            self.setIntentionExpireAt(self.mytimes["coffe_break_start"], self.mytimes["coffe_break_duration"])
        elif self.isItMyCoffeBreak2():
            self.intention = self.model.arrival_zone_name
            self.setIntentionExpireAt(self.mytimes["coffe_break2_start"], self.mytimes["coffe_break2_duration"])
        elif self.isItMyLunchTm():
            self.intention = self.model.arrival_zone_name
            self.setIntentionExpireAt(self.mytimes["lunch_break_start"], self.mytimes["lunch_break_duration"])
        elif self.isAtWorkPlace():
            intention, duration = self.utility_functions_select_intention()
            self.intention = intention
            self.mytimes["duration"] = duration/60 # to minutes # this determine duration out of workplace (nwz , wz )
            self.setNextDurVar('out_of_work_zone')
            self.setIntentionExpireAt(self.mytimes["start"], self.mytimes["duration"])
        elif not self.isAtWorkPlace(): # goToWorkPlace:
            # self.assgin_intention(self.set_type_of_next_break())
            self.intention = self.bim_element.zone
            self.setNextDurVar(self.intention)
            self.setIntentionExpireAt(0, self.mytimes["finish"])

    def workerWagonName(self):
        """
        get wagon name of worker
        :return:
        """
        return self.agent_name[:3]

    def find_space(self):
        """
        find target space for worker
        :return:
        """

        if self.intention == self.bim_element.zone:
            if not self.model.model_tasks_grids:
                self.target_space = self.model.zones_agents[self.bim_element.zone][0]
            else:
                self.target_space = self.model.zones_agents[self.bim_element.name][0]
        else:
                self.target_space = self.model.zones_agents[self.intention][0]

    def set_destination(self):
        """
        Set the destination position to match the target_space
        :return:
        """
        if self.target_space:
            self.destination = self.target_space.pos
    def pick_choice_pdfunc(self, pdfseries):
        """
        :param pdfseries:pdf series which has index
        :return:
        """

    def utility_functions_select_intention(self):
        """
        worker agent decide what to do next
        :return: next activity and its duration
        """
        # {"task_porb":task_porb, "durations_dist":durations_dist, "activities":activities, "wz_nwz_prob":wz_nwz_prob, "nwz_wz_pdfs":nwz_wz_pdfs}
        if self.selected_task_key:
            task_porb = self.behaviors_by_key[self.selected_task_key]["wz_nwz_prob"]
            next_work = self.model.random.choices(population=list(task_porb.keys()) ,weights=list(task_porb.values()), k=1)
            next_work = next_work[0]
            next_work_durations_pdfseries = self.behaviors_by_key[self.selected_task_key]["nwz_wz_pdfs"][next_work]
            population = next_work_durations_pdfseries.index
            weights = next_work_durations_pdfseries.values
            duration = self.model.random.choices(population, weights)[0]
            duration if duration >= 0 else self.utility_functions_select_intention()
            next_work = self.model.random.choices(self.model.zones_dwwz_nwwz[next_work]) # working zone or non working zone
            next_work = next_work[0]
            # return choices(population, weights)[0]
            # next_work = self.model.random.choices(population=list(self.behaviors_by_key[self.selected_task_key]["task_porb"].keys()) ,weights=list(self.behaviors_by_key[self.selected_task_key]["task_porb"].values()), k=1)
            # next_work = next_work[0]
            # next_work_durations = self.behaviors_by_key[self.selected_task_key]["durations_dist"][next_work]#df[df[next_work] != ""][next_work]
            # duration = self.model.random.choice(next_work_durations)
            return (next_work, duration)
        # return (random.choices(breakList, cum_weights=(1, 10), k=1)[0])

    def setIntentionStartTime(self):
        """
        set the start time of intention
        :return:
        """
        self.IntentionStartTime = self.get_today_minutes()

    def setIntentionFullfillmentTime(self):
        """
        set the time when the worker fullfill intention
        :return:
        """
        self.IntentionFullfilmentTime = self.get_today_minutes()

    def getIntentionStartTime(self):
        """
        get the intention start time
        :return:
        """
        return self.IntentionStartTime

    def getIntentionFullfillmentTime(self):
        """
        get intention fullfilment time
        :return:
        """
        return self.IntentionFullfilmentTime

    def sendVisitorOutOfSpace(self):
        """
        used to remove person from space (space keep track of the number of worker it has)
        :return:
        """
        if self.target_space:
            self.target_space.remove_visitor_from_space(self)

    def registerVisitorToSpace(self):
        """
        assgin person to space when person arrive to space
        :return:
        """
        # todo:add function register_person
        if self not in self.target_space.current_visitors:
            self.target_space.add_visitor_to_space(self)

    def calculate_utilization(self):
        """
        calculate utilization of the worker (can be then captured for each step from the model)
        :return:
        """
        if self.isAtWorkPlace():
            if self.calculate_time_at_site_today():#self.model.passed_working_time:
                self.t_at_workplace +=(self.model.simulation_speed_microsec/1000000)/60
                self.utilization = 100*self.t_at_workplace/self.t_at_site

    def calculate_idle_time(self):
        """
        calculate utilization of the worker (can be then captured for each step from the model)
        :return:
        """
        if self.is_idle():
            if self.calculate_time_at_site_today():#self.model.passed_working_time:
                self.total_time_idle +=(self.model.simulation_speed_microsec/1000000)/60 # add the time of each step
                self.idle_percentage = 100*self.total_time_idle/self.t_at_site

    def calculate_time_at_site_today(self):
        """
        calculate the time this worker spent on site (worker has different arrival times)
        :return: duration in site for this day for this worker in minutes
        """
        if self.isArrived():
            return self.get_today_minutes() - self.mytimes["arrival_time"]

    def calculate_time_at_site_total(self):
        """
        calculate the time  passed on site since the start for the simulation (worker has different arrival times)
        :return: set time passed since statrt of simulation in minutes
        :return:
        """
        if self.isArrived():
             self.t_at_site +=(self.model.simulation_speed_microsec/1000000)/60

    def determine_possible_tasks(self):
        """
        Determine the possible tasks that can be worked on depending on the trade of this worker
        :return:
        """
        possible_tasks_key = self.production_rate.keys()
        possible_tasks = {task_key:tasks for task_key, tasks in self.model.available_tasks.items() for task in tasks if task_key in possible_tasks_key
                          if (task["n_worker"] < task["max_n_worker"] and not task["constraints"])} #
        return possible_tasks

    def pick_task_key(self, possible_tasks):
        """
        select task key from the avaialbe tasks
        :return:
        """
        match self.model.task_piking_strategy:
            case "random":
                selected_task_key = self.model.random.choice(list(possible_tasks.keys()))
            case "first":
                selected_task_key = list(possible_tasks.keys())[0]
            case _:
                selected_task_key = self.model.random.choice(list(possible_tasks.keys()))
        return selected_task_key

    def pick_task(self, possible_tasks, selected_task_key):
        """
        worker pick a task to work on from the available tasks (now random, later according to some rules)
        :param possible_tasks: dictionary of possible tasks the keys and the tasks that the worker can do and value is list of possible tasks
        {"KEYMECH":[{"amount":200, "bim_element":"dry_wall11"......},{"amount":200, "bim_element":"dry_wall12"......}]} or {"KEYMECH":[{task1},{task2}]}
        :return:
        """
        n_tasks = len(list(possible_tasks[selected_task_key]))
        tasks = list(possible_tasks[selected_task_key])
        match self.model.task_piking_strategy:
            case "random":
                task_index = self.model.random.choice(range(n_tasks))
            case "first":
                task_index = 0
            case _:
                task_index = self.model.random.choice(range(n_tasks))
        selected_task = tasks[task_index]
        return selected_task, task_index

    # def pick_bim_element(self, task):
    #     """
    #     pick the bim_element to work on based on the selected task, information about
    #     :param task:
    #     :return:
    #     """
    #     self.bim_element = task["bim_element"]

    def is_idle(self):
        """
        check if the worker is idel (present in site but not doing work)
        :return: True if the worker is idle False otherwise
        """
        return True if self.intention == self.status == "idle" else False

    def print_attributes(self):
        """
        print the attributes of this agent
        :return:
        """
        print ("worker_att", "dest", self.destination,
               "pos", self.pos,
                "status", self.status,
                "intention",self.intention,
               "isIntentionExpired", self.isIntentionExpired(),
               "isArrivedtoSpace", self.isArrivedtoSpace(),
               "status", self.status,
               "FullfillingIntention", self.FullfillingIntention,
               "canChangeIntention", self.canChangeIntention(),
               "arrived", self.arrived,
               "get_today_minutes",self.get_today_minutes(),
               "mytimes", self.mytimes,
               self.unique_id)

    def step(self):
        """
        executed at each step by the schedular (the model). Other option is to define what should be done during each step in the model
        (can be safer option if the actiavation method of agents matter)
        i.e. the all the worker first should move , then all the worker should work  then the bim_elements should generate tasks
        if the activation is made by step  function then the activation will not consider agent type
        """
        # if self.trade == "plastering":
        # self.print_attributes()
        # print(self.is_idle(),self.isAtWorkPlace(), "worker", self.intention, self.status, self.idle_percentage, self.utilization)
        if self.isNewVisual:
            self.change_visual()
            self.isNewVisual = False
        self.calculate_time_at_site_total()
        #self.set_random_destination()
        # self.current_datetime = self.model.current_datetime
#        if self.status[:3] == self.intention[:3] and self.status[:3] == "BRR":
#            self.carry_carry_lunch_box = False
#         if self.agent_name != "dummy" :
            # if self.agent_name[-1]:# == "0":

        self.get_newday_times()# keep thisfirst
#                 self.calculate_time_at_site_total()

        if not self.bim_element:#get bim_element to work on if you don't have one
            possible_tasks = self.determine_possible_tasks()
            if possible_tasks and not self.bim_element:
                selected_task_key = self.pick_task_key(possible_tasks)
                task, task_index = self.pick_task(possible_tasks, selected_task_key)
                # if more than one trade can work on different bim_elements
                # if not self.model.one_zone_one_trade: # zone does not have any trade
                    #and selected_task_key not in self.model.zones_agents[0][task["zone_name"]].current_trade
                self.selected_task_key = selected_task_key
                self.task_index = task_index
                self.bim_element_name = task["bim_element"]
                self.bim_element = self.model.bim_elements_agents[self.bim_element_name][0]
                self.bim_element.current_trade = self.trade
                # update zone, tasks for bim_element and tasks avaialabe in the model
                # remove tasks that can't be picke
                # if self.trade == "plastering":
                #
                self.model.increase_n_workers(selected_task_key, task_index)
                # self.bim_element.increase_n_workers(selected_task_key) # update bim_element n_workers
                self.bim_element.add_person(self) # update bim_element task n_workers
                zone = self.model.zones_agents[self.bim_element.zone][0]
                zone.add_worker(self)
                zone.add_trade(selected_task_key) # update zone
                if zone.is_trades_full() or zone.is_workers_full() or zone.is_visitors_full():
                    # remove all bim_elements in this zone from avaialbe
                    self.model.remove_zone_works(zone.name)
                elif self.bim_element.is_bim_element_max_n_worker(): #
                     # remove this bim_element from availabe
                    self.model.remove_bim_element(self.bim_element.name)
                elif self.bim_element.is_task_max_n_worker(task):
                    self.model.remove_task(self.selected_task_key, self.task_index)

        if self.bim_element:
            if not self.bim_element.tasks[self.selected_task_key]["finished"]:
                if self.canChangeIntention():
                    self.sendVisitorOutOfSpace()
                    self.change_intention()
                    self.setIntentionStartTime()
                    self.find_space()
                    self.FullfillingIntention = True
                    self.total_intentions += 1
                    self.set_destination()
                if self.isFullfillingIntention():
                    self.move()
                    self.set_status()
                    self.entered_wp_at = None
                    # self.sendVisitorOutOfSpace()
                    if self.isArrivedtoSpace():
                        self.registerVisitorToSpace()
                        self.setIntentionFullfillmentTime()
                        self.FullfillingIntention = False

                if self.isAtWorkPlace():
                    self.calculate_utilization()
                    self.last_t_at_workplace +=(self.model.simulation_speed_microsec/1000000)/60
                    if self.last_t_at_workplace > self.model.w_presence:
                        self.bim_element.reduce_amount(self.production_rate[self.selected_task_key]*self.model.simulation_speed_h)
            if self.bim_element.tasks[self.selected_task_key]["finished"]:
                #todo:remove worker from zone
                # self.model.decrease_n_workers(self.selected_task_key, self.task_index)
                self.bim_element.decrease_n_workers(self.selected_task_key)  # update bim_element n_workers
                self.bim_element.remove_person(self)  # update bim_element task n_workers
                self.model.zones_agents[self.bim_element.zone][0].remove_worker(self)
                self.model.zones_agents[self.bim_element.zone][0].remove_trade(self.selected_task_key)  # update zone
                self.bim_element = None
                self.selected_task_key = None
                self.bim_element_name = None

        else:
            self.sendVisitorOutOfSpace()
            self.intention = "idle"
            self.status = "idle"
            self.calculate_idle_time()
            self.destination = (1,1)
            self.move()

                # self.calculate_system_latency("all")
###################################################################
#
# other useful stuff
#
######################
    # def is_occupied(self, pos, occupants_number):
    #     """
    #     determine if the cell with position pos is occupied
    #     :param pos: position of grid/cell to check
    #     :param occupants_number: number of occupents in this grid cell
    #     :return: True if the the cell/grid is not occupied or occupied with number leess than occupants_number
    #     """
    #     this_cell = self.model.grid.get_cell_list_contents([pos])
    #     return len(this_cell) >= occupants_number
    #
    # def get_agent(self, pos, agent_type):
    #     """
    #     return
    #     :param pos:
    #     :param agent_type:
    #     :return:
    #     """
    #     agents = list()
    #     this_cell = self.model.grid.get_cell_list_contents([pos])
    #     for agent in this_cell:
    #         if type(agent) is agent_type:##check the type of agent in the cell
    #             agents.append(agent)
    #     return agents
    #
    # def get_neighbors_by_type(self, space_type, vision=90):
    #     neighbors = [i for i in self.model.grid.get_neighborhood(self.pos, self.moore,
    #             False, radius=vision) ]  # self.vision#get_neighborhood return the cells of the grid then we want to check if they are occupied (there is agents in them)note that  radius determine the number of cells to consider as neighbor
    #     workspaces_agents =  [self.get_agent(pos, space_type) for pos in neighbors]#get pos of wagons
    #     workspaces_agents_cleaned = [agent for agent in workspaces_agents if agent is not None]
    #     return workspaces_agents_cleaned


#     def move(self):
#         if self.status == "go_to_elevator":
#             x = self.model.check_unoccupied_waitingspace(self.model.cells_x["EV"], self.pos[1], self.model.waiting_cells, 1000)
#             self.model.grid.move_agent(self,(x, self.pos[1]))
#             self.status = "wait_for_EV"
# #            self.select_anelevator()
#             self.call_elevator()
#
#         elif   self.status == "go_by_stairs":
#            x = self.model.check_unoccupied_waitingspace(self.model.stair_x, self.pos[1], self.model.stair_cells, 1000)
#            self.model.grid.move_agent(self, (x, self.pos[1]))
#            if self.target_space.pos[1] > self.pos[1]:
#                x = self.model.check_unoccupied_waitingspace(self.model.stair_x, self.pos[1]+1, self.model.stair_cells, 1000)
#                #maybe model level function that have the rules  tell the agent where to go
#                self.model.grid.move_agent(self, (x, self.pos[1]+1))
#                self.current_floor+=1
#            elif self.target_space.pos[1] < self.pos[1]:
#                x = self.model.check_unoccupied_waitingspace(self.model.stair_x, self.pos[1]-1, self.model.stair_cells, 1000)
#                self.model.grid.move_agent(self, (x, self.pos[1]-1))
#                self.current_floor-=1
#            else:
#                self.status = "arrived"
#
#         elif self.status == "arrived" or self.status == "waiting":
#
#             if len(self.target_space.register_list) < self.target_space.capacity:
#                 self.target_space.register_person(self)
# #                x = self.model.check_unoccupied_waitingspace(self.target_space.pos[0], self.pos[1], self.model.waiting_cells, 20)
#                 #  each space has to tell the worker where to go
#                 self.model.grid.move_agent(self,  self.target_space.pos)
# #                self.model.grid.move_agent(self, (x, self.target_space.pos[1]))
#
# #                self.model.grid.move_agent(self, (self.model.check_unoccupied_waitingspace(self.target_space.pos[0],self.target_space.pos[1], self.target_space.capacity)
#                 self.status = self.intention # self.target_space.agent_name[:2]
#                 self.current_step = self.model.current_datetime
# #                        self.duration = self.model.utility_functions(agent=self)
#             else:
#                 self.status = "waiting"
#                 x = self.model.check_unoccupied_waitingspace(self.target_space.pos[0]-self.model.waiting_cells, self.pos[1],self.model.waiting_cells - 1 ,200 )
#                 if self.pos[0] not in range(x, x+6):
#                     if x<0:
#                         x=0
#                         self.model.grid.move_agent(self, (x, self.pos[1]))
#                     else:
#                         self.model.grid.move_agent(self, (x, self.pos[1]))