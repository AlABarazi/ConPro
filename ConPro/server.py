import mesa
from .model import ConPro
from mesa.visualization.modules import TextElement, CanvasGrid, ChartModule, BarChartModule
from mesa.visualization.ModularVisualization import ModularServer
# from mesa.visualization.UserParam import UserSettableParameter
from random import randrange

def Agent_portrayal(agent):
    if agent is None:
        return
    else:
        return agent.visual
# model_params = {}


params_list = ["w_presence", "n_plastering_workers", "n_painting_workers", "zone_max_worker", "zone_max_trades",
               "KEYSTART_max","KEYFRAMES_max","KEYMECH_max","KEYELEC_max", "KEYINSU_max", "KEYSTUD_max", "KEYPAINTING_max",  "KEYFINISHING_max",
               "KEYEND_max"]

model_params = {key:(mesa.visualization.NumberInput( key, value=1)) for key in params_list }

model_params["work_duration"] = mesa.visualization.NumberInput( "work_duration", value=0.4) # 1500000 1.5 sec # 15000000 15 sec
model_params["work_duration_min"] = mesa.visualization.NumberInput( "work_duration_min", value=0.1) # 1500000 1.5 sec # 15000000 15 sec
model_params["work_duration_max"] = mesa.visualization.NumberInput( "work_duration_max", value=0.6) # 1500000 1.5 sec # 15000000 15 se
model_params["simulation_speed_microsec"] = mesa.visualization.NumberInput( "simulation_speed_microsec", value=1500000) # 1500000 1.5 sec # 15000000 15 sec
model_params["seed"] = mesa.visualization.NumberInput( "seed", value=randrange(4294967294))
# model_params["one_behavior_file"] = mesa.visualization.Checkbox( "one_behavior_file", value=True)
canvas_element = mesa.visualization.CanvasGrid(Agent_portrayal, ConPro.width, ConPro.height, ConPro.width*10, ConPro.height*10)

class ShowSomeText(TextElement):
    """
    render the text (site info) on top of canvas visualization
    """
    def __init__(self):
        pass
    def render(self, model):  # access model to render it’s variables
        return "{1}{2}{3}{4}{5}".format(
            "Date " + model.current_datetime.strftime("%d/%m/%Y, %H:%M:%S") + "<br>",
            "Today is " + model.weekdays[model.current_datetime.weekday()] + "<br>",
            str('{:04.1f} minutes passed today'.format(model.get_today_minutes())) + "<br>",
            "Week # " + model.this_week + "<br>",
            "Status # " + model.status + "<br>",
            "Completed drywalls " + str(model.get_completed_drywalls()) + "<br>",
            "CoBr St " + str(model.coffe_break_start) + "<br>",
            "pssd_wrk_t" + str(model.passed_working_time)
        )
        # + str('{:04.1f}'.format(model.get_days()))+" days passed" + "<br>"\
    # + "This Day Start At "+ model.this_day_start_date.strftime("%d/%m/%Y, %H:%M:%S") +"<br>"\
    # + "Project Start Date " + model.project_startdate.strftime("%d/%m/%Y, %H:%M:%S") +"<br>"\


####################
#
#       Charts
#
####################
tasks_bars = [{"Label": key, "Color": ConPro.colors[value[0]]} for key,value in ConPro.trades_tasks_keys.items()]

text_element = ShowSomeText()
# chart_element = ChartModule(
#     [{"Label": "Trade", "Color": "#AA0000"}]
# )

chart_element2 = BarChartModule(
    [
        {"Label": "Utilization", "Color": "#000000"},
     {"Label": "Idle", "Color": "blue"}

     ]
)
chart_element3 = BarChartModule(tasks_bars)




server = ModularServer(
    ConPro,
    #[text_element, canvas_element, chart_element, chart_element2, chart_element3 ],
[text_element, canvas_element, chart_element2, chart_element3 ],
    "ConPro",
    model_params=model_params
)
server.verbose = False
# server.launch()

# Parameter types include:
# ‘number’ - a simple numerical input
#
# ‘checkbox’ - boolean checkbox
#
# ‘choice’ - String-based dropdown input, for selecting choices within a model
#
# ‘slider’ - A number-based slider input with settable increment
#
# ‘static_text’ - A non-input textbox for displaying model info.
#
# Examples:
#
# # Simple number input number_option = UserSettableParameter(‘number’, ‘My Number’, value=123)
#
# # Checkbox input boolean_option = UserSettableParameter(‘checkbox’, ‘My Boolean’, value=True)
#
# # Choice input choice_option = UserSettableParameter(‘choice’, ‘My Choice’, value=’Default choice’,
#
# choices=[‘Default Choice’, ‘Alternate Choice’])
#
# # Slider input slider_option = UserSettableParameter(‘slider’, ‘My Slider’, value=123, min_value=10, max_value=200, step=0.1)
#
# # Static text static_text = UserSettableParameter(‘static_text’, value=”This is a descriptive textbox”)