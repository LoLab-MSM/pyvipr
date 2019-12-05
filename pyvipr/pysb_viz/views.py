from pyvipr.viz import Viz

__all__ = [
    'sp_view',
    'sp_comp_view',
    'sp_comm_louvain_view',
    'sp_comm_louvain_hierarchy_view',
    'sp_comm_greedy_view',
    'sp_comm_asyn_lpa_view',
    'sp_comm_label_propagation_view',
    'sp_comm_girvan_newman_view',
    'sp_comm_asyn_fluidc_view',
    'sp_rxns_bidirectional_view',
    'sp_rxns_view',
    'sp_rules_view',
    'sp_rules_fxns_view',
    'sp_rules_mod_view',
    'rules_fxns_view',
    'rules_mod_view',
    'projected_species_from_bireactions_view',
    'projected_bireactions_view',
    'projected_rules_view',
    'projected_species_from_rules_view',
    'cluster_rxns_by_rules_view',
    'sp_dyn_view',
    'sp_comp_dyn_view',
    'sp_comm_dyn_view',
    'sim_model_dyn_view',
    'sbgn_view',
    'atom_rules_view',
    'highlight_nodes_view'
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
    return Viz(data=model, type_of_viz='sp_comp_view', layout_name=layout_name)


def sp_comm_louvain_view(model, layout_name='klay', random_state=None):
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
    return Viz(data=model, type_of_viz='sp_comm_louvain_view', random_state=random_state, layout_name=layout_name)


def sp_comm_louvain_hierarchy_view(model, layout_name='klay', random_state=None):
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
    return Viz(data=model, type_of_viz='sp_comm_louvain_hierarchy_view',
               random_state=random_state, layout_name=layout_name)


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


def sp_comm_asyn_fluidc_view(model, k, max_iter=100, random_state=None, layout_name='fcose'):
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
    from pyvipr.pysb_viz.static_viz import PysbStaticViz
    pviz = PysbStaticViz(model, generate_eqs=False)
    data = pviz.sp_comm_asyn_fluidc_view(k, max_iter, random_state)
    return Viz(data=data, type_of_viz='', layout_name=layout_name)


def cluster_rxns_by_rules_view(model, layout_name='fcose'):
    """
    Render a visualization of the interactions between the reactions in a model.
    Reaction nodes are grouped by the rules that generated them.

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
    return Viz(data=model, type_of_viz='cluster_rxns_by_rules_view', layout_name=layout_name)


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
    return Viz(data=model, type_of_viz='sp_rxns_bidirectional_view', layout_name=layout_name)


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
    return Viz(data=model, type_of_viz='sp_rxns_view', layout_name=layout_name)


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
    return Viz(data=model, type_of_viz='sp_rules_view', layout_name=layout_name)


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
    return Viz(data=model, type_of_viz='sp_rules_fxns_view', layout_name=layout_name)


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
    return Viz(data=model, type_of_viz='sp_rules_mod_view', layout_name=layout_name)


def rules_fxns_view(model, layout_name='cose-bilkent'):
    """
    Render a visualization of a unipartite rules graph. Rules are grouped by the functions that created them.

    Parameters
    ----------
    model: pysb.model or str
        Model to visualize. It can be a pysb model, or the file path to an
        an SBML or BNGL model
    layout_name: str
        Layout to use

    """
    return Viz(data=model, type_of_viz='rules_fxns_view', layout_name=layout_name)


def rules_mod_view(model, layout_name='cose-bilkent'):
    """
    Render a visualization of a unipartite rules graph. Rules are grouped by the modules where they are defined.

    Parameters
    ----------
    model: pysb.model or str
        Model to visualize. It can be a pysb model, or the file path to an
        an SBML or BNGL model
    layout_name: str
        Layout to use

    """
    return Viz(data=model, type_of_viz='rules_mod_view', layout_name=layout_name)


def projected_species_from_bireactions_view(model, layout_name='cose-bilkent'):
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
    return Viz(data=model, type_of_viz='projected_species_from_bireactions_view', layout_name=layout_name)


def projected_bireactions_view(model, layout_name='cose-bilkent'):
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
    return Viz(data=model, type_of_viz='projected_bireactions_view', layout_name=layout_name)


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
    return Viz(data=model, type_of_viz='projected_rules_view', layout_name=layout_name)


def projected_species_from_rules_view(model, layout_name='cose-bilkent'):
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
    return Viz(data=model, type_of_viz='projected_species_from_rules_view', layout_name=layout_name)


def atom_rules_view(model, visualize_args, rule_name=None, verbose=False, cleanup=True, layout_name='fcose'):
    """
    Uses the BioNetGen atom-rules to visualize large rule-base models. For more
    information regarding atom-rules and its parameters please visit:
    Sekar et al (2017), Automated visualization of rule-based models
    https://doi.org/10.1371/journal.pcbi.1005857

    The visualize_args parameter contains all the arguments that will be passed to the
    BioNetGen visualize function. It is a dictionary and supports the following
    key, value pairs.

      - `type`

        * `conventional` => Conventional rule visualization
        * `compact` => Compact rule visualization (using graph operation nodes)
        * `regulatory` => Rule-derived regulatory graph
        * `opts` => Options template for regulatory graph
        * `contactmap` => Contact map
        * `reaction_network` => Reaction network
      -  `suffix`

        * str => add suffix string to output filename
      - `each`

        * 1 => Show all rules in separate GML files
        * 0 => Show all rules  the same GML file.
      - `opts`

        * file path => import options from file
      - `background`

        * 1 => Enable background
        * 0 => Disable background
      - `groups`

        * 1 => Enable groups
        * 0 => Disable groups
      - `collapse`

        * 1 => Enable collapsing of groups
        * 0 => Disable collapsing of groups
      - `ruleNames`

        * 1 => Enable display of rule names
        * 0 => Disable display of rule names
      - `doNotUseContextWhenGrouping`

        * 1 => Use permissive edge signature
        * 0 => Use strict edge signature
      - `doNotCollapseEdges`:

        * 1 => When collapsing nodes, retain duplicate edges
        * 0 => When collapsing nodes, remove duplicate edges

    Parameters
    ----------
    model: pysb.model or bngl file
        Model to visualize
    visualize_args: dict
        Contains all the arguments that will be passed to the BioNetGen visualize function.
        The following key, value pairs are available

    rule_name : str
       Name of the rule to visualize, when `each` is set to 1 in visualize_args.
    cleanup : bool, optional
        If True (default), delete the temporary files after the simulation is
        finished. If False, leave them in place. Useful for debugging.
    verbose : bool or int, optional (default: False)
        Sets the verbosity level of the logger. See the logging levels and
        constants from Python's logging module for interpretation of integer
        values. False is equal to the PySB default level (currently WARNING),
        True is equal to DEBUG.

    Returns
    -------

    """
    from pyvipr.pysb_viz.static_viz import PysbStaticViz
    from pysb.core import Model
    from pysb.importers.bngl import model_from_bngl
    if isinstance(model, Model):
        pviz = PysbStaticViz(model, generate_eqs=False)
    elif isinstance(model, str):
        pysb_model = model_from_bngl(model)
        pviz = PysbStaticViz(pysb_model, generate_eqs=False)

    else:
        raise TypeError('Only PySB and bngl models are supported')
    data = pviz.atom_rules_view(visualize_args, rule_name, verbose, cleanup)
    return Viz(data=data, type_of_viz='', layout_name=layout_name)


def highlight_nodes_view(model, species=None, reactions=None, layout_name='fcose'):
    from pyvipr.pysb_viz.static_viz import PysbStaticViz
    pviz = PysbStaticViz(model)
    data = pviz.highlight_nodes_view(species, reactions)
    return Viz(data=data, type_of_viz='', layout_name=layout_name)


def sbgn_view(model, layout_name='cose-bilkent'):
    return Viz(data=model, type_of_viz='sbgn_view', layout_name=layout_name)


def sp_dyn_view(simulation, sim_idx=0, process='consumption', layout_name='cose-bilkent', cmap='RdBu_r'):
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
    cmap : str or Colormap instance
        The colormap used to map the reaction rate values to RGBA colors. For more information
        visit: https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html

    """
    return Viz(data=simulation, type_of_viz='dynamic_sp_view', layout_name=layout_name,
               process=process, sim_idx=sim_idx, cmap=cmap)


def sp_comp_dyn_view(simulation, sim_idx=0, process='consumption', layout_name='cose-bilkent', cmap='RdBu_r'):
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
    cmap : str or Colormap instance
        The colormap used to map the reaction rate values to RGBA colors. For more information
        visit: https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html

    """
    return Viz(data=simulation, type_of_viz='dynamic_sp_comp_view', layout_name=layout_name,
               process=process, sim_idx=sim_idx, cmap=cmap)


def sp_comm_dyn_view(simulation, sim_idx=0, process='consumption', layout_name='klay',
                     cmap='RdBu_r', random_state=None):
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
    cmap : str or Colormap instance
        The colormap used to map the reaction rate values to RGBA colors. For more information
        visit: https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html
    random_state: int
        Random state seed use by the community detection algorithm

    """
    return Viz(data=simulation, type_of_viz='dynamic_sp_comm_view', layout_name=layout_name,
               random_state=random_state, process=process, sim_idx=sim_idx, cmap=cmap)


def sim_model_dyn_view(model, tspan, param_values=None, type_of_viz='dynamic_view', process='consumption',
                       cmap='RdBu_r', layout_name='cose-bilkent'):
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
    cmap : str or Colormap instance
        The colormap used to map the reaction rate values to RGBA colors. For more information
        visit: https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html
    layout_name : str
        Layout name to use

    """
    from pysb.simulator import ScipyOdeSimulator
    from pyvipr.util import dispatch_pysb_files

    model = dispatch_pysb_files(model)
    sim = ScipyOdeSimulator(model, tspan=tspan).run(param_values=param_values)
    return Viz(data=sim, type_of_viz=type_of_viz, process=process, layout_name=layout_name, cmap=cmap)
