from pysbjupyter.static_viz import StaticViz
from pysbjupyter.dynamic_viz import ModelVisualization
from pysb.core import Model
from pysb.simulator.base import SimulationResult
from pysb.importers.bngl import model_from_bngl
from pysb.importers.sbml import model_from_sbml, model_from_biomodels
import os


def data_to_json(_, widget):
    if isinstance(widget.data, Model):
        viz = StaticViz(widget.data)

    elif isinstance(widget.data, str):
        file_extension = os.path.splitext(widget.data)[1]
        if file_extension == '.bngl':
            model = model_from_bngl(widget.data)
        elif file_extension == '.sbml':
            model = model_from_sbml(widget.data)
        elif widget.data.startswith('BIOMD'):
            model = model_from_biomodels(widget.data)
        else:
            raise ValueError('Format not supported')
        viz = StaticViz(model)

    elif isinstance(widget.data, SimulationResult):
        viz = ModelVisualization(widget.data)

    elif isinstance(widget.data, dict):
        return widget.data

    else:
        raise TypeError('Only Model and SimulationResult are supported')

    try:
        jsondata = getattr(viz, widget.type_of_viz)()
    except AttributeError:
        raise AttributeError('Type of visualization not defined')
    return jsondata




