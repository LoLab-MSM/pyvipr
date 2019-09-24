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


def species_projected_graph(B, reactions, nodes, unireactions=False):
    r"""Returns the projection of a species-reactions bipartite graph
     onto the species nodes set.

    Returns the graph G that is the projection of the bipartite graph B
    onto the specified nodes. They retain their attributes and are connected
    in G if they have a common neighbor in B. Nodes that can be connected
    in the graph but belong to the same reactant list of a reaction won't be
    connected to maintain consistency of the way that the species graph is generated

    Parameters
    ----------
    B : NetworkX graph
      The input graph should be bipartite.

    reactions : list-like
      List of reactions used to avoid linking of species that are both
      reactants in the reaction.

    nodes : list or iterable
      Nodes to project onto (the "bottom" nodes).

    unireactions: bool (default=False)
       If True, the reactions argument correspond to uni-directional
       reactions instead of bidirectional reactions.

    Returns
    -------
    Graph : NetworkX graph
       A graph that is the projection onto the given nodes.

    Notes
    -----
    No attempt is made to verify that the input graph B is bipartite.
    Returns a simple graph that is the projection of the bipartite graph B
    onto the set of nodes given in list nodes.

    Directed graphs are allowed as input.  The output will also then
    be a directed graph with edges if there is a directed path between
    the nodes.

    The graph and node properties are (shallow) copied to the projected graph.

    See :mod:`bipartite documentation <networkx.algorithms.bipartite>`
    for further details on how bipartite graphs are handled in NetworkX.

    """
    if B.is_directed():
        G = nx.DiGraph()
    else:
        G = nx.Graph()
    G.graph.update(B.graph)
    G.add_nodes_from((n, B.nodes[n]) for n in nodes)
    if unireactions:
        for u in nodes:
            nbrs2 = set()
            for nbr in B[u]:
                r_idx = int(nbr[1:])
                reactants = reactions[r_idx]['reactants']
                for v in B[nbr]:
                    if v != u and int(v[1:]) not in reactants:
                        nbrs2.add(v)

            G.add_edges_from((u, n) for n in nbrs2)
    else:
        for u in nodes:
            nbrs2 = set()
            for nbr in B[u]:
                r_idx = int(nbr[1:])
                if int(u[1:]) in reactions[r_idx]['products'] and \
                        reactions[r_idx]['reversible']:
                    reactants = reactions[r_idx]['products']
                else:
                    reactants = reactions[r_idx]['reactants']
                for v in B[nbr]:
                    if v != u and int(v[1:]) not in reactants:
                        nbrs2.add(v)

            G.add_edges_from((u, n) for n in nbrs2)
    return G
