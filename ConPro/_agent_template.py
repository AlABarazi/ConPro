import mesa


class AgentName(mesa.Agent):
    """
    Sugar:
    - contains an amount of sugar
    - grows 1 amount of sugar at each turn
    """
    sugar_dic = {4: "#005C00", 3: "#008300", 2: "#00AA00", 1: "#00F800", '0':"#D6F5D6"}
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.isNewVisual = True
        self.pos = pos
        self.visual = {
            "Shape": "arrowHead",  # # "circle",  "arrowHead"        "r": 3,
            "Filled": "true",
            "r": 1,
            "Layer": 11,
            "Color": "yellow",
            # "w": 2,
            # "h": 2,
            "text": "",
            "text_color": "black",
            "heading_x": 0,
            "heading_y": 1, # up -1 down and x should be 0
            "scale": 1# if you want to use scale you should not used w and h
        }


    def change_visual(self):
        """
        how agent visualize itself on the grid. used in server.py file in  def Agent_portrayal(agent):
        """
        self.visual["Color"] = self.sugar_dic[self.amount]


    def step(self):
        """
        Sugar growth function, adds one unit of sugar each step until
        max amount
        """
        #####
        #
        #   Visualize
        #
        #####
        if self.isNewVisual:
            self.change_visual()
            self.isNewVisual = False

