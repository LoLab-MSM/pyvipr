import json
from collections import OrderedDict

import networkx as nx

from .util_networkx import from_networkx


def graph_to_json(sp_graph, layout=None, path=''):
    """

    Parameters
    ----------
    sp_graph : nx.Digraph graph
        A graph to be converted into cytoscapejs json format
    layout: str or dict
        Name of the layout algorithm to use for the visualization
    path: str
        Path to save the file

    Returns
    -------
    A Dictionary Object that can be converted into Cytoscape.js JSON
    """
    data = from_networkx(sp_graph, layout=layout, scale=1)
    if path:
        with open(path + 'data.json', 'w') as outfile:
            json.dump(data, outfile)
    return data


def dot_layout(sp_graph):
    """

    Parameters
    ----------
    sp_graph : nx.Digraph graph
        Graph to layout

    Returns
    -------
    An OrderedDict containing the node position according to the dot layout
    """

    pos = nx.nx_pydot.graphviz_layout(sp_graph, prog='dot')
    ordered_pos = OrderedDict((node, pos[node]) for node in sp_graph.nodes())
    return ordered_pos
