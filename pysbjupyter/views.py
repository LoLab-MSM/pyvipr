from .pysbviz import pysbViz

__all__ = [
    'sp_view',
    'sp_comp_view',
    'sp_comm_view',
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
    'magine_network'
]


def sp_view(model, layout_name='preset'):
    return pysbViz(data=model, type_of_viz='species_view', layout_name=layout_name)


def sp_comp_view(model, layout_name='cose-bilkent'):
    return pysbViz(data=model, type_of_viz='species_compartments_view', layout_name=layout_name)


def sp_comm_view(model, layout_name='cose-bilkent'):
    return pysbViz(data=model, type_of_viz='communities_view', layout_name=layout_name)


def sp_rxns_bidirectional_view(model, layout_name='preset'):
    return pysbViz(data=model, type_of_viz='sp_rxns_bidirectional_view', layout_name=layout_name)


def sp_rxns_view(model, layout_name='preset'):
    return pysbViz(data=model, type_of_viz='sp_rxns_view', layout_name=layout_name)


def sp_rules_view(model, layout_name='preset'):
    return pysbViz(data=model, type_of_viz='sp_rules_view', layout_name=layout_name)


def sp_rules_fxns_view(model, layout_name='cose-bilkent'):
    return pysbViz(data=model, type_of_viz='sp_rules_functions_view', layout_name=layout_name)


def sp_rules_mod_view(model, layout_name='cose-bilkent'):
    return pysbViz(data=model, type_of_viz='sp_rules_modules_view', layout_name=layout_name)


def projected_species_reactions_view(model, layout_name='preset'):
    return pysbViz(data=model, type_of_viz='projected_species_reactions_view', layout_name=layout_name)


def projected_reactions_view(model, layout_name='preset'):
    return pysbViz(data=model, type_of_viz='projected_reactions_view', layout_name=layout_name)


def projected_rules_view(model, layout_name='preset'):
    return pysbViz(data=model, type_of_viz='projected_rules_view', layout_name=layout_name)


def projected_species_rules_view(model, layout_name='preset'):
    return pysbViz(data=model, type_of_viz='projected_species_rules_view', layout_name=layout_name)


def sp_dyn_view(simulation, layout_name='preset'):
    return pysbViz(data=simulation, type_of_viz='dynamic_view', layout_name=layout_name)


def sp_comp_dyn_view(simulation, layout_name='cose-bilkent'):
    return pysbViz(data=simulation, type_of_viz='dynamic_compartments_view', layout_name=layout_name)


def sp_comm_dyn_view(simulation, layout_name='cose-bilkent'):
    return pysbViz(data=simulation, type_of_viz='dynamic_communities_view', layout_name=layout_name)


def magine_network(json_graph, layout_name='cose-bilkent'):
    return pysbViz(data=json_graph, type_of_viz='magine_graph', layout_name=layout_name)
