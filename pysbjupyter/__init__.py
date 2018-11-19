from ._version import version_info, __version__

from .pysbviz import *

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'cytoscape-jupyter-widget',
        'require': 'cytoscape-jupyter-widget/extension'
    }]
