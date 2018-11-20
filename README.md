# viz-pysb-widget
Dynamic and static visualizations of [PySB](http://pysb.org/) models using cytoscapejs, It is largely based on the 
[cytoscape-jupyter-widget](https://github.com/idekerlab/cytoscape-jupyter-widget)

## Installation
```bash
$ git clone https://github.com/LoLab-VU/viz-pysb-widget.git
$ cd viz-pysb-widget
$ pip install -e .
$ jupyter nbextension install --py --symlink --sys-prefix pysbjupyter
$ jupyter nbextension enable --py --sys-prefix pysbjupyter
```

## How to use the widget
After installing the widget, it can be used by importing it in the notebook. The widget is simple to use with PySB 
models and [SimulationResult](https://pysb.readthedocs.io/en/stable/modules/simulator.html#pysb.simulator.SimulationResult) 
objects. There are two types of visualizations that can be performed. 

1) Static visualizations. This type of visualization only requires a PySB model. There are different networks
that can be generated by using the species, rules and reactions defined in a model. These different networks
can be obtained by passing one of the following strings to the *type_of_viz* parameter of the widget:
    * Species network: 'species_view'
    * Species and reactions bipartite network: 'sp_rxns_bidirectional_view'
    * Species and rules bipartite network: 'sp_rules_view'
    * Reactions network: 'projected_view_reactions'
    * Rules network: 'projected_view_rules'
  

```python
from pysbjupyter import pysbViz
from pysbjupyter.pysb_models.mm_two_paths_model import model

pysbViz(data=model, type_of_viz='species_view')
```

![species_view](double_enzymatic_species.png)

2) Dynamic visualizations. This type of visualization requires the results of a simulation 
(a PySB SimulationResult object). This visualization encodes the reaction rate values in the size and color 
of the edges between the species nodes, and molecular species concentrations relative to the maximum
concentration attained across all time points are  represented with pie charts. Full pie chart represent 
the maximum concentration attained across all time points. Clicking on edges and nodes shows the
 absolute value of the reaction rates and the concentrations

```python
from pysbjupyter import pysbViz
from pysbjupyter.pysb_models.mm_two_paths_model import model
from pysb.simulator import ScipyOdeSimulator
import numpy as np

tspan = np.linspace(0, 1000, 100)
sim = ScipyOdeSimulator(model, tspan).run()
pysbViz(data=model)
```

![enzymatic_reaction](pysbViz.gif)

## License

[MIT](https://opensource.org/licenses/MIT)
