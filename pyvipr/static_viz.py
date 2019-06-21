import networkx as nx
import json
from .util_networkx import from_networkx
import pysb
import pyvipr.util as hf
from pysb.bng import generate_equations
from networkx.algorithms import bipartite
from community import best_partition, generate_dendrogram


class StaticViz(object):
    """
    Class to generate static visualizations of systems biology models

    Parameters
    ----------
    model : pysb.Model
        PySB Model to visualize.
    """

    def __init__(self, model):
        # Need to create a model visualization base and then do independent visualizations: static and dynamic
        self.model = model
        self.graph = None

    @staticmethod
    def merge_nodes(G, nodes, new_node, **attr):
        """
        Merges the selected `nodes` of the graph G into one `new_node`,
        meaning that all the edges that pointed to or from one of these
        `nodes` will point to or from the `new_node`.
        attr_dict and `**attr` are defined as in `G.add_node`.
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

    def sp_view(self):
        """
        Generate a dictionary that contains the species network information

        Parameters
        ----------

        Examples
        --------
        >>> from pysb.examples.earm_1_0 import model
        >>> viz = StaticViz(model)
        >>> data = viz.sp_view()

        Returns
        -------
        dict
            A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
            contains all the information (nodes,edges, positions) to generate a cytoscapejs network.
        """
        graph = self.species_graph()
        data = graph_to_json(sp_graph=graph)
        return data

    def sp_comp_view(self):
        """
        Generate a dictionary that contains the information about the species 
        network. Species are grouped by the compartments they belong to

        Returns
        -------
        dict
            A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
            contains all the information (nodes, parent_nodes, edges, positions) to
            generate a cytoscapejs network.
        """
        graph = self.compartments_data_graph()
        data = graph_to_json(sp_graph=graph)
        return data

    def compartments_data_graph(self):
        """
        Create a networkx DiGraph. Check for compartments in a model and add 
        the compartments as compound nodes where the species are located

        Returns
        -------
        nx.Digraph
            Graph with model species and compartments
        
        Raises
        ------
        ValueError
            Model has not compartments
        """
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

    def sp_comm_view(self, random_state=None):
        """
        Use the Louvain algorithm https://en.wikipedia.org/wiki/Louvain_Modularity
        for community detection to find groups of nodes that are densely connected.
        It generates the data to create a network with compound nodes that hold the communities.

        Parameters
        ==========
        random_state : int, optional
            Random state seed use by the community detection algorithm, by default None

        Returns
        -------
        dict
            A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
            contains all the information (nodes,edges, parent nodes, positions) to generate
            a cytoscapejs network.
        """
        graph = self.communities_data_graph(random_state=random_state)
        data = graph_to_json(sp_graph=graph)
        return data

    def sp_comm_hierarchy_view(self, random_state=None):
        """
        Use the Louvain algorithm https://en.wikipedia.org/wiki/Louvain_Modularity
        for community detection to find groups of nodes that are densely connected.
        It generates the data of all the intermediate clusters obtained during the Louvain
        algorithm generate to create a network with compound nodes that hold the communities.

        Parameters
        ==========
        random_state : int, optional
            Random state seed use by the community detection algorithm, by default None

        Returns
        -------
        dict
            A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
            contains all the information (nodes,edges, parent nodes, positions) to generate
            a cytoscapejs network.
        """
        graph = self.communities_data_graph(all_levels=True, random_state=random_state)
        data = graph_to_json(sp_graph=graph)
        return data

    def communities_data_graph(self, all_levels=False, random_state=None):
        """
        Create a networkx DiGraph. It applies the Louvain algorithm to detect
        communities and add that information to the graph
        
        Parameters
        ----------
        all_levels : bool
            Indicates if the generated graph contains the information about the
            clusters obtained at each iteration of the Louvain algorithm
        random_state : int, optional
            Random state seed use by the community detection algorithm, by default None
        
        Returns
        -------
        nx.DiGraph
            A networkx DiGraph where the nodes have a `parent` property that correspond
            to the community they belong to
        """
        graph = self.species_graph()
        graph_communities = graph.copy().to_undirected()  # Louvain algorithm only deals with undirected graphs
        if all_levels:
            # We add the first communities detected, The dendrogram at level 0 contains the nodes as keys
            # and the clusters they belong to as values.
            dendrogram = generate_dendrogram(graph_communities, random_state=random_state)
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

        Returns
        -------
        dict
            A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
            contains all the information (nodes,edges, parent nodes, positions) to generate
            a cytoscapejs network.

        """
        graph = self.sp_rxns_bidirectional_graph()
        data = graph_to_json(sp_graph=graph)
        return data

    def sp_rxns_view(self):
        """
        Generates a dictionary with the info of a bipartite graph where one set of nodes is the model species
        and the other set is the unidirectional reactions

        Returns
        -------
        dict
            A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
            contains all the information (nodes,edges, parent nodes, positions) to generate
            a cytoscapejs network.
        """
        graph = self.sp_rxns_graph()
        data = graph_to_json(sp_graph=graph)
        return data

    def sp_rules_view(self):
        """
        Generates a dictionary with the info of a bipartite graph where one set of nodes is the model species
        and the other set is the model rules
        
        Returns
        -------
        dict
            A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
            contains all the information (nodes,edges, parent nodes, positions) to generate
            a cytoscapejs network.
        """
        rules_graph = self.rules_graph()
        rules_graph = self.graph_merged_pair_edges(rules_graph)
        data = graph_to_json(sp_graph=rules_graph)
        return data

    def sp_rules_fxns_view(self):
        """
        Generates a dictionary with the info of a bipartite graph where one set of nodes is the model species
        and the other set is the model rules. Additionally, it adds information of the functions from which
        the rules come from.
        
        Returns
        -------
        dict
            A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
            contains all the information (nodes,edges, parent nodes, positions) to generate
            a cytoscapejs network.
        """
        rules_graph = self.rules_graph()
        rules_graph = self.graph_merged_pair_edges(rules_graph)
        rule_functions = {rule.name: rule._function for rule in self.model.rules}
        unique_functions = set(rule_functions.values())
        nx.set_node_attributes(rules_graph, rule_functions, 'parent')
        rules_graph.add_nodes_from(unique_functions, NodeType='function')
        data = graph_to_json(sp_graph=rules_graph)
        return data

    def sp_rules_mod_view(self):
        """
        Generates a dictionary with the info of a bipartite graph where one set of nodes is the model species
        and the other set is the model rules. Additionally, it adds information of the modules from which
        the rules come from.
        
        Returns
        -------
        dict
            A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
            contains all the information (nodes,edges, parent nodes, positions) to generate
            a cytoscapejs network.
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
        data = graph_to_json(sp_graph=rules_graph)
        return data

    def sbgn_view(self):
        sbgn_graph = self.sbgn_graph()
        data = graph_to_json(sbgn_graph)
        return data

    def projections_view(self, project_to='species_reactions'):
        """
        Project a bipartite graph to the type of node defined in `project to`.
        Generates a dictionary with the info of a graph representing the PySB model.

        Parameters
        ----------
        project_to: str
            Nodes to which the graph is going to be projected. Options are:
            'species_reactions', 'reactions', 'rules', 'species_rules'

        Returns
        -------
        dict
            A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
            contains all the information (nodes,edges, parent nodes, positions) to generate
            a cytoscapejs network.
        """
        if project_to == 'species_reactions' or project_to == 'reactions':
            bipartite_graph = self.sp_rxns_bidirectional_graph()
        elif project_to == 'rules' or project_to == 'species_rules':
            bipartite_graph = self.rules_graph()
        else:
            raise ValueError('Projection not valid')

        projected_graph = self.projected_graph(bipartite_graph, project_to)
        data = graph_to_json(sp_graph=projected_graph)
        return data

    def projected_species_reactions_view(self):
        return self.projections_view('species_reactions')

    def projected_reactions_view(self):
        return self.projections_view('reactions')

    def projected_rules_view(self):
        return self.projections_view('rules')

    def projected_species_rules_view(self):
        return self.projections_view('species_rules')

    def _sp_initial(self, sp):
        """
        Get initial condition of a species
        Parameters
        ----------
        sp: pysb.ComplexPattern, pysb species

        Returns
        -------

        """
        sp_0 = 0
        for spInitial in self.model.initials:
            if spInitial.pattern.is_equivalent_to(sp):
                sp_0 = spInitial.value.value
                break
        return sp_0

    def species_graph(self):
        """
        Creates a nx.DiGraph graph of the model species interactions

        Returns
        -------
        nx.Digraph 
            Graph that has the information for the visualization of the model
        """
        generate_equations(self.model)
        sp_graph = nx.DiGraph(name=self.model.name, graph={'rankdir': 'LR'}, paths=[])

        # TODO: there are reactions that generate parallel edges that are not taken into account because netowrkx
        # digraph only allows one edge between two nodes
        for idx, sp in enumerate(self.model.species):
            species_node = 's%d' % idx
            color = "#2b913a"
            # color species with an initial condition differently
            if len([s.pattern for s in self.model.initials if s.pattern.is_equivalent_to(sp)]):
                color = "#aaffff"
            # Setting the information about the node
            node_data = dict(label=hf.parse_name(sp),
                             background_color=color,
                             shape='ellipse',
                             NodeType='species',
                             spInitial=self._sp_initial(sp))
            sp_graph.add_node(species_node, **node_data)

        for reaction in self.model.reactions_bidirectional:
            reactants = set(reaction['reactants'])
            products = set(reaction['products'])
            if reaction['reversible']:
                attr_reversible = {'source_arrow_shape': 'diamond', 'target_arrow_shape': 'triangle',
                                   'source_arrow_fill': 'hollow'}
            else:
                attr_reversible = {'source_arrow_shape': 'none', 'target_arrow_shape': 'triangle',
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
        nx.Digraph 
            Graph that has the information for the visualization of the model
        """
        generate_equations(self.model)
        graph = nx.DiGraph(name=self.model.name, graph={'rankdir': 'LR'})
        for i, cp in enumerate(self.model.species):
            species_node = 's%d' % i
            slabel = hf.parse_name(cp)
            color = "#2b913a"
            # color species with an initial condition differently
            if len([s.pattern for s in self.model.initials if s.pattern.is_equivalent_to(cp)]):
                color = "#aaffff"
            graph.add_node(species_node,
                           label=slabel,
                           shape="ellipse",
                           background_color=color,
                           NodeType='species',
                           spInitial=self._sp_initial(cp),
                           bipartite=0)
        for j, reaction in enumerate(self.model.reactions_bidirectional):
            reaction_node = 'r%d' % j
            rule = self.model.rules.get(reaction['rule'][0])
            graph.add_node(reaction_node,
                           label=reaction_node,
                           shape="roundrectangle",
                           background_color="#d3d3d3",
                           NodeType='reaction',
                           kf=rule.rate_forward.value,
                           kr=rule.rate_reverse.value if rule.rate_reverse else 'None',
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
                attr_modifiers = {'target_arrow_shape': 'diamond'}
                self._r_link_bipartite(graph, s, j, **attr_modifiers)
        return graph

    def sp_rxns_graph(self):
        """
        Creates a bipartite nx.DiGraph graph where one set of nodes is the model species
        and the other set is the model unidirectional reactions.

        Returns
        -------
        nx.Digraph 
            Graph that has the information for the visualization of the model
        """
        generate_equations(self.model)
        graph = nx.DiGraph(name=self.model.name, graph={'rankdir': 'LR'})
        for i, cp in enumerate(self.model.species):
            species_node = 's%d' % i
            slabel = hf.parse_name(self.model.species[i])
            color = "#2b913a"
            # color species with an initial condition differently
            if len([s.pattern for s in self.model.initials if s.pattern.is_equivalent_to(cp)]):
                color = "#aaffff"
            graph.add_node(species_node,
                           label=slabel,
                           shape="ellipse",
                           background_color=color,
                           NodeType='species',
                           spInitial=self._sp_initial(cp),
                           bipartite=0)
        for i, reaction in enumerate(self.model.reactions):
            reaction_node = 'r%d' % i
            rule = self.model.rules.get(reaction['rule'][0])
            graph.add_node(reaction_node,
                           label=reaction_node,
                           shape="roundrectangle",
                           background_color="#d3d3d3",
                           NodeType='reaction',
                           kf=rule.rate_forward.value if not reaction['reverse'][0] else 'None',
                           kr=rule.rate_reverse.value if reaction['reverse'][0] else 'None',
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

    def sbgn_graph(self):
        import re
        from pysb.pattern import Pattern, Name
        from pysb import Rule, Parameter
        graph = nx.DiGraph(name=self.model.name, style='sbgn')
        all_cp = []
        cp_to_delete = []
        rules_for_nodes = []
        # Obtain complex patterns from rules, save the complexes formed during catalysis to remove them
        # as they don't appear in the SBGN standard, and save the rules that are not related to catalysis
        for r in self.model.rules:
            if re.match('catalyze_.+_to_.+_.+', r.name):
                cp_to_delete.append(r.reactant_pattern.complex_patterns[0])
                all_cp.append([r.product_pattern.complex_patterns[1]])
            elif re.match('bind_.+_.+_to_.+', r.name): # and r._function == 'catalyze':
                all_cp.append(r.reactant_pattern.complex_patterns)
                all_cp.append(r.product_pattern.complex_patterns)
            else:
                all_cp.append(r.reactant_pattern.complex_patterns)
                all_cp.append(r.product_pattern.complex_patterns)
                rules_for_nodes.append(r)
        # For each complex that is formed during the catalysis, we obtain the bind and catalyze rules to generate
        # the new rules that would give us the SBGN standard visualization
        for cpd in cp_to_delete:
            bind_cat = self.model.rules.filter(Pattern(cpd))
            bind = bind_cat.filter(Name('^bind'))
            cat = bind_cat.filter(Name('^catalyze'))
            par_aux = Parameter('bla', 1, _export=False)
            rule_aux1 = Rule('production_cat_1', bind[0].reactant_pattern.complex_patterns[1] >>
                             cat[0].product_pattern.complex_patterns[1], par_aux, _export=False)
            rule_aux2 = Rule('catalysis_cat_2', bind[0].reactant_pattern.complex_patterns[0] >>
                             None, par_aux, _export=False)
            rule_aux = {'production_cat_1': rule_aux1, 'catalysis_cat_2': rule_aux2}
            rules_for_nodes.append(rule_aux)
        # obtain unique complex patterns to add to the network
        all_cp = [item for sublist in all_cp for item in sublist]
        unique_cp = []
        for i in all_cp:
            if not in_cp_list(i, unique_cp) and not in_cp_list(i, cp_to_delete):
                unique_cp.append(i)
        cp_encode = [(unique_cp[idx], idx) for idx in range(len(unique_cp))]

        for cp, cp_idx in cp_encode:
            cp_node = 's{0}'.format(cp_idx)
            slabel = hf.parse_name(cp)
            cp_length = len(cp.monomer_patterns)
            if cp_length == 1:
                cp_class = 'macromolecule'
                mp_node = 'mp1_{0}'.format(cp_node)
                mp = cp.monomer_patterns[0]
                state_variables = []
                for s, v in mp.site_conditions.items():
                    if isinstance(v, str):
                        state = {'variable': s, 'value': v}
                        state_variables.append({'id': mp_node, 'class': 'state variable', 'state': state})
                node_data = {'label': mp.monomer.name, 'class': cp_class,
                             'NodeType': 'macromolecule', 'stateVariables': state_variables, "unitsOfInformation": []}
                graph.add_node(cp_node, **node_data)

            elif cp_length == 2:
                cp_class = 'complex'
                node_data = {'label': slabel, 'class': cp_class, 'stateVariables': [],
                             'NodeType': 'complex', "unitsOfInformation": []}
                graph.add_node(cp_node, **node_data)
                for idx, mp in enumerate(cp.monomer_patterns):
                    mp_node = 'mp2_{0}_{1}'.format(cp_node, idx)
                    state_variables = []
                    for s, v in mp.site_conditions.items():
                        if isinstance(v, str):
                            state = {'variable': s, 'value': v}
                            state_variables.append({'id': mp_node, 'class': 'state variable', 'state': state})
                    node_data_mp = {'label': mp.monomer.name, 'stateVariables': state_variables,
                                    'class': 'macromolecule', 'unitsOfInformation': [], 'parent': cp_node}
                    graph.add_node(mp_node, **node_data_mp)

            elif cp_length >= 3:
                cp_class = 'macromolecule multimer'

        for r_idx, rule in enumerate(rules_for_nodes):
            rule_node = 'r%d' % r_idx
            node_data = {'label': rule_node, 'class': 'process', 'NodeType': 'process'}
            graph.add_node(rule_node, **node_data)
            if isinstance(rule, dict):
                for rname, rcat in rule.items():
                    if rname.startswith('catalysis_cat'):
                        sbgn_class = 'catalysis'
                    elif rcat.is_reversible:
                        sbgn_class = 'production'
                    else:
                        sbgn_class = 'consumption'
                    reactants = rcat.reactant_pattern.complex_patterns
                    products = rcat.product_pattern.complex_patterns

                    for s in reactants:
                        reactant_node = get_cp_idx(s, cp_encode)
                        attr_edges = {'class': sbgn_class, "cardinality": 0,
                                      "portSource": "s{0}".format(reactant_node), "portTarget": rule_node}
                        self._r_link_bipartite(graph, reactant_node, r_idx, **attr_edges)
                    for s in products:
                        p_node = get_cp_idx(s, cp_encode)
                        attr_edges = {'class': 'production', "cardinality": 0,
                                      "portSource": rule_node, "portTarget": "s{0}".format(p_node)}
                        self._r_link_bipartite(graph, p_node, r_idx, _flip=True, **attr_edges)

            else:
                reactants = rule.reactant_pattern.complex_patterns
                products = rule.product_pattern.complex_patterns
                for s in reactants:
                    reactant_node = get_cp_idx(s, cp_encode)
                    attr_edges = {'class': 'consumption', "cardinality": 0,
                                  "portSource": "s{0}".format(reactant_node), "portTarget": rule_node}
                    self._r_link_bipartite(graph, reactant_node, r_idx, **attr_edges)
                for s in products:
                    p_node = get_cp_idx(s, cp_encode)
                    attr_edges = {'class': 'production', "cardinality": 0,
                                  "portSource": rule_node, "portTarget": "s{0}".format(p_node)}
                    self._r_link_bipartite(graph, p_node, r_idx, _flip=True, **attr_edges)
        return graph

    def rules_graph(self):
        """
        Creates a bipartite nx.DiGraph graph where one set of nodes is the model species
        and the other set is the model rules.

        Returns
        -------
        nx.Digraph
            Graph that has the information for the visualization of the model
        """
        graph = self.sp_rxns_graph()
        # Merge reactions into the rules that they come from
        nodes2merge = self.merge_reactions2rules()
        node_attrs = {'shape': 'roundrectangle', 'background_color': '#ff4c4c',
                      'NodeType': 'rule', 'bipartite': 1}
        for rule_info, rxns in nodes2merge.items():
            rule = self.model.rules.get(rule_info[0])
            node_attrs['kf'] = rule.rate_forward.value
            node_attrs['kr'] = rule.rate_reverse.value if rule.rate_reverse else 'None'
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
            One of the following options `species_reactions`, `species_rules`,
            `reactions`, `rules`

        Returns
        -------
        nx.DiGraph
            Projected graph
        """
        if project_to == 'species_reactions' or project_to == 'species_rules':
            nodes = {n for n, d in graph.nodes(data=True) if d['bipartite'] == 0}
        elif project_to == 'reactions' or project_to == 'rules':
            nodes = {n for n, d in graph.nodes(data=True) if d['bipartite'] == 1}
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
        nx.Digraph 
            Graph that has the information for the visualization of the model
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
        dict
            Dictionary whose keys are tuples of rule name and rule index and the values
            are the reactions that are generated by each rule
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
        # attrs.setdefault('arrowhead', 'normal')
        graph.add_edge(*nodes, **attrs)


def graph_to_json(sp_graph, layout=None, path=''):
    """
    Convert networkx graph to a dictionary that can be converted
    to cytoscape.js json
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
    dict
        A Dictionary Object that can be converted into Cytoscape.js JSON
    """
    data = from_networkx(sp_graph, layout=layout, scale=1)
    if path:
        with open(path + 'data.json', 'w') as outfile:
            json.dump(data, outfile)
    return data


def in_cp_list(cp, cp_list):
    if [s for s in cp_list if s.is_equivalent_to(cp)]:
        return True
    else:
        return False


def get_cp_idx(cp, cp_list):
    idx = None
    for c, c_idx in cp_list:
        if c.is_equivalent_to(cp):
            idx = c_idx
            break
    return idx

