import math
import mesa

class DummyDrywall(mesa.Agent):
    """
    DummyDrywall class
    """

    def __init__(
            self,
            unique_id,
            model,
            pos,
            drywall,
            name,
            moore=False
    ):
        super().__init__(unique_id, model)
        self.pos = pos
        self.moore = moore
        self.drywall = drywall
        self.isNewVisual = True
        self.visual = {
            "Shape": "rect",  # # "circle",  "arrowHead"        "r": 3,
            "Filled": "true",
            # "r": 1,
            "Layer": 11,
            "Color": "white",
            "w": 1,
            "h": 1,
            "text": "",
            "text_color": "black",
            "heading_x": 0,
            "heading_y": 1,
            "scale": 1
        }
        self.model = model
        self.name = name

    def change_visual(self):
        """
        how agent visualize itself on the grid. used in server.py file in  def Agent_portrayal(agent):
        """
        # todo: check why copy is needed here
        self.visual = self.drywall.visual.copy()


    def step(self):
        """
        executed at each step by the schedular (the model). Other option is to define what should be done during each step in the model
        (can be safer option if the actiavation method of agents matter)
        i.e. the all the worker first should move , then all the worker should work  then the drywalls should generate tasks
        if the activation is made by step  function then the activation will not consider agent type
        """
        if self.isNewVisual:
            self.change_visual()
            self.isNewVisual = True
        # self.model.print_object_attributes(self)

