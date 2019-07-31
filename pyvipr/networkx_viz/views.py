from pyvipr.viz import Viz

__all__ = [
    'nx_graph_view',
    'nx_graph_dyn_view',
]


def nx_graph_view(graph, layout_name='cose'):
    """
    Render a networkx Graph or DiGraph
    Parameters
    ----------
    graph: nx.Graph or nx.DiGraph
        Graph to render
    layout_name: str
        Layout to use
    Returns
    -------
    """
    return Viz(data=graph, type_of_viz='network_static_view', layout_name=layout_name)


def nx_graph_dyn_view(graph, tspan, node_rel=None, node_tip=None, edge_colors=None, edge_sizes=None,
                      edge_tips=None, layout_name='cose'):
    """
    Render a dynamic visualization of a networkx graph
    Parameters
    ----------
    graph: nx.DiGraph or nx.Graph
    tspan: vector-like, optional
        Time values over which to simulate. The first and last values define
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
    layout_name: str
        Layout to use
    """
    from pyvipr.util_networkx import network_dynamic_data

    network_dynamic_data(graph, tspan, node_rel, node_tip, edge_colors, edge_sizes,
                         edge_tips)

    return Viz(data=graph, type_of_viz='dynamic_network_view', layout_name=layout_name)