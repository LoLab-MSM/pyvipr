"""
Data conversion utility for NetworkX
=====================================
Convert cytoscape.js style graphs from/to NetworkX object.
https://networkx.github.io/
"""

import networkx as nx

# Special Keys
ID = 'id'
NAME = 'name'
DATA = 'data'
ELEMENTS = 'elements'

NODES = 'nodes'
EDGES = 'edges'

SOURCE = 'source'
TARGET = 'target'

DEF_SCALE = 100


def __map_table_data(columns, graph_obj):
    data = {}
    for col in columns:
        if col == 0:
            break

        data[col] = graph_obj[col]

    return data


def __create_node(node, node_id):
    new_node = {}
    node_columns = node.keys()
    data = __map_table_data(node_columns, node)
    # Override special keys
    data[ID] = str(node_id)
    data[NAME] = str(node_id)

    if 'position' in node.keys():
        position = node['position']
        new_node['position'] = position

    new_node[DATA] = data
    return new_node


def __build_multi_edge(edge_tuple, g):
    source = edge_tuple[0]
    target = edge_tuple[1]
    key = edge_tuple[2]
    data = edge_tuple[3]

    data['source'] = str(source)
    data['target'] = str(target)
    data['interaction'] = str(key)
    return {DATA: data}


def __build_edge(edge_tuple, g):
    source = edge_tuple[0]
    target = edge_tuple[1]
    data = edge_tuple[2]

    data['source'] = str(source)
    data['target'] = str(target)
    return {DATA: data}


def __build_empty_graph():
    return {
        DATA: {},
        ELEMENTS: {
            NODES: [],
            EDGES: []
        }
    }


def from_networkx(g, layout=None, scale=DEF_SCALE):
    # Dictionary Object to be converted to Cytoscape.js JSON
    cygraph = __build_empty_graph()

    if layout is not None:
        pos = list(map(lambda position:
                  {'x': position[0]*scale, 'y': position[1]*scale},
                  layout.values()))

    nodes = g.nodes()
    if isinstance(g, nx.MultiDiGraph) or isinstance(g, nx.MultiGraph):
        edges = g.edges(data=True, keys=True)
        edge_builder = __build_multi_edge
    else:
        edges = g.edges(data=True)
        edge_builder = __build_edge

    # Map network table data
    cygraph[DATA] = __map_table_data(g.graph.keys(), g.graph)

    for i, node_id in enumerate(nodes):
        new_node = __create_node(g.node[node_id], node_id)
        if layout is not None:
            new_node['position'] = pos[i]

        cygraph['elements']['nodes'].append(new_node)

    for edge in edges:
        cygraph['elements']['edges'].append(edge_builder(edge, g))

    return cygraph


def to_networkx(cyjs, directed=True):
    """
    Convert Cytoscape.js-style JSON object into NetworkX object.
    By default, data will be handles as a directed graph.
    """

    if directed:
        g = nx.MultiDiGraph()
    else:
        g = nx.MultiGraph()

    network_data = cyjs[DATA]
    if network_data is not None:
        for key in network_data.keys():
            g.graph[key] = network_data[key]

    nodes = cyjs[ELEMENTS][NODES]
    edges = cyjs[ELEMENTS][EDGES]

    for node in nodes:
        data = node[DATA]
        g.add_node(data[ID], attr_dict=data)

    for edge in edges:
        data = edge[DATA]
        source = data[SOURCE]
        target = data[TARGET]

        g.add_edge(source, target, attr_dict=data)

    return g


def network_dynamic_data(network, tspan, node_rel=None, node_tip=None, edge_colors=None, edge_sizes=None,
                         edge_tips=None):
    """

    Parameters
    ----------
    network: nx.DiGraph or nx.Graph
    tspan
    node_rel: dict
        A dictionary where the keys are the node ids and the values are
        lists that contain (0-100) values that are represented in a
        pie chart within the node
    node_tip: dict
        A dictionary where the keys are the node ids and the values are
        lists that contain any value that can be accessed
        as a tooltip in the rendered network
    edge_colors: dict
        A dictionary where the keys are the edge ids and the values are
        lists that contain any hexadecimal color value that are
        represented in the edge colors
    edge_sizes: dict
        A dictionary where the keys are the edge ids and the values are
        lists that contain any numerical value that are
        represented in the edge size
    edge_tips: dict
        A dictionary where the keys are the edge ids and the values are
        lists that contain any value that can be accessed
        as a tooltip in the rendered network
-

    """
    node_rel_default = [0] * len(tspan)
    node_tip_default = [0] * len(tspan)
    edge_colors_default = ['#787878'] * len(tspan)
    edge_sizes_default = [5] * len(tspan)
    edge_tips_default = [0] * len(tspan)

    if node_rel is not None:
        node_rel_default = node_rel
    if node_tip is not None:
        node_tip_default = node_tip
    if edge_colors is not None:
        edge_colors_default = edge_colors
    if edge_sizes is not None:
        edge_sizes_default = edge_sizes
    if edge_tips is not None:
        edge_tips_default = edge_tips

    node_edge_properties = [node_rel_default, node_tip_default, edge_colors_default,
                            edge_sizes_default, edge_tips_default]

    if [idx for idx in node_edge_properties if len(idx) != len(tspan)]:
        raise ValueError('All edge and node properties must be '
                         'equal length')

    nx.set_node_attributes(network, node_rel_default, 'rel_value')
    nx.set_node_attributes(network, node_tip_default, 'abs_value')
    nx.set_node_attributes(network, 'ellipse', 'shape')
    nx.set_node_attributes(network, '#2b913a', 'background_color')
    nx.set_edge_attributes(network, edge_colors_default, 'edge_color')
    nx.set_edge_attributes(network, edge_sizes_default, 'edge_size')
    nx.set_edge_attributes(network, edge_tips_default, 'edge_qtip')

    network.graph['name'] = ''
    network.graph['view'] = 'dynamic'
    network.graph['tspan'] = tspan

