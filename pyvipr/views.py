from .pysbviz import pysbViz

__all__ = [
    'sp_view',
    'sp_comp_view',
    'sp_comm_view',
    'sp_comm_hierarchy_view',
    'sp_rxns_bidirectional_view',
    'sp_rxns_view',
    'sp_rules_view',
    'sp_rules_fxns_view',
    'sp_rules_mod_view',
    'projected_species_reactions_view',
    'projected_reactions_view',
    'projected_rules_view',
    'projected_species_rules_view',
    'sp_dyn_view',
    'sp_comp_dyn_view',
    'sp_comm_dyn_view',
    'sim_model_dyn_view',
    'nx_graph_view',
    'nx_graph_dyn_view',
    'sbgn_view'
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

    return pysbViz(data=model, type_of_viz='sp_view', layout_name=layout_name)


def sp_comp_view(model, layout_name='cose-bilkent'):
    """
    Render a visualization of the interactions between the species in a model.
    The species nodes are grouped by the compartments they belong to.

    Parameters
    ----------
    model: pysb.model or str
        Model to visualize. It can be a pysb model, or the file path to an
        an SBML or BNGL model
    layout_name: str
        Layout to use

    """
    return pysbViz(data=model, type_of_viz='sp_comp_view', layout_name=layout_name)


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
    return pysbViz(data=model, type_of_viz='sp_comm_view', random_state=random_state, layout_name=layout_name)


def sp_comm_hierarchy_view(model, layout_name='klay', random_state=None):
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
    return pysbViz(data=model, type_of_viz='sp_comm_hierarchy_view', random_state=random_state, layout_name=layout_name)


def sp_rxns_bidirectional_view(model, layout_name='cose-bilkent'):
    """
    Render a visualization of a bipartite graph where one set of nodes
    are the molecular species in the model and the other set are the
    bidirectional reactions.

    Parameters
    ----------
    model: pysb.model or str
        Model to visualize. It can be a pysb model, or the file path to an
        an SBML or BNGL model
    layout_name: str
        Layout to use

    """
    return pysbViz(data=model, type_of_viz='sp_rxns_bidirectional_view', layout_name=layout_name)


def sp_rxns_view(model, layout_name='cose-bilkent'):
    """
    Render a visualization of a bipartite graph where one set of nodes
    are the molecular species in the model and the other set are the
    unidirectional reactions.

    Parameters
    ----------
    model: pysb.model or str
        Model to visualize. It can be a pysb model, or the file path to an
        an SBML or BNGL model
    layout_name: str
        Layout to use

    """
    return pysbViz(data=model, type_of_viz='sp_rxns_view', layout_name=layout_name)


def sp_rules_view(model, layout_name='cose-bilkent'):
    """
    Render a visualization of a bipartite graph where one set of nodes
    are the molecular species in the model and the other set are the rules.

    Parameters
    ----------
    model: pysb.model or str
        Model to visualize. It can be a pysb model, or the file path to an
        an SBML or BNGL model
    layout_name: str
        Layout to use

    """
    return pysbViz(data=model, type_of_viz='sp_rules_view', layout_name=layout_name)


def sp_rules_fxns_view(model, layout_name='cose-bilkent'):
    """
    Render a visualization of a bipartite graph where one set of nodes
    are the molecular species in the model and the other set are the rules.
    Additionally, rules are grouped by the macros that created them.

    Parameters
    ----------
    model: pysb.model or str
        Model to visualize. It can be a pysb model, or the file path to an
        an SBML or BNGL model
    layout_name: str
        Layout to use

    """
    return pysbViz(data=model, type_of_viz='sp_rules_fxns_view', layout_name=layout_name)


def sp_rules_mod_view(model, layout_name='cose-bilkent'):
    """
    Render a visualization of a bipartite graph where one set of nodes
    are the molecular species in the model and the other set are the rules.
    Additionally, rules are grouped by the modules where they are defined.

    Parameters
    ----------
    model: pysb.model or str
        Model to visualize. It can be a pysb model, or the file path to an
        an SBML or BNGL model
    layout_name: str
        Layout to use

    """
    return pysbViz(data=model, type_of_viz='sp_rules_mod_view', layout_name=layout_name)


def projected_species_reactions_view(model, layout_name='cose-bilkent'):
    """
    Render a visualization of the interactions between species in a model.

    Parameters
    ----------
    model: pysb.model or str
        Model to visualize. It can be a pysb model, or the file path to an
        an SBML or BNGL model
    layout_name: str
        Layout to use

    """
    return pysbViz(data=model, type_of_viz='projected_species_reactions_view', layout_name=layout_name)


def projected_reactions_view(model, layout_name='cose-bilkent'):
    """
    Render a visualization of the interaction between the reaction in a model

    Parameters
    ----------
    model: pysb.model or str
        Model to visualize. It can be a pysb model, or the file path to an
        an SBML or BNGL model
    layout_name: str
        Layout to use

    """
    return pysbViz(data=model, type_of_viz='projected_reactions_view', layout_name=layout_name)


def projected_rules_view(model, layout_name='cose-bilkent'):
    """
    Render a visualization of the interactions between rules in a model.

    Parameters
    ----------
    model: pysb.model or str
        Model to visualize. It can be a pysb model, or the file path to an
        an SBML or BNGL model
    layout_name: str
        Layout to use

    """
    return pysbViz(data=model, type_of_viz='projected_rules_view', layout_name=layout_name)


def projected_species_rules_view(model, layout_name='cose-bilkent'):
    """
    Render a visualization of a bipartite graph where one set of nodes
    are the molecular species in the model and the other set are the rules.

    Parameters
    ----------
    model: pysb.model or str
        Model to visualize. It can be a pysb model, or the file path to an
        an SBML or BNGL model
    layout_name: str
        Layout to use

    """
    return pysbViz(data=model, type_of_viz='projected_species_rules_view', layout_name=layout_name)


def sbgn_view(model, layout_name='cose-bilkent'):
    return pysbViz(data=model, type_of_viz='sbgn_view', layout_name=layout_name)


def sp_dyn_view(simulation, sim_idx=0, process='consumption', layout_name='cose-bilkent'):
    """
    Render a dynamic visualization of the simulation

    Parameters
    ----------
    simulation : pysb.SimulationResult
        Simulation result to visualize
    sim_idx : int
        Index of simulation to be visualized
    process : str
        Type of the dynamic visualization, it can be 'consumption' or 'production'
    layout_name : str
        Layout to use

    """
    return pysbViz(data=simulation, type_of_viz='dynamic_sp_view', layout_name=layout_name,
                   process=process, sim_idx=sim_idx)


def sp_comp_dyn_view(simulation, sim_idx=0, process='consumption', layout_name='cose-bilkent'):
    """
    Render a dynamic visualization of the simulation. The species nodes are grouped
    by the compartments they belong to.

    Parameters
    ----------
    simulation: pysb.SimulationResult object
        Simulation result to visualize dynamically
    sim_idx: int
        Index of simulation to be visualized
    process : str
        Type of the dynamic visualization, it can be 'consumption' or 'production'
    layout_name: str
        Layout to use

    """
    return pysbViz(data=simulation, type_of_viz='dynamic_sp_comp_view', layout_name=layout_name,
                   process=process, sim_idx=sim_idx)


def sp_comm_dyn_view(simulation, sim_idx=0, process='consumption', layout_name='klay', random_state=None):
    """
    Render a dynamic visualization of the simulation. The species nodes are grouped
    by the communities detected by the Louvain algorithm

    Parameters
    ----------
    simulation: pysb.SimulationResult object
        Simulation result to visualize dynamically
    sim_idx: int
        Index of simulation to be visualized
    process : str
        Type of the dynamic visualization, it can be 'consumption' or 'production'
    layout_name: str
        Layout to use
    random_state: int
        Random state seed use by the community detection algorithm

    """
    return pysbViz(data=simulation, type_of_viz='dynamic_sp_comm_view', layout_name=layout_name,
                   random_state=random_state, process=process, sim_idx=sim_idx)


def sim_model_dyn_view(model, tspan, param_values=None, type_of_viz='dynamic_view',
                       process='consumption', layout_name='cose-bilkent'):
    """
    Render a dynamic visualization of the model using the tspan and param_values
    passed to the function

    Parameters
    ----------
    model: pysb.model or str
        Model to visualize. It can be a pysb model, or the file path to an
        an SBML or BNGL model
    tspan : vector-like, optional
        Time values over which to simulate. The first and last values define
        the time range.
    param_values : vector-like or dict, optional
        Values to use for every parameter in the model. Ordering is
        determined by the order of model.parameters.
        If passed as a dictionary, keys must be parameter names.
        If not specified, parameter values will be taken directly from
        model.parameters.
    type_of_viz: str
        Type of visualization. It can only be `sp_dyn_view`, `sp_comp_dyn_view`
        or `sp_comm_dyn_view`
    process : str
        Type of the dynamic visualization, it can be 'consumption' or 'production'
    layout_name : str
        Layout name to use

    """
    from pysb.simulator import ScipyOdeSimulator
    from pyvipr.util import dispatch_pysb_files

    model = dispatch_pysb_files(model)
    sim = ScipyOdeSimulator(model, tspan=tspan).run(param_values=param_values)
    return pysbViz(data=sim, type_of_viz=type_of_viz, process=process, layout_name=layout_name)


def nx_graph_view(graph, layout_name='cose'):
    """
    Render a networkx Graph or DiGraph

    Parameters
    ----------
    graph: nx.Graph or nx.DiGraph
        Graph to render
    layout_name: str
        Layout to use

    Returns
    -------

    """
    return pysbViz(data=graph, type_of_viz='network_static_view', layout_name=layout_name)


def nx_graph_dyn_view(graph, tspan, node_rel=None, node_tip=None, edge_colors=None, edge_sizes=None,
                      edge_tips=None, layout_name='cose'):
    """
    Render a dynamic visualization of a networkx graph

    Parameters
    ----------
    graph: nx.DiGraph or nx.Graph
    tspan: vector-like, optional
        Time values over which to simulate. The first and last values define
    node_rel: dict
        A dictionary where the keys are the node ids and the values are
        lists that contain (0-100) values that are represented in a
        pie chart within the node
    node_tip: dict
        A dictionary where the keys are the node ids and the values are
        lists that contain any value that can be accessed
        as a tooltip in the rendered network
    edge_colors: dict
        A dictionary where the keys are the edge ids and the values are
        lists that contain any hexadecimal color value that are
        represented in the edge colors
    edge_sizes: dict
        A dictionary where the keys are the edge ids and the values are
        lists that contain any numerical value that are
        represented in the edge size
    edge_tips: dict
        A dictionary where the keys are the edge ids and the values are
        lists that contain any value that can be accessed
        as a tooltip in the rendered network
    layout_name: str
        Layout to use

    """
    from pyvipr.util_networkx import network_dynamic_data

    network_dynamic_data(graph, tspan, node_rel, node_tip, edge_colors, edge_sizes,
                         edge_tips)

    return pysbViz(data=graph, type_of_viz='dynamic_network_view', layout_name=layout_name)
