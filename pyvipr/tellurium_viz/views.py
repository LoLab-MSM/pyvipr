from pyvipr.viz import Viz

__all__ = [
    'sp_view',
    'sp_comm_view',
    'sp_dyn_view'
]


def sp_view(model, layout_name='cose-bilkent'):
    """
    Render a visualization of the interactions between the species in a model.

    Parameters
    ----------
    model: pysb.model or str
        Model to visualize. It can be a pysb model, or the file path to an
        an SBML or BNGL model
    layout_name: str
        Layout to use

    """

    return Viz(data=model, type_of_viz='sp_view', layout_name=layout_name)


def sp_dyn_view(simulation, process='consumption', layout_name='cose-bilkent'):
    """
    Render a dynamic visualization of the simulation

    Parameters
    ----------
    simulation : pysb.SimulationResult
        Simulation result to visualize
    process : str
        Type of the dynamic visualization, it can be 'consumption' or 'production'
    layout_name : str
        Layout to use

    """
    return Viz(data=simulation, type_of_viz='dynamic_sp_view', layout_name=layout_name,
               process=process)


def sp_comm_view(model, layout_name='klay', random_state=None):
    """
    Render a visualization of the interactions between the species in a model.
    The species nodes are grouped by the communities detected by the
    Louvain algorithm: https://en.wikipedia.org/wiki/Louvain_Modularity.

    Parameters
    ----------
    model: pysb.model or str
        Model to visualize. It can be a pysb model, or the file path to an
        an SBML or BNGL model
    layout_name: str
        Layout to use
    random_state: int
        Random state seed use by the community detection algorithm

    """
    return Viz(data=model, type_of_viz='sp_comm_view', random_state=random_state, layout_name=layout_name)
