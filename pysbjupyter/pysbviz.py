import ipywidgets as widgets
from pysbjupyter.model_simresult_to_json import data_to_json
from ._version import __frontend_version__

from traitlets import Any, Unicode, Int


@widgets.register
class pysbViz(widgets.DOMWidget):
    """Cytoscape.js widget for simple network visualization."""
    _view_name = Unicode('CytoscapeView').tag(sync=True)
    _model_name = Unicode('CytoscapeModel').tag(sync=True)
    _view_module = Unicode('viz-pysb-widget').tag(sync=True)
    _model_module = Unicode('viz-pysb-widget').tag(sync=True)
    _view_module_version = Unicode(__frontend_version__).tag(sync=True)
    _model_module_version = Unicode(__frontend_version__).tag(sync=True)

     # Cytoscape options
    data = Any().tag(sync=True, to_json=data_to_json)
    type_of_viz = Unicode('species_view').tag(sync=True, o=True)
    visual_style = Any().tag(sync=True, o=True)
    format = Unicode('cyjs').tag(sync=True, o=True)
    layout_name = Unicode().tag(sync=True, o=True)
    background = Unicode('#FFFFFF').tag(sync=True, o=True)
    random_state = Int(default_value=None, allow_none=True)  # This is necessary only for viz with communities
    process = Unicode('consumption')    # This is necessary only for dynamic visualization

