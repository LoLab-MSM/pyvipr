import ipywidgets as widgets
from pyvipr.model_simresult_to_json import data_to_json
from ._version import __frontend_version__

from traitlets import Any, Unicode, Int, observe


@widgets.register
class pysbViz(widgets.DOMWidget):
    """Cytoscape.js widget for simple network visualization."""
    _view_name = Unicode('CytoscapeView').tag(sync=True)
    _model_name = Unicode('CytoscapeModel').tag(sync=True)
    _view_module = Unicode('pyvipr').tag(sync=True)
    _model_module = Unicode('pyvipr').tag(sync=True)
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
    process = Unicode('consumption').tag(sync=True, o=True)   # This is necessary only for dynamic visualization
    sim_idx = Int(0).tag(sync=True, o=True)

    @observe('process')
    def _observe_process(self, change):
        self.send_state('data')

    @observe('sim_idx')
    def _observe_sim_idx(self, change):
        self.send_state('data')
