from pysbjupyter.static_viz import StaticViz
from pysbjupyter.dynamic_viz import ModelVisualization
from pysb.core import Model
from pysb.simulator.base import SimulationResult
from pysb.importers.bngl import model_from_bngl
from pysb.importers.sbml import model_from_sbml, model_from_biomodels
import os


def data_to_json(value, widget):

    if isinstance(value, Model):
        viz = StaticViz(value)

    elif isinstance(value, str):
        file_extension = os.path.splitext(value)[1]
        if file_extension == '.bngl':
            model = model_from_bngl(value)
        elif file_extension == '.sbml':
            model = model_from_sbml(value)
        elif value.startswith('BIOMD'):
            model = model_from_biomodels(value)
        else:
            raise ValueError('Format not supported')
        viz = StaticViz(model)

    elif isinstance(value, SimulationResult):
        viz = ModelVisualization(value)

    else:
        raise TypeError('Only Model and SimulationResult are supported')

    try:
        jsondata = getattr(viz, widget.type_of_viz)()
    except AttributeError:
        raise AttributeError('Type of visualization not defined')
    return jsondata




