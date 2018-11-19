from collections import OrderedDict
import networkx as nx
import json
from .util_networkx import from_networkx
import collections
import numpy
import pysb
import pysbjupyter.util as hf
from pysb.bng import generate_equations
from networkx.algorithms import bipartite


class OrderedGraph(nx.DiGraph):
    """
    Networkx Digraph that stores the nodes in the order they are input
    """
    node_dict_factory = OrderedDict
    adjlist_outer_dict_factory = OrderedDict
    adjlist_inner_dict_factory = OrderedDict
    edge_attr_dict_factory = OrderedDict


class StaticViz(object):
    """
    Class to visualize models and their dynamics

    Parameters
    ----------
    model : pysb.Model
        Model to visualize.
    """
    mach_eps = numpy.finfo(float).eps

    def __init__(self, model):
        # Need to create a model visualization base and then do independent visualizations: static and dynamic
        self.model = model
        self.graph = None
        self.passengers = []
        generate_equations(self.model)

    # This is a function to merge several nodes into one in a Networkx graph

    @staticmethod
    def merge_nodes(G, nodes, new_node, **attr):
        """
        Merges the selected `nodes` of the graph G into one `new_node`,
        meaning that all the edges that pointed to or from one of these
        `nodes` will point to or from the `new_node`.
        attr_dict and **attr are defined as in `G.add_node`.
        """
        G.add_node(new_node, **attr)  # Add the 'merged' node

        for n1, n2, data in G.edges(data=True):
            # For all edges related to one of the nodes to merge,
            # make an edge going to or coming from the `new gene`.
            if n1 in nodes:
                G.add_edge(new_node, n2, **data)
            elif n2 in nodes:
                G.add_edge(n1, new_node, **data)

        for n in nodes:  # remove the merged nodes
            G.remove_node(n)

    def species_view(self, get_passengers=True, cluster_info=None, dom_paths=None):
        """
        Generates a dictionary with the model graph data that can be converted in the Cytoscape.js JSON format

        Parameters
        ----------
        get_passengers : bool
            if True, nodes that only have one incoming or outgoing edge are painted with a different color
        cluster_info : dict
            A dictionary with the information of the clusters of mode of signal execution

        Examples
        --------
        >>> from pysb.examples.earm_1_0 import model
        >>> viz = StaticViz(model)
        >>> data = viz.species_view()

        Returns
        -------
        A Dictionary Object that can be converted into Cytoscape.js JSON
        """
        graph = self.species_graph(get_passengers=get_passengers)
        if cluster_info:
            # TODO check structure of cluster_info
            if isinstance(cluster_info, list):
                for c in cluster_info:
                    self._add_cluster_info(graph, c)
            elif isinstance(cluster_info, dict):
                self._add_cluster_info(graph, cluster_info)
            else:
                raise TypeError('Object no supported')
        if dom_paths is not None:
            graph.graph['paths'] = dom_paths
        g_layout = self.dot_layout(graph)
        data = self.graph_to_json(sp_graph=graph, layout=g_layout)
        return data

    def sp_rxns_bidirectional_view(self, dom_paths=None):
        """
        Generates a dictionary with the info of a bipartite graph where one set of nodes is the model species
        and the other set is the model bidirectional reactions

        Parameters
        ----------
        dom_paths : list
            list of dominant paths

        Returns
        -------
        A dictionary object with the graph information
        """
        graph = self.sp_rxns_bidirectional_graph()
        if dom_paths is not None:
            graph.graph['paths'] = dom_paths
        g_layout = self.dot_layout(graph)
        data = self.graph_to_json(sp_graph=graph, layout=g_layout)
        return data

    def sp_rxns_view(self):
        """
        Generates a dicionary with the info of a bipartite graph where one set of nodes is the model species
        and the other set is the unidirectional reactions
        Returns
        -------
        A dictionary object with the graph information
        """
        graph = self.sp_rxns_graph()
        g_layout = self.dot_layout(graph)
        data = self.graph_to_json(sp_graph=graph, layout=g_layout)
        return data

    def sp_rules_view(self):
        """
        Generates a dictionary with the info of a bipartite graph where one set of nodes is the model species
        and the other set is the model rules
        Returns
        -------

        """
        rules_graph = self.rules_graph()
        rules_graph = self.graph_merged_pair_edges(rules_graph)
        g_layout = self.dot_layout(rules_graph)
        data = self.graph_to_json(sp_graph=rules_graph, layout=g_layout)
        return data

    def projections_view(self, project_to='species_reactions'):
        """
        Generates a dictionary wit the info of a graph repesenting the PySB model.

        Parameters
        ----------
        project_to: str
            Nodes to which the graph is going to be projected. Options are:
            'species_reactions', 'reactions', 'rules', 'species_rules'

        Returns
        -------
        A dictionary object with the graph information

        """
        if project_to == 'species_reactions' or project_to == 'reactions':
            bipartite_graph = self.sp_rxns_bidirectional_graph()
        elif project_to == 'rules' or project_to == 'species_rules':
            bipartite_graph = self.rules_graph()
        else:
            raise ValueError('Projection not valid')

        projected_graph = self.projected_graph(bipartite_graph, project_to)
        g_layout = self.dot_layout(projected_graph)
        data = self.graph_to_json(sp_graph=projected_graph, layout=g_layout)
        return data

    def species_graph(self, get_passengers=False):
        """
        Creates a nx.DiGraph graph of the model species

        Returns
        -------
        A :class: nx.Digraph graph that has the information for the visualization of the model
        """
        sp_graph = OrderedGraph(name=self.model.name, graph={'rankdir':'LR'}, paths=[])
        if get_passengers:
            self.passengers = hf.find_nonimportant_nodes(self.model)

        # TODO: there are reactions that generate parallel edges that are not taken into account because netowrkx
        # digraph only allows one edge between two nodes

        for idx in range(len(self.model.species)):
            species_node = 's%d' % idx
            # Setting the information about the node
            node_data = {'label': hf.parse_name(self.model.species[idx])}
            if idx in self.passengers:
                node_data['background_color'] = "#162899"
            else:
                node_data['background_color'] = "#2b913a"
            node_data['shape'] = 'ellipse'

            sp_graph.add_node(species_node, **node_data)

        for reaction in self.model.reactions_bidirectional:
            reactants = set(reaction['reactants'])
            products = set(reaction['products'])
            attr_reversible = {'source_arrow_shape': 'diamond', 'target_arrow_shape': 'triangle',
                               'source_arrow_fill': 'hollow'} if reaction['reversible'] \
                                else {'source_arrow_shape': 'none', 'target_arrow_shape': 'triangle',
                                      'source_arrow_fill': 'filled'}
            for s in reactants:
                for p in products:
                    self._r_link_species(sp_graph, s, p, **attr_reversible)
        return sp_graph

    @staticmethod
    def _r_link_species(graph, s, r, **attrs):
        """
        Links two nodes in a species graph
        Parameters
        ----------
        s : int
            Source node
        r: int
            Target node
        attrs: dict
            Other attributes for edges

        Returns
        -------

        """

        nodes = ('s{0}'.format(s), 's{0}'.format(r))
        attrs.setdefault('arrowhead', 'normal')
        graph.add_edge(*nodes, **attrs)

    def sp_rxns_bidirectional_graph(self):
        """
        Creates a bipartite nx.DiGraph graph where one set of nodes is the model species
        and the other set is the model bidirectional reactions.

        Returns
        -------
        A :class: nx.Digraph graph that has the information for the visualization of the model
        """

        graph = OrderedGraph(name=self.model.name, graph={'rankdir':'LR'})
        ic_species = [cp for cp, parameter in self.model.initial_conditions]
        for i, cp in enumerate(self.model.species):
            species_node = 's%d' % i
            slabel = hf.parse_name(self.model.species[i])
            color = "#ccffcc"
            # color species with an initial condition differently
            if len([s for s in ic_species if s.is_equivalent_to(cp)]):
                color = "#aaffff"
            graph.add_node(species_node,
                           label=slabel,
                           shape="ellipse",
                           background_color=color,
                           bipartite=0)
        for i, reaction in enumerate(self.model.reactions_bidirectional):
            reaction_node = 'r%d' % i
            graph.add_node(reaction_node,
                           label=reaction_node,
                           shape="roundrectangle",
                           background_color="#d3d3d3",
                           bipartite=1)
            reactants = set(reaction['reactants'])
            products = set(reaction['products'])
            modifiers = reactants & products
            reactants = reactants - modifiers
            products = products - modifiers
            attr_reversible = {'source_arrow_shape': 'triangle', 'target_arrow_shape': 'triangle',
                               'source_arrow_fill': 'hollow'} if reaction['reversible'] \
                                else {'source_arrow_shape': 'none', 'target_arrow_shape': 'triangle', 'source_arrow_fill': 'filled'}
            for s in reactants:
                self._r_link_bipartite(graph, s, i, **attr_reversible)
            for s in products:
                self._r_link_bipartite(graph, s, i, _flip=True, **attr_reversible)
            for s in modifiers:
                attr_modifiers = {'target_arrow_shape':'diamond'}
                self._r_link_bipartite(graph, s, i, **attr_modifiers)
        return graph

    def sp_rxns_graph(self):
        """
        Creates a bipartite nx.DiGraph graph where one set of nodes is the model species
        and the other set is the model unidirectional reactions.

        Returns
        -------
        A :class: nx.Digraph graph that has the information for the visualization of the model
        """
        graph = OrderedGraph(name=self.model.name, graph={'rankdir': 'LR'})
        ic_species = [cp for cp, parameter in self.model.initial_conditions]
        for i, cp in enumerate(self.model.species):
            species_node = 's%d' % i
            slabel = hf.parse_name(self.model.species[i])
            color = "#ccffcc"
            # color species with an initial condition differently
            if len([s for s in ic_species if s.is_equivalent_to(cp)]):
                color = "#aaffff"
            graph.add_node(species_node,
                           label=slabel,
                           shape="ellipse",
                           background_color=color,
                           bipartite=0)
        for i, reaction in enumerate(self.model.reactions):
            reaction_node = 'r%d' % i
            graph.add_node(reaction_node,
                           label=reaction_node,
                           shape="roundrectangle",
                           background_color="#d3d3d3",
                           bipartite=1)
            reactants = set(reaction['reactants'])
            products = set(reaction['products'])
            modifiers = reactants & products
            reactants = reactants - modifiers
            products = products - modifiers
            attr_edges = {'source_arrow_shape': 'none', 'target_arrow_shape': 'triangle', 'source_arrow_fill': 'filled'}
            for s in reactants:
                self._r_link_bipartite(graph, s, i, **attr_edges)
            for s in products:
                self._r_link_bipartite(graph, s, i, _flip=True, **attr_edges)
            for s in modifiers:
                self._r_link_bipartite(graph, s, i, **attr_edges)
        return graph

    def rules_graph(self):
        """
        Creates a bipartite nx.DiGraph graph where one set of nodes is the model species
        and the other set is the model rules.

        Returns
        -------
        A :class: nx.Digraph graph that has the information for the visualization of the model
        """
        graph = self.sp_rxns_graph()
        nodes2merge = self.merge_reactions2rules()
        node_attrs = {'shape': 'roundrectangle', 'background_color': '#ff4c4c', 'bipartite':1}
        for rule, rxns in nodes2merge.items():
            node_attrs['label'] = rule
            self.merge_nodes(graph, rxns, rule, **node_attrs)
        return graph

    def projected_graph(self, graph, project_to='species'):
        if project_to == 'species_reactions' or project_to == 'species_rules':
            nodes = {n for n, d in graph.nodes(data=True) if d['bipartite']==0}
        elif project_to == 'reactions' or project_to == 'rules':
            nodes = {n for n, d in graph.nodes(data=True) if d['bipartite']==1}
        else:
            raise ValueError('Projection not valid')
        projected_graph = bipartite.projected_graph(graph, nodes)
        projected_graph = self.graph_merged_pair_edges(projected_graph)

        return projected_graph

    @staticmethod
    def graph_merged_pair_edges(graph):
        """
        Merges pair of edges that are reversed
        Parameters
        ----------
        graph: nx.DiGraph
            The networkx directed graph whose pairs of edges ((u, v), (v, u)) are going to be merged
        Returns
        -------
        A :class: nx.Digraph graph that has the information for the visualization of the model
        """
        edges_to_delete = []
        edges_attributes = {}
        for edge in graph.edges():
            if edge in edges_to_delete:
                continue
            if graph.has_edge(*edge[::-1]):
                attr_reversible = {'source_arrow_shape': 'triangle', 'target_arrow_shape': 'triangle',
                               'source_arrow_fill': 'hollow'}
                edges_attributes[edge] = attr_reversible
                edges_to_delete.append(edge[::-1])
            else:
                attr_irreversible = {'source_arrow_shape': 'none', 'target_arrow_shape': 'triangle',
                                     'source_arrow_fill': 'filled'}
                edges_attributes[edge] = attr_irreversible
        graph.remove_edges_from(edges_to_delete)
        nx.set_edge_attributes(graph, edges_attributes)
        return graph

    def merge_reactions2rules(self):
        """
        Merges the model reactions into each of the rules from which the reactions come form.
        Returns
        -------

        """
        rxn_per_rule = {}
        for rule in self.model.rules:
            rxns = []
            for i, rxn in enumerate(self.model.reactions):
                if rxn['rule'][0] == rule.name:
                    rxns.append('r{0}'.format(i))
            rxn_per_rule[rule.name] = rxns
        return rxn_per_rule


    @staticmethod
    def _r_link_bipartite(graph, s, r, **attrs):
        """
        Links two nodes in a species graph
        Parameters
        ----------
        s : int
            Source node
        r: int
            Target node
        attrs: dict
            Other attributes for edges

        Returns
        -------

        """

        nodes = ('s{0}'.format(s), 'r{0}'.format(r))
        if attrs.get('_flip'):
            del attrs['_flip']
            nodes = nodes[::-1]
        attrs.setdefault('arrowhead', 'normal')
        graph.add_edge(*nodes, **attrs)

    @staticmethod
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

    @staticmethod
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
        ordered_pos = collections.OrderedDict((node, pos[node]) for node in sp_graph.nodes())
        return ordered_pos

    @staticmethod
    def _add_cluster_info(graph, cluster_info):
        node_backgrounds = {}
        node_percentages = {}
        node_repres = {}
        node_clus_scores = {}
        for sp_info in cluster_info['cluster_info']:
            sp = [idx for idx in sp_info.keys() if isinstance(idx, int)]
            sp = sp[0]
            percs = []
            bgs = []
            repres = []
            scores = []
            for perc in sp_info[sp].values():
                if perc[0] < 1:
                    perc_r = perc[0] * 100
                else:
                    perc_r = perc[0]
                percs.append(perc_r)
                bgs.append(perc[1])
                repres.append(perc[2].tolist())
                scores.append(sp_info['best_silh'])
            node_percentages['s{}'.format(sp)] = percs
            node_backgrounds['s{}'.format(sp)] = bgs
            node_repres['s{}'.format(sp)] = repres
            node_clus_scores['s{}'.format(sp)] = scores

        rxns_type = cluster_info['rxns_type']
        if float(nx.__version__) >= 2:
            nx.set_node_attributes(graph, node_backgrounds, 'clus_colors_' + rxns_type)
            nx.set_node_attributes(graph, node_percentages, 'clus_perc_' + rxns_type)
            nx.set_node_attributes(graph, node_repres, 'clus_repres_' + rxns_type)
            nx.set_node_attributes(graph, node_clus_scores, 'clus_scores_' + rxns_type)
        else:
            nx.set_node_attributes(graph, 'clus_colors_' + rxns_type, node_backgrounds)
            nx.set_node_attributes(graph, 'clus_perc_' + rxns_type, node_percentages)
            nx.set_node_attributes(graph, 'clus_repres_' + rxns_type, node_repres)
            nx.set_node_attributes(graph, 'clus_scores_' + rxns_type, node_clus_scores)
        return