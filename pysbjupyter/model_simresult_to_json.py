from pysbjupyter.static_viz import StaticViz
from pysbjupyter.dynamic_viz import ModelVisualization
from pysb.core import Model
from pysb.simulator.base import SimulationResult


def data_to_json(_, widget):
    if isinstance(widget.data, Model):
        viz = StaticViz(widget.data)
        jsondata = viz.species_view()
        return jsondata
    elif isinstance(widget.data, SimulationResult):
        viz = ModelVisualization(widget.data)
        jsondata = viz.dynamic_view(get_passengers=False)
        return jsondata
    else:
        raise TypeError('Only Model and SimulationResult are supported')


