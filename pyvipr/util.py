import matplotlib.cm as cm
import matplotlib.colors as colors
import numpy as np
import networkx as nx
import networkx.algorithms.community as nx_community
from community import community_louvain


class MidpointNormalize(colors.Normalize):
    """
    A class which, when called, can normalize data into the [vmin,midpoint,vmax] interval
    """

    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))


def range_normalization(x, min_x, max_x, a=0.5, b=10):
    """
    Normalize vector to the [0.5, 10] range

    Parameters
    ----------
    x: np.ndarray
        Vector of values to be normalized
    min_x: float
        Minimum value in vector x
    max_x: float
        Maximum value in vector x
    a: float
        Value of minimum used for the normalization
    b: float
        Value of maximum used for the normalization

    Returns
    -------
    Normalized vector
    """
    return a + (x - min_x) * (b - a) / (max_x - min_x)


def f2hex_edges(fx, vmin=-0.99, vmax=0.99, cmap='RdBu_r'):
    """
    Converts reaction rates values to f2hex colors

    Parameters
    ----------
    fx: vector-like
        Vector of reaction rates(flux)
    vmin: float
        Value of the minimum for normalization
    vmax: float
        Value of the maximum for normalization
    cmap: str or Colormap instance
        The colormap used to map normalized data values to RGBA colors

    Returns
    -------
    list
        A vector of colors in hex format that encodes the reaction rate values
    """
    norm = MidpointNormalize(vmin=vmin, vmax=vmax, midpoint=0)
    f2rgb = cm.ScalarMappable(norm=norm, cmap=cm.get_cmap(cmap))
    rgb = [f2rgb.to_rgba(rate)[:3] for rate in fx]
    colors_hex = [0] * (len(rgb))
    for i, color in enumerate(rgb):
        colors_hex[i] = '#{0:02x}{1:02x}{2:02x}'.format(*tuple([int(255 * fc) for fc in color]))
    return colors_hex


def add_louvain_communities(graph, all_levels=False, random_state=None):
    # Louvain method only deals with undirected graphs
    graph_communities = nx.Graph(graph)
    if all_levels:
        # We add the first communities detected, The dendrogram at level 0 contains the nodes as keys
        # and the clusters they belong to as values.
        dendrogram = community_louvain.generate_dendrogram(graph_communities, random_state=random_state)
        partition = dendrogram[0]
        cnodes = set(partition.values())
        graph.add_nodes_from(cnodes, NodeType='subcommunity')
        nx.set_node_attributes(graph, partition, 'parent')

        # The dendrogram at level 1 contains the new community nodes and the clusters they belong to.
        # We change the cluster names to differentiate them from the cluster names of the first clustering
        # result. Then, repeat the same procedures for the next levels.
        cluster_child_parent = dendrogram[1]
        for key, value in cluster_child_parent.items():
            cluster_child_parent[key] = '{0}_{1}'.format(1, value)
        cnodes = set(cluster_child_parent.values())
        graph.add_nodes_from(cnodes, NodeType='subcommunity')
        nx.set_node_attributes(graph, cluster_child_parent, 'parent')
        for level in range(2, len(dendrogram)):
            cluster_child_parent = dendrogram[level]
            cluster_child_parent2 = {'{0}_{1}'.format(level - 1, key): '{0}_{1}'.format(level, value) for
                                     (key, value) in cluster_child_parent.items()}
            cnodes = set(cluster_child_parent2.values())
            if level < len(dendrogram) - 1:
                graph.add_nodes_from(cnodes, NodeType='subcommunity')
            else:
                graph.add_nodes_from(cnodes, NodeType='community')
            nx.set_node_attributes(graph, cluster_child_parent2, 'parent')
            # Update nodes clusters
    else:
        communities = community_louvain.best_partition(graph_communities, random_state=random_state)
        # compound nodes to add to hold communities
        cnodes = set(communities.values())
        graph.add_nodes_from(cnodes, NodeType='community')
        nx.set_node_attributes(graph, communities, 'parent')
    return graph


def _nx_community_data_to_graph(graph, communities_result):
    node_community = {idx: 'c_{0}'.format(comm) for comm, nodes in
                      enumerate(communities_result) for idx in nodes}
    cnodes = set(node_community.values())

    graph.add_nodes_from(cnodes, NodeType='community')
    nx.set_node_attributes(graph, node_community, 'parent')
    return


def add_greedy_modularity_communities(graph):
    graph_communities = graph.copy().to_undirected()
    communities_result = nx_community.greedy_modularity_communities(graph_communities)
    _nx_community_data_to_graph(graph, communities_result)
    return graph


def add_asyn_lpa_communities(graph, weight=None, seed=None):
    communities_result = nx_community.asyn_lpa_communities(graph, weight, seed)
    _nx_community_data_to_graph(graph, communities_result)
    return graph


def add_label_propagation_communities(graph):
    graph_communities = graph.copy().to_undirected()  # label propagation algorithm only deals with undirected graphs
    communities_result = nx_community.label_propagation_communities(graph_communities)
    _nx_community_data_to_graph(graph, communities_result)
    return graph


def add_asyn_fluidc(graph, k, max_iter=100, seed=None):
    graph_communities = graph.copy().to_undirected()  # asyn_fluidc algorithm only deals with undirected graphs
    communities_result = nx_community.asyn_fluidc(graph_communities, k, max_iter, seed)
    _nx_community_data_to_graph(graph, communities_result)
    return graph


def add_girvan_newman(graph, most_valuable_edge=None):
    communities_result = nx_community.girvan_newman(graph, most_valuable_edge)
    # The girvan_newman algorithm returns communities at each level of the iteration.
    # We choose the top level community.
    top_level_communities = next(communities_result)
    _nx_community_data_to_graph(graph, top_level_communities)
    return graph

