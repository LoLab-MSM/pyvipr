import pytest
from pyvipr.examples_models.lopez_embedded import model
from pyvipr.pysb_viz.dynamic_viz import PysbDynamicViz
import numpy as np
from pysb.simulator import ScipyOdeSimulator


@pytest.fixture
def viz_model():
    tspan = np.linspace(0, 20000, 100)
    sim = ScipyOdeSimulator(model, tspan).run()
    viz = PysbDynamicViz(sim)
    return viz


def test_viz_exists(dyn_viz):
    assert dyn_viz

