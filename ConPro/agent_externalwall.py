import mesa
import random

class ExternalWall(mesa.Agent):
    """
    This agent represent the inner wall on the plan
    In the futur, this agent can be a child to parent class Wall 
    """

    def __init__(self, unique_id, model, pos):
        """
         Intialization of this class Inner Wall
        :param unique_id: unique_id passed to this when intializing new agent (creation)
        :param model: model object passed to this when intializing/create new agent of inner wall
        :param pos: pos  passed to this when intializing/create new agent of inner wall
        """
        super().__init__(unique_id, model)
        """
        Intialization of parent class (mesa.Agent)
        """
        self.isNewVisual = True
        self.pos = pos
        self.visual = {
            "Color": "grey",
            "Shape": "rect",
            "Filled": "true",
            "Layer": 10,
            "w": 1,
            "h": 1,
            "text":self.pos[0] if self.pos[1] == 0 else self.pos[1] if self.pos[0] == 0 else "",
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
