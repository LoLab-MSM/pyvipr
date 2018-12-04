import ipywidgets as widgets
from pysbjupyter.model_simresult_to_json import data_to_json

from traitlets import (
    Any,
    Unicode

)

@widgets.register
class pysbViz(widgets.DOMWidget):
    """Cytoscape.js widget for simple network visualization."""
    _view_name = Unicode('CytoscapeView').tag(sync=True)
    _model_name = Unicode('CytoscapeModel').tag(sync=True)
    _view_module = Unicode('viz-pysb-widget').tag(sync=True)
    _model_module = Unicode('viz-pysb-widget').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)

     # Cytoscape options
    data = Any().tag(sync=True, to_json=data_to_json)
    type_of_viz = Unicode('species_view').tag(sync=True, o=True)
    visual_style = Any().tag(sync=True, o=True)
    format = Unicode('cyjs').tag(sync=True, o=True)
    layout_name = Unicode().tag(sync=True, o=True)
    background = Unicode('#FFFFFF').tag(sync=True, o=True)