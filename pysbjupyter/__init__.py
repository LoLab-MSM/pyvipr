from ._version import version_info, __version__

from .pysbviz import *

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'viz-pysb-widget',
        'require': 'viz-pysb-widget/extension'
    }]
