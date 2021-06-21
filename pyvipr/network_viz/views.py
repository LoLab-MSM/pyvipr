from pyvipr.viz import Viz
from pyvipr.network_viz.network_viz import NetworkViz
import networkx as nx

__all__ = [
    'nx_graph_view',
    'nx_graph_dyn_view',
    'nx_function_view',
    'graphml_view',
    'sif_view',
    'sbgn_xml_view',
    'json_view',
    'dynamic_json_view',
    'gexf_view',
    'gml_view',
    'yaml_view'
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


def nx_function_view(graph, nx_function, layout_name='cose', **kwargs):
    nv = NetworkViz(graph)
    data = nv.nx_function_view(nx_function, **kwargs)
    return Viz(data=data, type_of_viz='', layout_name=layout_name)


def nx_graph_dyn_view(graph, tspan, node_rel=None, node_tip=None, edge_colors=None, edge_sizes=None,
                      edge_tips=None, layout_name='cose'):
    """
    Render a dynamic visualization of a networkx graph

    Parameters
    ----------
    graph: nx.DiGraph or nx.Graph
        Graph to visualize
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
    Returns
    -------
    """
    from pyvipr.util_networkx import network_dynamic_data

    network_dynamic_data(graph, tspan, node_rel, node_tip, edge_colors, edge_sizes,
                         edge_tips)

    return Viz(data=graph, type_of_viz='dynamic_network_view', layout_name=layout_name)


def graphml_view(file, layout_name='fcose'):
    """
    Read graph stored in GRAPHML format using NetworkX and render a visualization of it

    Parameters
    ----------
    file : str
        Path to file in graphml format
    layout_name : str
        Name of layout to use

    Returns
    -------

    """
    return Viz(data=file, type_of_viz='graphml', layout_name=layout_name)


def sif_view(file, layout_name='fcose'):
    """
    Read graph stored in SIF format using NetworkX and render a visualization of it

    Parameters
    ----------
    file : str
        Path to file in sif format
    layout_name : str
        Name of layout to use

    Returns
    -------

    """
    return Viz(data=file, type_of_viz='sif', layout_name=layout_name)


def sbgn_xml_view(file, layout_name='fcose'):
    """
    Read graph stored in SBGN XML format using NetworkX and render a visualization of it

    Parameters
    ----------
    file : str
        Path to file in SBGN XML format
    layout_name : str
        Name of layout to use

    Returns
    -------

    """
    return Viz(data=file, type_of_viz='sbgn_xml', layout_name=layout_name)


def json_view(file, layout_name='fcose'):
    """
    Read graph stored in cytoscape json format using NetworkX and render a visualization of it

    Parameters
    ----------
    file : str
        Path to file in cytoscape json format
    layout_name : str
        Name of layout to use

    Returns
    -------

    """
    return Viz(data=file, type_of_viz='json', layout_name=layout_name)


def dynamic_json_view(file, layout_name='fcose'):
    """
    Read graph stored in cytoscape json format using NetworkX and render a visualization of it.
    This function is for graphs saved from dynamic visualizations.

    Parameters
    ----------
    file : str
        Path to file in cytoscape json format
    layout_name : str
        Name of layout to use

    Returns
    -------

    """
    return Viz(data=file, type_of_viz='dynamic_json', process='json_process_nx_', sim_idx=0, layout_name=layout_name)


def gexf_view(file, node_type=None, relabel=False, version='1.2draft', layout_name='fcose'):
    """
    Read graph stored in GEXF format using NetworkX and render a visualization of it

    Parameters
    ----------
    file : str
        Path to file in gexf format
    node_type : Python type (default: none)
        Convert node ids to this type if not None
    relabel : bool (default: False)
        If True relabel the nodes to use the GEXF node "label attribute"
        instead of the node "id" attribute as the NetworkX node label
    version : str (default: 1.2draft)
        Version of GEFX File Format (see https://gephi.org/gexf/format/schema.html).
        Supported values: "1.1draft", "1.2dra
    layout_name : str
        Name of layout to use

    Returns
    -------

    """
    # Edge ids must be different than the ids assigned to nodes. Otherwise the visualization won't work
    graph = nx.read_gexf(file, node_type=node_type, relabel=relabel, version=version)
    return Viz(data=graph, type_of_viz='network_static_view', layout_name=layout_name)


def gml_view(file, label='label', destringizer=None, layout_name='fcose'):
    """
    Read graph stored in GML format using NetworkX and render a visualization of it

    Parameters
    ----------
    file : str
        Path to file in cytoscape json format
    label : str, optional
        If not None, the pased nodes will be renamed according to node attributes indicated by label.
        Default value: 'label'
    destringizer : callable, optional
        A destringizer that recovers values stored as strings in GML. If it cannot convert a string
        to a value, a ValueError is raised. Default value: None
    layout_name : str
        Name of layout to use

    Returns
    -------

    """
    graph = nx.read_gml(file, label=label, destringizer=destringizer)
    return Viz(data=graph, type_of_viz='network_static_view', layout_name=layout_name)


def yaml_view(file, layout_name='fcose'):
    """
    Read graph stored in YAML format using NetworkX and render a visualization of it

    Parameters
    ----------
    file : str
        Path to file in YAML format
    layout_name : str
        Name of layout to use

    Returns
    -------

    """
    try:
        import yaml
    except ImportError as e:
        raise ImportError("yaml_view() requires PyYAML: http://pyyaml.org/") from e
    with open(file, 'r') as f:
        graph = yaml.load(f, Loader=yaml.Loader)
    return Viz(data=graph, type_of_viz='network_static_view', layout_name=layout_name)
