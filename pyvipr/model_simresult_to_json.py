from pyvipr.dynamic_viz import DynamicViz
from pyvipr.network_viz import NetworkViz
from pyvipr.static_viz import StaticViz
from pyvipr.util import dispatch_pysb_files
from pysb.core import Model
from pysb.simulator.base import SimulationResult
from networkx import Graph, DiGraph


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
    try:
        model = dispatch_pysb_files(value)
        viz = StaticViz(model)
        try:
            if widget.type_of_viz in ['sp_comm_view', 'sp_comm_hierarchy_view']:
                rs = widget.random_state
                jsondata = getattr(viz, widget.type_of_viz)(random_state=rs)
            else:
                jsondata = getattr(viz, widget.type_of_viz)()
        except AttributeError:
            raise AttributeError('Type of static visualization not defined')
        return jsondata
    except KeyError:
        pass
    try:
        viz = DynamicViz(value, widget.sim_idx)
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
    except TypeError:
        pass
    try:
        viz = NetworkViz(value)
        jsondata = getattr(viz, widget.type_of_viz)()
        return jsondata
    except AttributeError:
        pass
    finally:
        raise TypeError('Only pysb Model, pysb SimulationResult, tellurium Model, '
                        'PySCeS Model, and networkx graphs are supported')
