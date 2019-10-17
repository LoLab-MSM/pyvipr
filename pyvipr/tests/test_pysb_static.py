import pytest
from pyvipr.examples_models.lopez_embedded import model
from pyvipr.pysb_viz.static_viz import PysbStaticViz


@pytest.fixture
def viz_model():
    viz = PysbStaticViz(model)
    return viz


def test_viz_exists(viz_model):
    assert viz_model


def test_graphs(viz_model):
    g_sp = viz_model.species_graph()
    g_rxn_bi = viz_model.sp_rxns_bidirectional_graph(two_edges=True)
    g_rxn = viz_model.sp_rxns_graph()
    g_rules = viz_model.sp_rules_graph()
    g_proj_sp = viz_model.projected_graph(g_rxn_bi, 'species_from_bireactions', viz_model.model.reactions_bidirectional)
    g_proj_birxns = viz_model.projected_graph(g_rxn_bi, 'bireactions')
    g_proj_rules = viz_model.projected_graph(g_rules, 'rules')

    n_species = len(viz_model.model.species)
    assert len(g_sp.nodes()) == n_species
    assert len(g_rxn_bi.nodes()) == n_species + len(viz_model.model.reactions_bidirectional)
    assert len(g_rxn.nodes()) == n_species + len(viz_model.model.reactions)
    assert len(g_rules.nodes()) == n_species + len(viz_model.model.rules)
    assert len(g_proj_sp.nodes()) == n_species
    assert len(g_proj_birxns.nodes()) == len(viz_model.model.reactions_bidirectional)
    assert len(g_proj_rules.nodes()) == len(viz_model.model.rules)


def test_wrong_projection(viz_model):
    with pytest.raises(ValueError):
        viz_model._projections_view('wrong_projection')


def test_no_compartments(viz_model):
    with pytest.raises(ValueError):
        viz_model.compartments_data_graph()
