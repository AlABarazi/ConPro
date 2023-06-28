import mesa


class Route(mesa.Agent):
    """
    This agent represent grids that act as path
    These grids may be useful in the futur, for now they are turned off so they are not created in the model
    """
    
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.isNewVisual = True
        self.pos = pos
        self.visual = {
            "Color": "blue",
            "Shape": "rect",
            "Filled": "true",
            "Layer": 10,
            "w": 1,
            "h": 1,
        "text":"",
        "text_color":"black",
            "heading_x":1,
            "heading_y":1
        }

    def change_visual(self):
        """
        how agent visualize itself on the grid. used in server.py file in  def Agent_portrayal(agent):
        """
        pass

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
