# <img alt="pyViPR" src="https://github.com/LoLab-VU/pyvipr/blob/master/pyvipr_logo.png" height="100">


[![Documentation Status](https://readthedocs.org/projects/pyvipr/badge/?version=latest)](https://pyvipr.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/LoLab-VU/pyvipr.svg?branch=master)](https://travis-ci.org/LoLab-VU/pyvipr)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/LoLab-VU/pyvipr/master?filepath=docs%2Ftutorial.ipynb)
# PyViPR
PyViPR is a Jupyter widget for dynamic and static visualizations of [PySB](http://pysb.org/), [Tellurium](http://tellurium.analogmachine.org/),
[BNGL](https://www.csb.pitt.edu/Faculty/Faeder/?page_id=409), and [SBML](http://sbml.org/Main_Page) 
 models using cytoscapejs. Additionally, it can be used to visualize models defined in [Ecell4](https://github.com/ecell/ecell4).

## Installation

### From conda

#### To use with Jupyter Notebooks:

```bash
> conda install pyvipr -c ortegas
```

#### To use with JupyterLab:

```bash
> conda install pyvipr -c ortegas
> jupyter labextension install @jupyter-widgets/jupyterlab-manager
> jupyter labextension install pyvipr
```

### From PyPI

#### To use with Jupyter Notebooks:

```bash
> pip install pyvipr
```

#### To use with JupyterLab:

```bash
> pip install pyvipr
> jupyter labextension install @jupyter-widgets/jupyterlab-manager
> jupyter labextension install pyvipr
```

### From git (requires npm)
```bash
$ git clone https://github.com/LoLab-VU/pyvipr.git
$ cd pyvipr
$ pip install .
```

## How to use the widget
After installing the widget, it can be used by importing it in the Jupyter notebook. The widget is simple to use with PySB 
models, [SimulationResult](https://pysb.readthedocs.io/en/stable/modules/simulator.html#pysb.simulator.SimulationResult) 
objects, [Tellurium](http://tellurium.analogmachine.org/) models and BNGL & SBML files. 

PyViPR has two main interfaces: a PySB interface and a Tellurium interface.

### PySB interface

PySB is needed to visualize PySB models and it is needed if you want to use the pyvipr.pysb_viz module:

Installing PySB from pip:
```bash
> pip install pysb
```

When using pip the [installation of PySB](https://pysb.readthedocs.io/en/stable/installation.html#option-1-install-pysb-natively-on-your-computer)
requires to manually install BioNetGen into the default path for your platform 
(/usr/local/share/BioNetGen on Mac and Linux, c:\Program Files\BioNetGen on Windows), 
or set the BNGPATH environment variable to the BioNetGen path on your machine.

Installing PySB from conda:
```bash
> conda install pysb -c alubbock
```

PyViPR has the following functions to visualize PySB models and simulations:

| Function                                 | Description                                           |
|------------------------------------------|-------------------------------------------------------|
| `sp_view(model)`                    | Shows network of interacting species                  |
| `sp_comp_view(model)`       | Shows network of species in their respective compartments |
| `sp_comm_view(model)`                | Shows network of species grouped in [communities](https://en.wikipedia.org/wiki/Community_structure) |
| `sp_rxns_bidirectional_view(model)`      | Shows bipartite network with species and bidirectional reactions nodes |
| `sp_rxns_view(model)`                    | Shows bipartite network with species and unidirectional reactions nodes |
| `sp_rules_view(model)`                   | Shows bipartite network with species and rules nodes  |
| `sp_rules_fxns_view(model)`         | Shows bipartite network with species and rules nodes.<br> Rules nodes are grouped in the functions they come from |
| `sp_rules_mod_view(model)`           | Shows bipartite network with species and rules nodes.<br> Rules nodes are grouped in the file modules they come from |
| `projected_species_reactions_view(model)`| Shows network of species projected from the <br> bipartite(species, reactions) graph |
| `projected_reactions_view(model)`        | Shows network of reactions projected from the <br> bipartite(species, reactions) graph |
| `projected_rules_view(model)`            | Shows network of rules projected from the <br> bipartite(species, rules) graph |
| `projected_species_rules_view(model)`    | Shows network of species projected from the <br> bipartite(species, rules) graph |
| `sp_dyn_view(SimulationResult)`| Shows a species network. Edges size and color are updated <br> according to reaction rate values. Nodes filling <br> are updated according to concentration|
| `sp_comp_dyn_view(SimulationResult)` | Same as sp_dyn_view but species nodes are grouped by <br> the compartments on which they are located |
| `sp_comm_dyn_view(SimulationResult)` | Same as sp_dyn_view but species nodes are grouped by communities |
| `sim_model_dyn_view(model, tspan, param_values)` | Simulates a model a shows a dynamic visualization of the results |
| `nx_graph_view(graph)` | Shows a networkx graph |
| `nx_graph_dyn_view(graph, tspan, **kwargs)`| Shows a dynamic visualization of the graph |

### Tellurium interface

Tellurium is needed to visualize Tellurium models and it is needed if you want to use the pyvipr.tellurium_viz module:

Installing Tellurium from pip:
```bash
> pip install tellurium
```

Currently PyViPR only supports two static visualizations:

* sp_view(model)
* sp_comm(model)

and one dynamic visualization:

* sp_dyn_view(simulation)

In the future, we plan to add more visualizations of Tellurium models

## Examples

#### Static Example:
```python
import pyvipr.pysb_viz as viz
from pyvipr.examples_models.lopez_embedded import model

viz.sp_comm_view(model, random_state=1, layout_name='klay')
```
![species_view](earm_comms.png)

#### Dynamic Example:
```python
import pyvipr.pysb_viz as viz
from pyvipr.examples_models.mm_two_paths_model import model
from pysb.simulator import ScipyOdeSimulator
import numpy as np

tspan = np.linspace(0, 1000, 100)
sim = ScipyOdeSimulator(model, tspan).run()
viz.sp_dyn_view(sim)
```

![enzymatic_reaction](pysbViz.gif)

PyViPR now has basic support to visualize PySB models using the SBGN standard:
```python
from pyvipr.examples_models.mm_two_paths_model import model
import pyvipr.pysb_viz as viz

viz.sbgn_view(model)
```

![sbgn_view](sbgn_double_enzymatic.png)

## License

[MIT](https://opensource.org/licenses/MIT)
