from .pysbviz import pysbViz

__all__ = [
    'species_view',
    'species_compartments_view',
    'communities_view',
    'sp_rxns_bidirectional_view',
    'sp_rxns_view',
    'sp_rules_view',
    'sp_rules_functions_view',
    'sp_rules_modules_view',
    'projected_species_reactions_view',
    'projected_reactions_view',
    'projected_rules_view',
    'projected_species_rules_view',
    'species_dynamics_view',
    'sp_compartments_dynamics_view',
    'sp_communities_dynamics_view'
]


def species_view(model, layout_name='preset'):
    return pysbViz(data=model, type_of_viz='species_view', layout_name=layout_name)


def species_compartments_view(model, layout_name='cose-bilkent'):
    return pysbViz(data=model, type_of_viz='species_compartments_view', layout_name=layout_name)


def communities_view(model, layout_name='cose-bilkent'):
    return pysbViz(data=model, type_of_viz='communities_view', layout_name=layout_name)


def sp_rxns_bidirectional_view(model, layout_name='preset'):
    return pysbViz(data=model, type_of_viz='sp_rxns_bidirectional_view', layout_name=layout_name)


def sp_rxns_view(model, layout_name='preset'):
    return pysbViz(data=model, type_of_viz='sp_rxns_view', layout_name=layout_name)


def sp_rules_view(model, layout_name='preset'):
    return pysbViz(data=model, type_of_viz='sp_rules_view', layout_name=layout_name)


def sp_rules_functions_view(model, layout_name='cose-bilkent'):
    return pysbViz(data=model, type_of_viz='sp_rules_functions_view', layout_name=layout_name)


def sp_rules_modules_view(model, layout_name='cose-bilkent'):
    return pysbViz(data=model, type_of_viz='sp_rules_modules_view', layout_name=layout_name)


def projected_species_reactions_view(model, layout_name='preset'):
    return pysbViz(data=model, type_of_viz='projected_species_reactions_view', layout_name=layout_name)


def projected_reactions_view(model, layout_name='preset'):
    return pysbViz(data=model, type_of_viz='projected_reactions_view', layout_name=layout_name)


def projected_rules_view(model, layout_name='preset'):
    return pysbViz(data=model, type_of_viz='projected_rules_view', layout_name=layout_name)


def projected_species_rules_view(model, layout_name='preset'):
    return pysbViz(data=model, type_of_viz='projected_species_rules_view', layout_name=layout_name)


def species_dynamics_view(simulation, layout_name='preset'):
    return pysbViz(data=simulation, type_of_viz='dynamic_view', layout_name=layout_name)


def sp_compartments_dynamics_view(simulation, layout_name='cose-bilkent'):
    return pysbViz(data=simulation, type_of_viz='dynamic_compartments_view', layout_name=layout_name)


def sp_communities_dynamics_view(simulation, layout_name='cose-bilkent'):
    return pysbViz(data=simulation, type_of_viz='dynamic_communities_view', layout_name=layout_name)
