import mesa


class ZoneLabel(mesa.Agent):
    """
    Zone agent represent distinctive zone worker go to
    Zone has two types of people in it: Workers are doing work inside the zone, visitors visit the zone from time to time i.e. check something or searching
    Total number of people = visitors + workers
    The zone may allow one or more trade to work in at the same time. The number of trades can be set
    """
    zones_colors={'storage204': '#94FAF1', 'A6': '#7AA988', 'A3': '#884E16', 'A7': '#02E974', 'storage201': '#AEC8DF', 'elevator': '#5A0BB9', 'A4': '#0BFBA9', 'A8': '#530F51', 'staircase': '#C0AECA', 'A5': '#1B2A74'}
    def __init__(self, unique_id, model, pos, name):
        super().__init__(unique_id, model)
        self.isNewVisual = True
        self.pos = pos
        self.name = name
        self.visual = {
            "Color": "yellow",
            "Shape": "rect",
            "Filled": "true",
            "Layer": 10000,
            "w": 2,
            "h": 2,
            "scale":20,
        "text":self.name, #len(self.current_visitors),
        "text_color":"red",
            # "heading_x":1,
            # "heading_y":1
        }
 
    # def total_workers(self):
    #     """
    #     Total indivisuals in this zone including those who are working in it and those who just visit the space
    #     :return:
    #     """
    #     return len(self.current_workers) + len(self.current_visitors)
    #
    # def is_total_full(self):
    #     """
    #     check if the number of total is less than maximum
    #     :return:
    #     """
    #     total = self.total_workers()
    #     return total == self.max_trades
    #
    # def is_visitors_full(self):
    #     """
    #     check if the number of current_visitors are less than maximum
    #     :return:
    #     """
    #     return len(self.current_visitors) == self.max_visitor
    #
    # def is_trades_full(self):
    #     """
    #     check if the number of trades is less than maximum
    #     :return:
    #     """
    #     return len(self.current_trades) == self.max_trades
    #
    # def is_workers_full(self):
    #     """
    #     check if the number of worker is less than maximum
    #     :return:
    #     """
    #     return len(self.current_workers) == self.max_worker
    #
    # def add_trade(self, trade):
    #     """
    #     add trade to space
    #     :param trade: agent of type trade
    #     """
    #     if trade not in self.current_trades:
    #         self.current_trades.add(trade)
    #     self.isNewVisual = True
    #
    # def remove_trade(self, trade):
    #     if trade in self.current_trades:
    #         self.current_trades.remove(trade)
    #     self.isNewVisual = True
    #
    # def add_worker(self, worker):
    #     """
    #     add worker to space
    #     :param worker: agent of type worker
    #     """
    #     if worker not in self.current_workers:
    #         self.current_workers.add(worker)
    #     self.isNewVisual = True
    #
    # def remove_worker(self, worker):
    #     if worker in self.current_workers:
    #         self.current_workers.remove(worker)
    #     self.isNewVisual = True
    #
    # def add_visitor_to_space(self, visitor):
    #     """
    #     add visitor to space
    #     :param visitor: agent of type worker
    #     """
    #     if visitor not in self.current_visitors:
    #         self.current_visitors.add(visitor)
    #     self.isNewVisual = True
    #
    # def remove_visitor_from_space(self, visitor):
    #     if visitor in self.current_visitors:
    #         self.current_visitors.remove(visitor)
    #     self.isNewVisual = True
    #
    #
    # def change_visual(self):
    #     """
    #     how agent visualize itself on the grid. used in server.py file in  def Agent_portrayal(agent):
    #     """
    #     self.visual["text"] = len(self.current_visitors)
    #
    #
    # def step(self):
    #     """
    #     executed at each step by the schedular (the model). Other option is to define what should be done during each step in the model
    #     (can be safer option if the actiavation method of agents matter)
    #     i.e. the all the worker first should move , then all the worker should work  then the drywalls should generate tasks
    #     if the activation is made by step  function then the activation will not consider agent type
    #     """
    #     if self.isNewVisual:
    #         self.change_visual()
    #         self.isNewVisual = True
