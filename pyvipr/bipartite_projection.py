# -*- coding: utf-8 -*-
#    Copyright (C) 2017-2019 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
# Authors: Aric Hagberg <aric.hagberg@gmail.com>
#          Jordi Torrents <jtorrents@milnou.net>
# Modifications copyright (C) 2019 Oscar Ortega.
# Modified code to include the data of edges in the projection
import networkx as nx


def species_projected_graph(B, reactions, nodes):
    r"""Returns the projection of a species-reactions bipartite graph
     onto the species nodes set.

    Returns the graph G that is the projection of the bipartite graph B
    onto the specified nodes. They retain their attributes and are connected
    in G if they have a common neighbor in B. Nodes that can be connected
    in the graph but belong to the same reactant list of a reaction won't be
    connected as in the species graph reactants should only be connected
    to products

    Parameters
    ----------
    B : NetworkX graph
      The input graph should be bipartite.

    reactions : list-like
      List of reactions used to avoid linking of species that are both
      reactants in the reaction.

    nodes : list or iterable
      Nodes to project onto (the "bottom" nodes).

    Returns
    -------
    Graph : NetworkX MultiDigraph
       A graph that is the projection onto the given nodes.

    Notes
    -----
    No attempt is made to verify that the input graph B is bipartite.
    Returns a simple graph that is the projection of the bipartite graph B
    onto the set of nodes given in list nodes.

    The graph and node properties are (shallow) copied to the projected graph.

    """
    # if B.is_directed():
    #     G = nx.DiGraph()
    # else:
    #     G = nx.Graph()
    G = nx.MultiDiGraph()
    G.graph.update(B.graph)
    G.add_nodes_from((n, B.nodes[n]) for n in nodes)

    for u in nodes:
        for nbr in B[u]:
            r_idx = int(nbr[1:])
            if int(u[1:]) in reactions[r_idx]['products'] and \
                    reactions[r_idx]['reversible']:
                reactants = reactions[r_idx]['products']
            else:
                reactants = reactions[r_idx]['reactants']
            for v in B[nbr]:
                if v != u and int(v[1:]) not in reactants:
                    if not G.has_edge(u, v, nbr):
                        G.add_edge(u, v, key=nbr)
    return G
