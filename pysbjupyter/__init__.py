from ._version import version_info, __version__
from .magine_nb import render_network
from .pysbviz import pysbViz, networkxViz
from .views import *


def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'viz-pysb-widget',
        'require': 'viz-pysb-widget/extension'
    }]


__all__ = ['pysbViz', 'networkxViz', 'render_network'] + views.__all__
