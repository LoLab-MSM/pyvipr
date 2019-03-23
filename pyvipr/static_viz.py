from collections import OrderedDict
import networkx as nx
import json
from .util_networkx import from_networkx
import collections
import pysb
import pyvipr.util as hf
from pysb.bng import generate_equations
from networkx.algorithms import bipartite
from community import best_partition


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
        PySB Model to visualize.
    """

    def __init__(self, model):
        # Need to create a model visualization base and then do independent visualizations: static and dynamic
        self.model = model
        self.graph = None
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
        newG = G.copy()

        for n1, n2, data in newG.edges(data=True):
            # For all edges related to one of the nodes to merge,
            # make an edge going to or coming from the `new gene`.
            if n1 in nodes:
                G.add_edge(new_node, n2, **data)
            elif n2 in nodes:
                G.add_edge(n1, new_node, **data)

        for n in nodes:  # remove the merged nodes
            G.remove_node(n)

    def species_view(self):
        """
        Generate data to create a species network

        Parameters
        ----------

        Examples
        --------
        >>> from pysb.examples.earm_1_0 import model
        >>> viz = StaticViz(model)
        >>> data = viz.species_view()

        Returns
        -------
        A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
        contains all the information (nodes,edges, positions) to generate a cytoscapejs network.
        """
        graph = self.species_graph()
        g_layout = dot_layout(graph)
        data = graph_to_json(sp_graph=graph, layout=g_layout)
        return data

    def species_compartments_view(self):
        """
        Generate data to create a species networks and their respective compartments
        Returns
        -------
        A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
        contains all the information (nodes, parent_nodes, edges, positions) to
         generate a cytoscapejs network.
        """
        graph = self.compartments_data_graph()
        g_layout = dot_layout(graph)
        data = graph_to_json(sp_graph=graph, layout=g_layout)
        return data

    def compartments_data_graph(self):
        # Check if model has comparments
        if not self.model.compartments:
            raise ValueError('Model has no compartments')
        graph = self.species_graph()
        compartment_nodes = []
        for c in self.model.compartments:
            if c.parent is not None:
                compartment_nodes.append((c.name, dict(parent=c.parent.name)))
            else:
                compartment_nodes.append(c.name)

        graph.add_nodes_from(compartment_nodes, NodeType='compartment')
        # Determining compartment node family tree
        # Determine species compartment
        sp_compartment = {}
        for idx, sp in enumerate(self.model.species):
            monomers = sp.monomer_patterns
            monomers_comp = {m.compartment.name: m.compartment.size for m in monomers}
            smallest_comp = min(monomers_comp, key=monomers_comp.get)
            sp_compartment['s{0}'.format(idx)] = smallest_comp
        nx.set_node_attributes(graph, sp_compartment, 'parent')
        return graph

    def communities_view(self, random_state=None):
        """
        Use a community detection algorithm to find groups of nodes that are densely connected.
        It generates the data to create a network with compound nodes that hold the communities.
        Returns
        -------
        A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
        contains all the information (nodes,edges, parent nodes, positions) to generate
        a cytoscapejs network.
        """
        graph = self.communities_data_graph(random_state=random_state)
        g_layout = dot_layout(graph)
        data = graph_to_json(sp_graph=graph, layout=g_layout)
        return data

    def communities_data_graph(self, random_state=None):
        graph = self.species_graph()
        graph_communities = graph.copy().to_undirected()  # Louvain algorithm only deals with undirected graphs
        communities = best_partition(graph_communities, random_state=random_state)
        # compound nodes to add to hold communities
        cnodes = set(communities.values())
        graph.add_nodes_from(cnodes, NodeType='community')
        nx.set_node_attributes(graph, communities, 'parent')
        return graph

    def sp_rxns_bidirectional_view(self):
        """
        Generate a dictionary with the info of a bipartite graph where one set of
        nodes is the model species and the other set is the model bidirectional reactions

        Parameters
        ----------

        Returns
        -------
        A dictionary object with the graph information
        """
        graph = self.sp_rxns_bidirectional_graph()
        g_layout = dot_layout(graph)
        data = graph_to_json(sp_graph=graph, layout=g_layout)
        return data

    def sp_rxns_view(self):
        """
        Generates a dictionary with the info of a bipartite graph where one set of nodes is the model species
        and the other set is the unidirectional reactions
        Returns
        -------
        A dictionary object with the graph information.
        """
        graph = self.sp_rxns_graph()
        g_layout = dot_layout(graph)
        data = graph_to_json(sp_graph=graph, layout=g_layout)
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
        g_layout = dot_layout(rules_graph)
        data = graph_to_json(sp_graph=rules_graph, layout=g_layout)
        return data

    def sp_rules_functions_view(self):
        """
        Generates a dictionary with the info of a bipartite graph where one set of nodes is the model species
        and the other set is the model rules. Additionally, it adds information of the functions from which
        the rules come from.
        Returns
        -------

        """
        rules_graph = self.rules_graph()
        rules_graph = self.graph_merged_pair_edges(rules_graph)
        rule_functions = {rule.name: rule._function for rule in self.model.rules}
        unique_functions = set(rule_functions.values())
        nx.set_node_attributes(rules_graph, rule_functions, 'parent')
        rules_graph.add_nodes_from(unique_functions, NodeType='function')
        g_layout = dot_layout(rules_graph)
        data = graph_to_json(sp_graph=rules_graph, layout=g_layout)
        return data

    def sp_rules_modules_view(self):
        """
        Generates a dictionary with the info of a bipartite graph where one set of nodes is the model species
        and the other set is the model rules. Additionally, it adds information of the modules from which
        the rules come from.
        Returns
        -------

        """
        rules_graph = self.rules_graph()
        rules_graph = self.graph_merged_pair_edges(rules_graph)

        # Unique modules used in the model
        unique_modules = [m for m in self.model.modules if not m.startswith('_')]
        # Remove outer model file to not look further modules that are not related to
        # the model
        unique_modules.remove(self.model.name)
        module_parents = {}
        # pysb components have a modules list that starts from the inner frame
        # to the outer frame.
        for module in unique_modules:
            total_parents = []
            for rule in self.model.rules:
                mods = rule._modules
                try:
                    mod_idx = mods.index(module)
                    module_parent = mods[mod_idx + 1]
                except (ValueError, IndexError):
                    continue
                total_parents.append(module_parent)

            total_parents = list(set(total_parents))
            if module in total_parents:
                total_parents.remove(module)

            if len(total_parents) >= 2:
                for idx, p in enumerate(total_parents):
                    module_parents[module + str(idx)] = p
            else:
                module_parents[module] = total_parents[0]

        rules_module = {}
        for rule in self.model.rules:
            m = rule._modules[0]
            if m not in module_parents.keys():
                m_parent = rule._modules[1]
                m_parent_child = list(module_parents.keys())[list(module_parents.values()).index(m_parent)]
                rules_module[rule.name] = m_parent_child
            else:
                rules_module[rule.name] = m

        module_parent_nodes = list(module_parents.keys())
        module_parent_nodes.append(self.model.name)
        rules_graph.add_nodes_from(module_parent_nodes, NodeType='module')
        nx.set_node_attributes(rules_graph, module_parents, 'parent')
        nx.set_node_attributes(rules_graph, rules_module, 'parent')
        g_layout = dot_layout(rules_graph)
        data = graph_to_json(sp_graph=rules_graph, layout=g_layout)
        return data

    def projections_view(self, project_to='species_reactions'):
        """
        Generates a dictionary with the info of a graph representing the PySB model.

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
        g_layout = dot_layout(projected_graph)
        data = graph_to_json(sp_graph=projected_graph, layout=g_layout)
        return data

    def projected_species_reactions_view(self):
        return self.projections_view('species_reactions')

    def projected_reactions_view(self):
        return self.projections_view('reactions')

    def projected_rules_view(self):
        return self.projections_view('rules')

    def projected_species_rules_view(self):
        return self.projections_view('species_rules')

    def species_graph(self):
        """
        Creates a nx.DiGraph graph of the model species

        Returns
        -------
        A :class: nx.Digraph graph that has the information for the visualization of the model
        """
        sp_graph = OrderedGraph(name=self.model.name, graph={'rankdir':'LR'}, paths=[])

        # TODO: there are reactions that generate parallel edges that are not taken into account because netowrkx
        # digraph only allows one edge between two nodes

        for idx in range(len(self.model.species)):
            species_node = 's%d' % idx
            # Setting the information about the node
            node_data = dict(label=hf.parse_name(self.model.species[idx]),
                             background_color="#2b913a",
                             shape='ellipse',
                             NodeType='species')
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
                           NodeType='species',
                           bipartite=0)
        for j, reaction in enumerate(self.model.reactions_bidirectional):
            reaction_node = 'r%d' % j
            graph.add_node(reaction_node,
                           label=reaction_node,
                           shape="roundrectangle",
                           background_color="#d3d3d3",
                           NodeType='reaction',
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
                self._r_link_bipartite(graph, s, j, **attr_reversible)
            for s in products:
                self._r_link_bipartite(graph, s, j, _flip=True, **attr_reversible)
            for s in modifiers:
                attr_modifiers = {'target_arrow_shape':'diamond'}
                self._r_link_bipartite(graph, s, j, **attr_modifiers)
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
                           NodeType='species',
                           bipartite=0)
        for i, reaction in enumerate(self.model.reactions):
            reaction_node = 'r%d' % i
            graph.add_node(reaction_node,
                           label=reaction_node,
                           shape="roundrectangle",
                           background_color="#d3d3d3",
                           NodeType='reaction',
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
        # Merge reactions into the rules that they come from
        nodes2merge = self.merge_reactions2rules()
        node_attrs = {'shape': 'roundrectangle', 'background_color': '#ff4c4c',
                      'NodeType': 'rule', 'bipartite': 1}
        for rule_info, rxns in nodes2merge.items():
            node_attrs['label'] = rule_info[0]
            node_attrs['index'] = 'rule' + str(rule_info[1])
            self.merge_nodes(graph, rxns, rule_info[0], **node_attrs)
        return graph

    def projected_graph(self, graph, project_to='species'):
        """
        Project a bipartite graph into one of the sets of nodes
        Parameters
        ----------
        graph: nx.DiGraph
            a networkx bipartite graph
        project_to: str
            One of the following options: `species_reactions`, `species_rules`,
            `reactions`, `rules`

        Returns
        -------
        a nx.DiGraph
        """
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
        for r_idx, rule in enumerate(self.model.rules):
            rxns = []
            for i, rxn in enumerate(self.model.reactions):
                if rxn['rule'][0] == rule.name:
                    rxns.append('r{0}'.format(i))
            rxn_per_rule[(rule.name, r_idx)] = rxns
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
    ordered_pos = collections.OrderedDict((node, pos[node]) for node in sp_graph.nodes())
    return ordered_pos
