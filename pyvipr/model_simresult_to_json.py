from pyvipr.static_viz import StaticViz
from pyvipr.dynamic_viz import ModelVisualization
from pysb.core import Model
from pysb.simulator.base import SimulationResult
from pysb.importers.bngl import model_from_bngl
from pysb.importers.sbml import model_from_sbml, model_from_biomodels
import os


def data_to_json(value, widget):
    """
    Generate a json file from the data passed to the widget
    Parameters
    ----------
    value: pysb.Model, pysb.SimulationResult, str
        Value passed to the widget that is going to be visualized
    widget: Widget
        Widget instance

    Returns
    -------

    """
    if isinstance(value, (Model, str)):
        viz = dispatch_pysb_files(value)
        try:
            if widget.type_of_viz == 'communities_view':
                rs = widget.random_state
                jsondata = getattr(viz, widget.type_of_viz)(random_state=rs)
            else:
                jsondata = getattr(viz, widget.type_of_viz)()
        except AttributeError:
            raise AttributeError('Type of static visualization not defined')
        return jsondata

    elif isinstance(value, SimulationResult):
        viz = ModelVisualization(value, widget.sim_idx)
        process = widget.process
        try:
            if widget.type_of_viz == 'dynamic_communities_view':
                rs = widget.random_state
                jsondata = getattr(viz, widget.type_of_viz)(random_state=rs, type_viz=process)
            else:
                jsondata = getattr(viz, widget.type_of_viz)(type_viz=process)
        except AttributeError:
            raise AttributeError('Type of visualization not defined')
        return jsondata
    else:
        raise TypeError('Only Model and SimulationResult are supported')


def dispatch_pysb_files(value):
    functions = {'str': _handle_model_files, 'pysb.core.Model': _handle_pysb_model}
    data_type = str(type(value)).split("'")[1]
    result = functions[data_type](value)
    return result


def _handle_model_files(value):
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
    return viz


def _handle_pysb_model(value):
    return StaticViz(value)








