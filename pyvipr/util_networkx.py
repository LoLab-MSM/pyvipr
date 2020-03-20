"""
Data conversion utility for NetworkX
=====================================
Convert cytoscape.js style graphs from/to NetworkX object.
https://networkx.github.io/
"""

from numbers import Number
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

CY_GML_NODE_STYLE = {'ellipse': 'ellipse', 'roundrectangle': 'round-rectangle'}
CY_GML_ARROWS = {'standard': 'triangle', 'none': 'none'}
CY_GML_LINE_STYLE = {'line': 'solid', 'dotted': 'dotted', 'dashed': 'dashed'}


def __map_table_data(columns, graph_obj):
    data = {}
    for col in columns:
        if col == 0:
            break

        data[col] = graph_obj[col]

    return data


def map_node_data_gml(columns, graph_obj):
    data = {}

    if graph_obj['gid'] != '':
        data['parent'] = graph_obj['gid']

    shape = graph_obj['graphics']['type']

    background_color = graph_obj['graphics']['fill']
    data['label'] = graph_obj['label']
    data['border_color'] = graph_obj['graphics']['outline']
    data['shape'] = CY_GML_NODE_STYLE[shape]
    data['background_color'] = background_color
    return data


def map_edge_data_gml(edge_data):
    line_style = edge_data['graphics']['style']
    source_arrow = edge_data['graphics']['sourceArrow']
    target_arrow = edge_data['graphics']['targetArrow']
    line_color = edge_data['graphics']['fill']
    data = {'line_style': CY_GML_LINE_STYLE[line_style], 'line_color': line_color,
            'source_arrow_shape': CY_GML_ARROWS[source_arrow], 'target_arrow_shape': CY_GML_ARROWS[target_arrow]}
    return data


def __create_node(node, node_id, map_data):
    new_node = {}
    node_columns = node.keys()
    data = map_data(node_columns, node)
    # Override special keys
    data[ID] = str(node_id)
    data[NAME] = str(node_id)

    if 'position' in node.keys():
        position = node['position']
        new_node['position'] = position

    new_node[DATA] = data
    return new_node


def __build_multi_edge(edge_tuple, map_data=None):
    source = edge_tuple[0]
    target = edge_tuple[1]
    key = edge_tuple[2]
    if map_data is not None:
        data = map_data(edge_tuple[3])
    else:
        data = edge_tuple[3]

    data['source'] = str(source)
    data['target'] = str(target)
    data['interaction'] = str(key)
    return {DATA: data}


def __build_edge(edge_tuple, map_data=None):
    source = edge_tuple[0]
    target = edge_tuple[1]
    if map_data is not None:
        data = map_data(edge_tuple[2])
    else:
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


def from_networkx(g, layout=None, scale=DEF_SCALE, map_node_data=None, map_edge_data=None):
    # Dictionary Object to be converted to Cytoscape.js JSON
    if map_node_data is None:
        map_node_data = __map_table_data
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
        new_node = __create_node(g.nodes[node_id], node_id, map_node_data)
        if layout is not None:
            new_node['position'] = pos[i]

        cygraph['elements']['nodes'].append(new_node)

    for edge in edges:
        cygraph['elements']['edges'].append(edge_builder(edge, map_edge_data))

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
    nx.set_node_attributes(network, node_tip_default, 'qtip')
    nx.set_node_attributes(network, 'ellipse', 'shape')
    nx.set_node_attributes(network, '#2b913a', 'background_color')
    nx.set_edge_attributes(network, edge_colors_default, 'edge_color')
    nx.set_edge_attributes(network, edge_sizes_default, 'edge_size')
    nx.set_edge_attributes(network, edge_tips_default, 'qtip')

    network.graph['name'] = ''
    network.graph['view'] = 'dynamic'
    network.graph['tspan'] = tspan


# The function below is modified from NetworkX

"""
Copyright (C) 2004-2019, NetworkX Developers
Aric Hagberg <hagberg@lanl.gov>
Dan Schult <dschult@colgate.edu>
Pieter Swart <swart@lanl.gov>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

  * Redistributions in binary form must reproduce the above
    copyright notice, this list of conditions and the following
    disclaimer in the documentation and/or other materials provided
    with the distribution.

  * Neither the name of the NetworkX Developers nor the names of its
    contributors may be used to endorse or promote products derived
    from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


def draw_networkx_edges(G, pos,
                        edgelist=None,
                        width=1.0,
                        edge_color='k',
                        style='solid',
                        alpha=None,
                        arrowstyle='-|>',
                        arrowsize=10,
                        edge_cmap=None,
                        edge_vmin=None,
                        edge_vmax=None,
                        ax=None,
                        arrows=True,
                        label=None,
                        node_size=300,
                        nodelist=None,
                        node_shape="o",
                        connectionstyle=None,
                        min_source_margin=0,
                        min_target_margin=0,
                        **kwds):
    """Draw the edges of the graph G.

    This draws only the edges of the graph G.

    Parameters
    ----------
    G : graph
       A networkx graph

    pos : dictionary
       A dictionary with nodes as keys and positions as values.
       Positions should be sequences of length 2.

    edgelist : collection of edge tuples
       Draw only specified edges(default=G.edges())

    width : float, or array of floats
       Line width of edges (default=1.0)

    edge_color : color or array of colors (default='k')
       Edge color. Can be a single color or a sequence of colors with the same
       length as edgelist. Color can be string, or rgb (or rgba) tuple of
       floats from 0-1. If numeric values are specified they will be
       mapped to colors using the edge_cmap and edge_vmin,edge_vmax parameters.

    style : string
       Edge line style (default='solid') (solid|dashed|dotted,dashdot)

    alpha : float
       The edge transparency (default=None)

    edge_ cmap : Matplotlib colormap
       Colormap for mapping intensities of edges (default=None)

    edge_vmin,edge_vmax : floats
       Minimum and maximum for edge colormap scaling (default=None)

    ax : Matplotlib Axes object, optional
       Draw the graph in the specified Matplotlib axes.

    arrows : bool, optional (default=True)
       For directed graphs, if True draw arrowheads.
       Note: Arrows will be the same color as edges.

    arrowstyle : array-like, optional (default='-|>')
       For directed graphs, choose the style of the arrow heads for each edge.
       See :py:class: `matplotlib.patches.ArrowStyle` for more
       options.

    arrowsize : int, optional (default=10)
       For directed graphs, choose the size of the arrow head head's length and
       width. See :py:class: `matplotlib.patches.FancyArrowPatch` for attribute
       `mutation_scale` for more info.

    connectionstyle : str, optional (default=None)
       Pass the connectionstyle parameter to create curved arc of rounding
       radius rad. For example, connectionstyle='arc3,rad=0.2'.
       See :py:class: `matplotlib.patches.ConnectionStyle` and
       :py:class: `matplotlib.patches.FancyArrowPatch` for more info.

    label : [None| string]
       Label for legend

    min_source_margin : int, optional (default=0)
       The minimum margin (gap) at the begining of the edge at the source.

    min_target_margin : int, optional (default=0)
       The minimum margin (gap) at the end of the edge at the target.

    Returns
    -------
    matplotlib.collection.LineCollection
        `LineCollection` of the edges

    list of matplotlib.patches.FancyArrowPatch
        `FancyArrowPatch` instances of the directed edges

    Depending whether the drawing includes arrows or not.

    Notes
    -----
    For directed graphs, arrows are drawn at the head end.  Arrows can be
    turned off with keyword arrows=False. Be sure to include `node_size` as a
    keyword argument; arrows are drawn considering the size of nodes.

    Examples
    --------
    >>> G = nx.dodecahedral_graph()
    >>> edges = nx.draw_networkx_edges(G, pos=nx.spring_layout(G))

    >>> G = nx.DiGraph()
    >>> G.add_edges_from([(1, 2), (1, 3), (2, 3)])
    >>> arcs = nx.draw_networkx_edges(G, pos=nx.spring_layout(G))
    >>> alphas = [0.3, 0.4, 0.5]
    >>> for i, arc in enumerate(arcs):  # change alpha values of arcs
    ...     arc.set_alpha(alphas[i])

    Also see the NetworkX drawing examples at
    https://networkx.github.io/documentation/latest/auto_examples/index.html

    See Also
    --------
    draw()
    draw_networkx()
    draw_networkx_nodes()
    draw_networkx_labels()
    draw_networkx_edge_labels()
    """
    try:
        import matplotlib
        import matplotlib.pyplot as plt
        from matplotlib.colors import colorConverter, Colormap, Normalize
        from matplotlib.collections import LineCollection
        from matplotlib.patches import FancyArrowPatch
        import numpy as np
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    if ax is None:
        ax = plt.gca()

    if edgelist is None:
        edgelist = list(G.edges())

    if not edgelist or len(edgelist) == 0:  # no edges!
        if not G.is_directed() or not arrows:
            return LineCollection(None)
        else:
            return []

    if nodelist is None:
        nodelist = list(G.nodes())

    # FancyArrowPatch handles color=None different from LineCollection
    if edge_color is None:
        edge_color = 'k'

    # set edge positions
    edge_pos = np.asarray([(pos[e[0]], pos[e[1]]) for e in edgelist])

    # Check if edge_color is an array of floats and map to edge_cmap.
    # This is the only case handled differently from matplotlib
    if np.iterable(edge_color) and (len(edge_color) == len(edge_pos)) \
            and np.alltrue([isinstance(c, Number) for c in edge_color]):
        if edge_cmap is not None:
            assert(isinstance(edge_cmap, Colormap))
        else:
            edge_cmap = plt.get_cmap()
        if edge_vmin is None:
            edge_vmin = min(edge_color)
        if edge_vmax is None:
            edge_vmax = max(edge_color)
        color_normal = Normalize(vmin=edge_vmin, vmax=edge_vmax)
        edge_color = [edge_cmap(color_normal(e)) for e in edge_color]

    if (not G.is_directed() or not arrows):
        edge_collection = LineCollection(edge_pos,
                                         colors=edge_color,
                                         linewidths=width,
                                         antialiaseds=(1,),
                                         linestyle=style,
                                         transOffset=ax.transData,
                                         alpha=alpha
                                         )

        edge_collection.set_cmap(edge_cmap)
        edge_collection.set_clim(edge_vmin, edge_vmax)

        edge_collection.set_zorder(1)  # edges go behind nodes
        edge_collection.set_label(label)
        ax.add_collection(edge_collection)

        return edge_collection

    arrow_collection = None

    if G.is_directed() and arrows:
        # Note: Waiting for someone to implement arrow to intersection with
        # marker.  Meanwhile, this works well for polygons with more than 4
        # sides and circle.

        def to_marker_edge(marker_size, marker):
            if marker in "s^>v<d":  # `large` markers need extra space
                return np.sqrt(2 * marker_size) / 2
            else:
                return np.sqrt(marker_size) / 2

        # Draw arrows with `matplotlib.patches.FancyarrowPatch`
        arrow_collection = []
        mutation_scale = arrowsize  # scale factor of arrow head

        # FancyArrowPatch doesn't handle color strings
        arrow_colors = colorConverter.to_rgba_array(edge_color, alpha)
        for i, (src, dst) in enumerate(edge_pos):
            x1, y1 = src
            x2, y2 = dst
            shrink_source = 0  # space from source to tail
            shrink_target = 0  # space from  head to target
            if np.iterable(node_size):  # many node sizes
                source, target = edgelist[i][:2]
                source_node_size = node_size[nodelist.index(source)]
                target_node_size = node_size[nodelist.index(target)]
                shrink_source = to_marker_edge(source_node_size, node_shape)
                shrink_target = to_marker_edge(target_node_size, node_shape)
            else:
                shrink_source = shrink_target = to_marker_edge(node_size, node_shape)

            if shrink_source < min_source_margin:
                shrink_source = min_source_margin

            if shrink_target < min_target_margin:
                shrink_target = min_target_margin

            if len(arrow_colors) == len(edge_pos):
                arrow_color = arrow_colors[i]
            elif len(arrow_colors) == 1:
                arrow_color = arrow_colors[0]
            else:  # Cycle through colors
                arrow_color = arrow_colors[i % len(arrow_colors)]

            if np.iterable(width):
                if len(width) == len(edge_pos):
                    line_width = width[i]
                else:
                    line_width = width[i % len(width)]
            else:
                line_width = width

            arrow = FancyArrowPatch((x1, y1), (x2, y2),
                                    arrowstyle=arrowstyle[i],
                                    shrinkA=shrink_source,
                                    shrinkB=shrink_target,
                                    mutation_scale=mutation_scale,
                                    color=arrow_color,
                                    linewidth=line_width,
                                    connectionstyle=connectionstyle,
                                    linestyle=style,
                                    zorder=1)  # arrows go behind nodes

            # There seems to be a bug in matplotlib to make collections of
            # FancyArrowPatch instances. Until fixed, the patches are added
            # individually to the axes instance.
            arrow_collection.append(arrow)
            ax.add_patch(arrow)

    # update view
    minx = np.amin(np.ravel(edge_pos[:, :, 0]))
    maxx = np.amax(np.ravel(edge_pos[:, :, 0]))
    miny = np.amin(np.ravel(edge_pos[:, :, 1]))
    maxy = np.amax(np.ravel(edge_pos[:, :, 1]))

    w = maxx - minx
    h = maxy - miny
    padx,  pady = 0.05 * w, 0.05 * h
    corners = (minx - padx, miny - pady), (maxx + padx, maxy + pady)
    ax.update_datalim(corners)
    ax.autoscale_view()

    ax.tick_params(
        axis='both',
        which='both',
        bottom=False,
        left=False,
        labelbottom=False,
        labelleft=False)

    return arrow_collection
