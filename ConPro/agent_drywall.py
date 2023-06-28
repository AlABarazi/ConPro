import math
import mesa

#todo: estimated_tasks_finish and estimated_total_finish
#todo: the same for model level all task (aggregate from tasks)
#todo: max_n_workers
#todo: for each task make field for the work accomplished
class Drywall(mesa.Agent):
    """
    Drywall class
    """

    def __init__(
            self,
            unique_id,
            model,
            pos,
            moore=False,
            name="xxxx",
            tasks=None,
            zone="xxx",
            GUID="xxxx",
            # todo: add Guid number to each task (when creating the tasks for the drywall) (it can be in every task and also in each task)
            hasStarted=False,
            current_task_key="",
            current_workers=None
    ):
        super().__init__(unique_id, model)
        if current_workers is None:
            current_workers = set()
        if tasks is None:
            tasks = dict()
        self.current_task_index = 1
        self.dry_wall_completed = False
        self.pos = pos
        self.moore = moore
        self.name = name
        self.tasks = tasks
        self.zone = zone
        self.isNewVisual = True
        self.hasStarted = hasStarted
        self.current_task_key = current_task_key
        self.isAvailableTasksSet = False
        self.available_tasks = set()
        self.not_available_tasks = set()
        self.current_trade = ""
        self.current_workers = current_workers
        self.visual = {
            "Shape": "rect",  # # "circle",  "arrowHead"        "r": 3,
            "Filled": "true",
            # "r": 1,
            "Layer": 11,
            "Color": "white",
            "w": 1,
            "h": 1,
            "text": str(len(self.current_workers)),
            "text_color": "black",
            "heading_x": 0,
            "heading_y": 1,
            "scale": 1
        }

    def add_person(self, person):
        """
        add the worker to work on this drywall
        :param person: agent of type worker
        """
        if person not in self.current_workers:
            self.current_workers.add(person)
        self.isNewVisual = True

    def remove_person(self, person):
        """
        Remove the worker from working on this drywall
        :param person: worker agent done working on its tasks
        :return:
        """
        if person in self.current_workers:
            self.current_workers.remove(person)
        self.isNewVisual = True

    def reduce_amount(self, production_rate=100):
        """
        reduce the amount of the task by production rate (perform added value work)
        :param production_rate: average unit/step relfect the production rate of worker
        :return:
        """
        if self.tasks[self.current_task_key]['amount'] >= 0 :
            self.tasks[self.current_task_key]['amount'] = max(self.tasks[self.current_task_key]['amount'] - production_rate, 0)

    def is_taks_finished(self, task_key):
        """
        check if the task is finished
        :return:
        """
        return self.tasks[task_key]["finished"]

    def is_task_max_n_worker(self, task):
        """
        check if n_workerers working on task equal maximum
        :return:
        """
        return task["n_worker"] >= task["max_n_worker"]

    def is_drywall_max_n_worker(self):
        """
        check if n_workerers working on task equal maximum
        :return:
        """
        return len(self.current_workers) >= self.model.drywall_max_workers

    def set_available_task(self):
        """
        set the availabe tasks that can start,
        1 - the workers on drywall should not exceed the maximum
        2. the n_woerkes on particular task should be less than maximu
        3. the n_workers in zone where the task is should not exceed the max_n_workers in that zone
        4. used by model when all grid tasks for the current key is finished
        :return:
        """
        self.available_tasks = set()
        for task_key in self.model.tasks_sequence[self.current_task_index]:
            # if not self.is_drywall_max_n_worker():
                # zone_name = self.tasks[task_key]["zone_name"]
                # zone = self.model.zones_agents[zone_name][0]
                # if not zone.is_total_full() and not zone.is_trades_full() and not zone.is_workers_full():
                #     if  (not self.is_taks_finished(task_key)  and not self.is_task_max_n_worker(task_key)):
            self.available_tasks.add(task_key)
            self.isAvailableTasksSet = True

    def set_task_aquired(self, current_task_key):
        """
        Set the task as aquired
        :param key:
        :return:
        """
        self.tasks[current_task_key]["aquired"] = True
        #todo : add actual_start time

    def increase_n_workers(self, selected_task_key):
        """
        increase the number of workers working ono specific task for a give task
        :return:
        """
        self.tasks[selected_task_key]["n_worker"] = self.tasks[selected_task_key]["n_worker"] + 1

    def decrease_n_workers(self, selected_task_key):
        """
        decrease the number of workers working ono specific task for a give task
        :return:
        """
        self.tasks[selected_task_key]["n_worker"] = self.tasks[selected_task_key]["n_worker"] - 1

    def select_task(self):
        """
        select task from availabe tasks
        :return:
        """
        # print(self.available_tasks)
        self.current_task_key = self.model.random.choice(tuple(self.available_tasks))
        self.available_tasks = set()
        self.available_tasks.add(self.current_task_key)
        return self.current_task_key

    def set_task_finished(self):
        """
        set the task of the current key as finished
        :return:
        """
        #todo: remove workers or woerkers remove themselves
        self.tasks[self.current_task_key]["finished"] = True
        self.available_tasks.remove(self.current_task_key)
        if not self.available_tasks:
            self.isAvailableTasksSet = False

    def isCurrent_index_tasks_finished(self):
        """
        Check if all tasks under the current index are finished
        :return:
        """
        task_status = []
        for task_key in self.model.tasks_sequence[self.current_task_index]:
            task_status.append(self.tasks[task_key]["finished"])
        if all(task_status):
            return True
        else:
            return False

    def is_dry_wall_completed(self):
        """
        check if the drywall has been complete
        :return:
        """
        if all([self.tasks[task_key]['amount']<=0 for sequence_key in self.model.tasks_sequence.keys() for task_key in self.model.tasks_sequence[sequence_key] ]):
            return True
        else:
            return False

    def set_dry_wall_completed(self):
        """
        set the status of drywall to completed
        :return:
        """
        self.dry_wall_completed = True
        self.isNewVisual = True

    def start_next_task(self):
        """
        start next task
        :return: the key of the selected task
        """
        if self.isCurrent_index_tasks_finished():
            self.current_task_index +=1


    def set_started(self):
        """
        set the task to started when first trade reserve the space
        :return:
        """
        self.hasStarted = True

    def change_visual(self):
        """
        how agent visualize itself on the grid. used in server.py file in  def Agent_portrayal(agent):
        """
        if self.dry_wall_completed:
            self.visual["Color"] = "grey"
        elif self.current_trade:
            self.visual["Color"] = self.model.colors[self.current_trade]
        self.visual["text"] = len(self.current_workers)

    def test_print(self):
        print(self.available_tasks, self.isAvailableTasksSet, self.tasks[self.current_task_key], self.is_dry_wall_completed())

    # def set_current_trade(self, current_trade):
    #     """
    #     set the trade based on the task/phase
    #     :return:
    #     """
    #     self.current_trade = self.model.trades_tasks[self.current_task_key][0]

    def add_walls_to_map(self, agent, value=0):
        """
        when the whole drywall is built, the path is not open anymore for walking
        :return:
        """
        self.model.update_xymap(agent.pos, value)

    def step(self):
        """
        executed at each step by the schedular (the model). Other option is to define what should be done during each step in the model
        (can be safer option if the actiavation method of agents matter)
        i.e. the all the worker first should move , then all the worker should work  then the drywalls should generate tasks
        if the activation is made by step  function then the activation will not consider agent type
        """
        if self.isNewVisual:
            self.change_visual()
            self.isNewVisual = False

        if not self.dry_wall_completed:
            if self.isAvailableTasksSet:
                # self.reduce_amount() # task reduce amount by itself
                if self.tasks[self.current_task_key]["amount"] <= 0:
                    self.set_task_finished()
                    if self.is_dry_wall_completed():
                        self.set_dry_wall_completed()
                        self.model.increase_completed_drywall()
                        if self.available_tasks:
                            self.select_task()
                        else:
                            self.current_task_key = None
                        self.add_walls_to_map(self)
                        for dummy_drywall in self.model.dummy_drywalls_agents[self.name]:
                            self.add_walls_to_map(dummy_drywall)
                        #todo:set current_task_key to none

            elif not self.isAvailableTasksSet:
                self.start_next_task()
                self.set_available_task()
                if self.available_tasks:
                    current_task_key = self.select_task()
                    self.set_task_aquired(current_task_key)
                    # self.available_tasks = [current_task_key]
                    # self.set_current_trade()
                    self.isNewVisual = True
        # print(self.available_tasks, self.isAvailableTasksSet, self.tasks[self.current_task_key], self.is_dry_wall_completed())

