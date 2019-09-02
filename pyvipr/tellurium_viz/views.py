from pyvipr.viz import Viz

__all__ = [
    'sp_view',
    'sp_rxns_view',
    'sp_comm_view',
    'sp_dyn_view'
]


def sp_view(model, layout_name='cose-bilkent'):
    """
    Render a visualization of the interactions between the species in a model.

    Parameters
    ----------
    model: tellurium model
        Model to visualize.
        an SBML or BNGL model
    layout_name: str
        Layout to use

    """

    return Viz(data=model, type_of_viz='sp_view', layout_name=layout_name)


def sp_rxns_view(model, layout_name='cose-bilkent'):
    """
    Render a visualization of the interactions between the species and reactions in a model.

    Parameters
    ----------
    model: tellurium model
        Model to visualize.
        an SBML or BNGL model
    layout_name: str
        Layout to use

    """

    return Viz(data=model, type_of_viz='sp_rxns_view', layout_name=layout_name)


def sp_dyn_view(simulation, process='consumption', layout_name='cose-bilkent', cmap='RdBu_r'):
    """
    Render a dynamic visualization of the simulation

    Parameters
    ----------
    simulation : tellurium simulation
        Simulation to visualize
    process : str
        Type of the dynamic visualization, it can be 'consumption' or 'production'
    layout_name : str
        Layout to use
    cmap : str or Colormap instance
        The colormap used to map the reaction rate values to RGBA colors. For more information
        visit: https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html

    """
    return Viz(data=simulation, type_of_viz='dynamic_sp_view', layout_name=layout_name,
               process=process, cmap=cmap)


def sp_comm_view(model, layout_name='klay', random_state=None):
    """
    Render a visualization of the interactions between the species in a model.
    The species nodes are grouped by the communities detected by the
    Louvain algorithm: https://en.wikipedia.org/wiki/Louvain_Modularity.

    Parameters
    ----------
    model: tellurium model
        Model to visualize.
    layout_name: str
        Layout to use
    random_state: int
        Random state seed use by the community detection algorithm

    """
    return Viz(data=model, type_of_viz='sp_comm_view', random_state=random_state, layout_name=layout_name)
