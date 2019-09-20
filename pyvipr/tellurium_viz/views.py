from pyvipr.viz import Viz

__all__ = [
    'sp_view',
    'sp_rxns_view',
    'sp_comm_louvain_view',
    'sp_dyn_view',
    'sp_comm_greedy_view',
    'sp_comm_asyn_lpa_view',
    'sp_comm_label_propagation_view',
    'sp_comm_girvan_newman_view',
    'sp_comm_asyn_fluidc_view'
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


def sp_comm_louvain_view(model, layout_name='klay', random_state=None):
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
    return Viz(data=model, type_of_viz='sp_comm_louvain_view', random_state=random_state, layout_name=layout_name)


def sp_comm_greedy_view(model, layout_name='klay'):
    """
    Render a visualization of the interactions between the species in a model.
    The species nodes are grouped by the communities detected by the
    Clauset-Newman-Moore greedy modularity maximization algorithm
    implemented in Networkx

    Parameters
    ----------
    model: pysb.model or str
        Model to visualize. It can be a pysb model, or the file path to an
        an SBML or BNGL model
    layout_name: str
        Layout to use

    Returns
    -------

    """
    return Viz(data=model, type_of_viz='sp_comm_greedy_view', layout_name=layout_name)


def sp_comm_asyn_lpa_view(model, random_state=None, layout_name='klay'):
    """
    Render a visualization of the interactions between the species in a model.
    The species nodes are grouped by the communities detected by the
    asynchronous label propagation algorithm implemented in Networkx.

    Parameters
    ----------
    model: pysb.model or str
        Model to visualize. It can be a pysb model, or the file path to an
        an SBML or BNGL model
    layout_name: str
        Layout to use
    random_state: int
        Random state seed use by the community detection algorithm

    Returns
    -------

    """
    return Viz(data=model, type_of_viz='sp_comm_asyn_lpa_view', layout_name=layout_name,
               random_state=random_state)


def sp_comm_label_propagation_view(model, layout_name='klay'):
    """
    Render a visualization of the interactions between the species in a model.
    The species nodes are grouped by the communities detected by the
    label propagation algorithm implemented in Networkx.

    Parameters
    ----------
    model: pysb.model or str
        Model to visualize. It can be a pysb model, or the file path to an
        an SBML or BNGL model
    layout_name: str
        Layout to use

    Returns
    -------

    """
    return Viz(data=model, type_of_viz='sp_comm_label_propagation_view', layout_name=layout_name)


def sp_comm_girvan_newman_view(model, layout_name='klay'):
    """
    Render a visualization of the interactions between the species in a model.
    The species nodes are grouped by the communities detected by the
    Girvan-Newman method implemented in Networkx.

    Parameters
    ----------
    model: pysb.model or str
        Model to visualize. It can be a pysb model, or the file path to an
        an SBML or BNGL model
    layout_name: str
        Layout to use

    Returns
    -------

    """
    return Viz(data=model, type_of_viz='sp_comm_girvan_newman_view', layout_name=layout_name)


def sp_comm_asyn_fluidc_view(model, k, max_iter=100, seed=None, layout_name='fcose'):
    """
    Render a visualization of the interactions between the species in a model.
    The species nodes are grouped by the communities detected by the
    asynchronous label propagation algorithm implemented in Networkx.

    Parameters
    ----------
    model: pysb.model or str
        Model to visualize. It can be a pysb model, or the file path to an
        an SBML or BNGL model
    k: int
        The number of communities to be found
    max_iter: int
        The number of maximum iterations allowed
    random_state: int
        Random state seed use by the community detection algorithm
    layout_name: str
        Layout to use

    Returns
    -------

    """
    from pyvipr.tellurium_viz.static_viz import TelluriumStaticViz
    tviz = TelluriumStaticViz(model)
    data = tviz.sp_comm_asyn_fluidc_view(k, max_iter, seed)
    return Viz(data=data, type_of_viz='', layout_name=layout_name)
