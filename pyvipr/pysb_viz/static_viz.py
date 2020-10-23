import networkx as nx
from pyvipr.util_networkx import from_networkx, map_edge_data_rn_gml, map_node_data_gml, map_edge_data_contactmap_gml
import pysb
from pysb.bng import generate_equations
from pysb.pattern import match_complex_pattern
from networkx.algorithms import bipartite
import re
import pyvipr.util as hf
from pysb.bng import BngFileInterface
from pysb.logging import EXTENDED_DEBUG
from pysb.tools.render_reactions import sp_from_expression


class PysbStaticViz(object):
    """
    Class to generate static visualizations of systems biology models

    Parameters
    ----------
    model : pysb.Model
        PySB Model to visualize.
    generate_eqs : bool
        If True, generate math expressions for reaction rates and species in a model
    """

    def __init__(self, model, generate_eqs=True):
        # Need to create a model visualization base and then do independent visualizations: static and dynamic
        self.model = model
        if generate_eqs:
            generate_equations(self.model)

    def sp_view(self):
        """
        Generate a dictionary that contains the species network information

        Parameters
        ----------

        Examples
        --------
        >>> from pysb.examples.earm_1_0 import model
        >>> viz = PysbStaticViz(model)
        >>> data = viz.sp_view()

        Returns
        -------
        dict
            A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
            contains all the information (nodes,edges, positions) to generate a cytoscapejs network.
        """
        graph = self.species_graph()
        data = from_networkx(graph)
        return data

    def highlight_nodes_view(self, species=None, reactions=None):
        """
        Highlights the species and/or reactions passed as arguments

        Parameters
        ----------
        species: list-like
            It can be a vector with the indices of the species to be highlighted,
            or a vector with the concrete pysb.ComplexPattern species to be highlighted
        reactions: list-like
            A vector of tuples of length 2, where the first entry is the edge source
            and the second entry is the edge target, entries can be species indices or
            complex patterns. Or it can be a vector of integers that represent the
            indices of the reactions to highlight.

        Returns
        -------
        dict
            A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
            contains all the information (nodes,edges, positions) to generate a cytoscapejs network.
        """
        graph = self.species_graph()
        if species is not None:
            if all(isinstance(x, int) for x in species):
                sp_new_shape = {'s{0}'.format(sp): {'border_width': 4, 'border_color': '#D81B60',
                                                    'highlight_nodes': 'yes'} for sp in species}
            elif all(isinstance(x, pysb.ComplexPattern) for x in species):
                sp_new_shape = {'s{0}'.format(self.model.species.index(sp)):
                                    {'border_width': 4, 'border_color': '#D81B60',
                                     'highlight_nodes': 'yes'} for sp in species}
            else:
                raise ValueError
            nx.set_node_attributes(graph, sp_new_shape)
        if reactions is not None:
            if all(isinstance(x, int) for x in reactions):
                edge_new_style = {}
                for rxn in reactions:
                    reaction = self.model.reactions_bidirectional[rxn]
                    reactants = set(reaction['reactants'])
                    products = set(reaction['products'])
                    for s in reactants:
                        for p in products:
                            edge_new_style[('s{0}'.format(s), 's{0}'.format(p))] = {'line_color': '#D81B60',
                                                                                    'highlight_edges': 'yes'}
            elif all(isinstance(x, tuple) for x in reactions):
                edge_new_style = {self._process_incoming_edge(rxn):
                                      {'line_color': '#D81B60', 'highlight_edges': 'yes'} for rxn in reactions}
            else:
                raise ValueError
            nx.set_edge_attributes(graph, edge_new_style)
        data = from_networkx(graph)
        return data

    def _process_incoming_edge(self, edge):
        """
        Takes a tuple (s, t) edge and convert it into the edges used in
        the cytoscape visualization
        Parameters
        ----------
        edge: tuple
            Edge tuple

        Returns
        -------
        tuple
            A formatted tuple that matches edges used in cytoscape.js
        """
        source = edge[0]
        target = edge[1]
        if isinstance(source, int):
            source = 's{0}'.format(source)
        elif isinstance(source, pysb.ComplexPattern):
            source = 's{0}'.format(self.model.species.index(source))
        if isinstance(target, int):
            target = 's{0}'.format(target)
        elif isinstance(target, pysb.ComplexPattern):
            target = 's{0}'.format(self.model.species.index(target))
        return source, target

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
        data = from_networkx(graph)
        return data

    def sp_comm_louvain_view(self, random_state=None):
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
        graph = self.species_graph()
        hf.add_louvain_communities(graph, all_levels=False, random_state=random_state)
        data = from_networkx(graph)
        return data

    def sp_comm_louvain_hierarchy_view(self, random_state=None):
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
        graph = self.species_graph()
        hf.add_louvain_communities(graph, all_levels=True, random_state=random_state)
        data = from_networkx(graph)
        return data

    def sp_comm_greedy_view(self):
        graph = self.species_graph()
        hf.add_greedy_modularity_communities(graph)
        data = from_networkx(graph)
        return data

    def sp_comm_asyn_lpa_view(self, random_state=None):
        graph = self.species_graph()
        hf.add_asyn_lpa_communities(graph, seed=random_state)
        data = from_networkx(graph)
        return data

    def sp_comm_label_propagation_view(self):
        graph = self.species_graph()
        hf.add_label_propagation_communities(graph)
        data = from_networkx(graph)
        return data

    def sp_comm_girvan_newman_view(self):
        graph = self.species_graph()
        hf.add_girvan_newman(graph)
        data = from_networkx(graph)
        return data

    def sp_comm_asyn_fluidc_view(self, k, max_iter=100, seed=None):
        graph = self.species_graph()
        hf.add_asyn_fluidc(graph, k, max_iter, seed)
        data = from_networkx(graph)
        return data

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
        graph = self.sp_rxns_bidirectional_graph(two_edges=False)
        data = from_networkx(graph)
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
        data = from_networkx(graph)
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
        rules_graph = self.sp_rules_graph()
        data = from_networkx(rules_graph)
        return data

    def sp_rules_fxns_view(self):
        """
        Generates a dictionary with the info of a bipartite graph where one set of nodes is the model species
        and the other set is the model rules. Additionally, it clusters rules into the functions used to
        create the rules.

        Returns
        -------
        dict
            A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
            contains all the information (nodes,edges, parent nodes, positions) to generate
            a cytoscapejs network.
        """
        graph = self.sp_rules_graph()
        self._add_rules_functions(graph)
        data = from_networkx(graph)
        return data

    def rules_fxns_view(self):
        """
        Generates a dictionary with the info of a unipartite rules graph. Additionally, it clusters rules
        into the functions used to create them

        Returns
        -------
        dict
            A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
            contains all the information (nodes,edges, parent nodes, positions) to generate
            a cytoscapejs network.
        """
        sp_rules_graph = self.sp_rules_graph()
        rules_graph = self.projected_graph(sp_rules_graph, 'rules')
        self._add_rules_functions(rules_graph)
        data = from_networkx(rules_graph)
        return data

    def _add_rules_functions(self, rules_graph):
        """
        Obtains functions where rules are declared and add them as nodes to the graph. It also, set nodes attributes
        to relate rules with their corresponding function.

        Parameters
        ----------
        rules_graph : nx.DiGraph
            A graph that contains rules nodes

        Returns
        -------

        """
        rule_functions = {rule.name: rule._function for rule in self.model.rules}
        unique_functions = set(rule_functions.values())
        nx.set_node_attributes(rules_graph, rule_functions, 'parent')
        rules_graph.add_nodes_from(unique_functions, NodeType='function')

    def sp_rules_mod_view(self):
        """
        Generates a dictionary with the info of a bipartite graph where one set of nodes is the model species
        and the other set is the model rules. Additionally, it clusters rules into the modules used to create them

        Returns
        -------
        dict
            A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
            contains all the information (nodes,edges, parent nodes, positions) to generate
            a cytoscapejs network.
        """
        rules_graph = self.sp_rules_graph()
        self._add_rules_modules(rules_graph)
        data = from_networkx(rules_graph)
        return data

    def rules_mod_view(self):
        """
        Generates a dictionary with the info of a unipartite rules graph. Additionally, it clusters rules
        into the modules used to create them

        Returns
        -------
        dict
            A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
            contains all the information (nodes,edges, parent nodes, positions) to generate
            a cytoscapejs network.
        """
        sp_rules_graph = self.sp_rules_graph()
        rules_graph = self.projected_graph(sp_rules_graph, 'rules')
        self._add_rules_modules(rules_graph)
        data = from_networkx(rules_graph)
        return data

    def _add_rules_modules(self, rules_graph):
        """
        Obtains modules where rules are declared and add them as node to the graph. It also, set nodes attributes
        to relate rules with their corresponding module.

        Parameters
        ----------
        rules_graph : nx.DiGraph
            A graph that contains rules nodes

        Returns
        -------

        """
        # Unique modules used in the model
        unique_modules = [m for m in self.model.modules if not m.startswith('_')]
        # Remove outer model file to not look further modules that are not related to
        # the model
        unique_modules.remove(self.model.name)
        # Remove macros as we are only interested in the modules
        if 'pysb.macros' in unique_modules:
            unique_modules.remove('pysb.macros')
        module_parents = {}
        # pysb components have a modules list that starts from the inner frame
        # to the outer frame.
        # Get module parents to add to the graph. If a child module node has two
        # parent nodes, we have to create a new child node, because cytoscape doesn't
        # support overlapped compound nodes
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
            rule_modules = list(dict.fromkeys(rule._modules))
            mod_initial_idx = 0
            if rule_modules[mod_initial_idx] != 'pysb.macros':
                m = rule_modules[mod_initial_idx]
            else:
                mod_initial_idx = 1
                m = rule_modules[mod_initial_idx]
            if m not in module_parents.keys():
                m_parent = rule_modules[mod_initial_idx + 1]
                m_parent_child = list(module_parents.keys())[list(module_parents.values()).index(m_parent)]
                rules_module[rule.name] = m_parent_child
            else:
                rules_module[rule.name] = m

        module_parent_nodes = list(module_parents.keys())
        module_parent_nodes.append(self.model.name)
        rules_graph.add_nodes_from(module_parent_nodes, NodeType='module')
        nx.set_node_attributes(rules_graph, module_parents, 'parent')
        nx.set_node_attributes(rules_graph, rules_module, 'parent')

    def atom_rules_view(self, visualize_args, rule_name=None, verbose=False, cleanup=True):
        """
        Uses the BioNetGen atom-rules to visualize large rule-base models. For more
        information regarding atom-rules and its parameters please visit:
        Sekar et al (2017), Automated visualization of rule-based models
        https://doi.org/10.1371/journal.pcbi.1005857

        The visualize_args parameter contains all the arguments that will be passed to the
        BioNetGen visualize function. It is a dictionary and supports the following
        key, value pairs.

          - `type`

            * `conventional` => Conventional rule visualization
            * `compact` => Compact rule visualization (using graph operation nodes)
            * `regulatory` => Rule-derived regulatory graph
            * `contactmap` => Contact map
            * `reaction_network` => Reaction network
          -  `suffix`

            * str => add suffix string to output filename
          - `each`

            * 1 => Show all rules in separate GML files
            * 0 => Show all rules  the same GML file.
          - `opts`

            * file path => import options from file. Options template for regulatory graph
          - `background`

            * 1 => Enable background
            * 0 => Disable background
          - `groups`

            * 1 => Enable groups
            * 0 => Disable groups
          - `collapse`

            * 1 => Enable collapsing of groups
            * 0 => Disable collapsing of groups
          - `ruleNames`

            * 1 => Enable display of rule names
            * 0 => Disable display of rule names
          - `doNotUseContextWhenGrouping`

            * 1 => Use permissive edge signature
            * 0 => Use strict edge signature
          - `doNotCollapseEdges`:

            * 1 => When collapsing nodes, retain duplicate edges
            * 0 => When collapsing nodes, remove duplicate edges

        Parameters
        ----------
        visualize_args: dict
            Contains all the arguments that will be passed to the BioNetGen visualize function.
            The following key, value pairs are available
        rule_name : str
           Name of the rule to visualize, when `each` is set to 1 in visualize_args.
        cleanup : bool, optional
            If True (default), delete the temporary files after the simulation is
            finished. If False, leave them in place. Useful for debugging.
        verbose : bool or int, optional (default: False)
            Sets the verbosity level of the logger. See the logging levels and
            constants from Python's logging module for interpretation of integer
            values. False is equal to the PySB default level (currently WARNING),
            True is equal to DEBUG.

        Returns
        -------

        """
        # TODO: Check that all visualize_args work
        bng_action_debug = verbose if isinstance(verbose, bool) else \
            verbose <= EXTENDED_DEBUG

        visualize_args['verbose'] = visualize_args.get('verbose',
                                                       bng_action_debug)

        file_name = '_{0}'.format(visualize_args['type'])
        if rule_name:
            file_name += '_{0}'.format(rule_name)
        if 'suffix' in visualize_args.keys():
            file_name += '_{0}'.format(visualize_args['suffix'])
        file_name += '.gml'

        with BngFileInterface(self.model, verbose=verbose, cleanup=cleanup) as bngfile:
            bngfile.action('visualize', **visualize_args)
            bngfile.execute()
            output = bngfile.base_filename + file_name
            try:
                g = nx.read_gml(output, label='id')
            except nx.exception.NetworkXError as e:
                if 'duplicated' in str(e):
                    with open(output, "r") as f:
                        contents = f.readlines()
                    contents[1] = '[multigraph 1\n'
                    with open(output, "w") as f:
                        f.writelines(contents)
                    g = nx.read_gml(output, label='id')

        g.graph['name'] = self.model.name
        g.graph['style'] = 'atom'
        if visualize_args['type'] == 'contactmap':
            data = from_networkx(g, map_node_data=map_node_data_gml, map_edge_data=map_edge_data_contactmap_gml)
        else:
            data = from_networkx(g, map_node_data=map_node_data_gml, map_edge_data=map_edge_data_rn_gml)
        return data

    def sbgn_view(self):
        sbgn_graph = self.sbgn_graph()
        data = from_networkx(sbgn_graph)
        return data

    def cluster_rxns_by_rules_view(self):
        """
        Cluster reaction nodes into the rules that generated them

        Returns
        -------
        dict
            A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
            contains all the information (nodes,edges, parent nodes, positions) to generate
            a cytoscapejs network.
        """
        bigraph = self.sp_rxns_bidirectional_graph(two_edges=True)
        rxns_graph = self.projected_graph(bigraph, 'bireactions')
        rxns_rule = {'r{0}'.format(i): j['rule'][0] for i, j in enumerate(self.model.reactions_bidirectional)}
        cnodes = set(rxns_rule.values())
        rxns_graph.add_nodes_from(cnodes, NodeType='rule')
        nx.set_node_attributes(rxns_graph, rxns_rule, 'parent')
        data = from_networkx(rxns_graph)
        return data

    def _projections_view(self, project_to):
        """
        Project a bipartite graph to the type of node defined in `project to`.
        Generates a dictionary with the info of a graph representing the PySB model.

        Parameters
        ----------
        project_to: str
            Type of nodes to which the graph is going to be projected. Options are:
            'species_from_bireactions' to project to a species graph from a  species & bidirectional
            reactions graph, 'bireactions' to project to a reactions graph from a species &
            bidirectional reaction graph,

        Returns
        -------
        dict
            A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
            contains all the information (nodes,edges, parent nodes, positions) to generate
            a cytoscapejs network.
        """
        if project_to in ['species_from_bireactions', 'bireactions']:
            bipartite_graph = self.sp_rxns_bidirectional_graph(two_edges=True)
            reactions = self.model.reactions_bidirectional
        else:
            raise ValueError('Projection not valid')

        projected_graph = self.projected_graph(bipartite_graph, project_to, reactions)
        data = from_networkx(projected_graph)
        return data

    def projected_species_from_bireactions_view(self):
        """
        This is a projection from the species & bidirectioanl reactions
        bipartite graph
        Returns
        -------

        """
        return self._projections_view('species_from_bireactions')

    def projected_bireactions_view(self):
        return self._projections_view('bireactions')

    def projected_rules_view(self):
        graph = self.sp_rxns_bidirectional_graph(two_edges=True)
        rxn_graph = self.projected_graph(graph, 'bireactions', self.model.reactions_bidirectional)
        self.merge_reactions2rules(rxn_graph)
        data = from_networkx(rxn_graph)

        return data

    def projected_species_from_rules_view(self):
        return self.projected_species_from_bireactions_view()

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
        # Check if model has compartments
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
            monomers_comp = {m.compartment.name: m.compartment.dimension for m in monomers}
            smallest_comp = min(monomers_comp, key=monomers_comp.get)
            sp_compartment['s{0}'.format(idx)] = smallest_comp
        nx.set_node_attributes(graph, sp_compartment, 'parent')
        return graph

    def species_graph(self):
        """
        Creates a nx.DiGraph graph of the model species interactions

        Returns
        -------
        nx.Digraph 
            Graph that has the information for the visualization of the model
        """
        sp_graph = nx.DiGraph(name=self.model.name)

        # TODO: there are reactions that generate parallel edges that are not taken into account because netowrkx
        # digraph only allows one edge between two nodes
        for idx, sp in enumerate(self.model.species):
            species_node = 's%d' % idx
            color = "#2b913a"
            # color species with an initial condition differently
            sp_initial = self._sp_initial(sp)
            if sp_initial != 0:
                color = "#aaffff"
            # Setting the information about the node
            node_data = dict(label=parse_name(sp),
                             background_color=color,
                             shape='ellipse',
                             NodeType='species',
                             spInitial=sp_initial)
            sp_graph.add_node(species_node, **node_data)

        for reaction in self.model.reactions_bidirectional:
            reactants = set(reaction['reactants'])
            products = set(reaction['products'])
            if reaction['reversible']:
                attr_reversible = {'source_arrow_shape': 'triangle', 'target_arrow_shape': 'triangle',
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

    def sp_rxns_bidirectional_graph(self, two_edges=False):
        """
        Creates a bipartite nx.DiGraph graph where one set of nodes is the model species
        and the other set is the model bidirectional reactions.

        Parameters
        ----------
        two_edges : bool
            If true, it draws two edges (in opposite directions) for each reversible reaction

        Returns
        -------
        nx.Digraph 
            Graph that has the information for the visualization of the model
        """
        graph = nx.DiGraph(name=self.model.name, graph={'rankdir': 'LR'})
        for i, cp in enumerate(self.model.species):
            species_node = 's%d' % i
            slabel = parse_name(cp)
            color = "#2b913a"
            # color species with an initial condition differently
            sp_initial = self._sp_initial(cp)
            if sp_initial != 0:
                color = "#aaffff"
            graph.add_node(species_node,
                           label=slabel,
                           shape="ellipse",
                           background_color=color,
                           NodeType='species',
                           spInitial=sp_initial,
                           bipartite=0)

        # Attributes for edges of reactions with expressions and modifiers
        attr_modifiers = {'source_arrow_shape': 'diamond', 'target_arrow_shape': 'diamond',
                          'source_arrow_fill': 'filled'}
        attr_expr = {'source_arrow_shape': 'none', 'target_arrow_shape': 'square',
                     'source_arrow_fill': 'filled'}
        for j, reaction in enumerate(self.model.reactions_bidirectional):
            reaction_node = 'r%d' % j
            rule = self.model.rules.get(reaction['rule'][0])
            graph.add_node(reaction_node,
                           label=reaction_node,
                           shape="roundrectangle",
                           background_color="#d3d3d3",
                           NodeType='reaction',
                           kf=str(rule.rate_forward.get_value()) if isinstance(rule.rate_forward,
                                                                               (pysb.Parameter, pysb.Expression)) else 'None',
                           kr=str(rule.rate_reverse.get_value()) if isinstance(rule.rate_reverse,
                                                                               (pysb.Parameter, pysb.Expression)) else 'None',
                           bipartite=1)
            reactants = set(reaction['reactants'])
            products = set(reaction['products'])
            modifiers = reactants & products
            reactants = reactants - modifiers
            products = products - modifiers

            sps_forward = set()
            if isinstance(rule.rate_forward, pysb.Expression):
                sps_forward = sp_from_expression(rule.rate_forward)
                for s in sps_forward:
                    self._r_link_bipartite(graph, s, j, **attr_expr)

            if isinstance(rule.rate_reverse, pysb.Expression):
                sps_reverse = sp_from_expression(rule.rate_reverse)
                sps_reverse = set(sps_reverse) - set(sps_forward)
                for s in sps_reverse:
                    self._r_link_bipartite(graph, s, j, **attr_expr)

            attr_edge = {'source_arrow_shape': 'none', 'target_arrow_shape': 'triangle',
                         'source_arrow_fill': 'filled'}
            if reaction['reversible'] and two_edges:
                link = self._r_link_twice
            elif reaction['reversible'] and not two_edges:
                attr_edge = {'source_arrow_shape': 'triangle', 'target_arrow_shape': 'triangle',
                             'source_arrow_fill': 'hollow'}
                link = self._r_link_bipartite
            else:
                link = self._r_link_bipartite

            for s in reactants:
                link(graph, s, j, **attr_edge)
            for s in products:
                # self._r_link_bipartite(graph, s, j, _flip=True, **attr_edge)
                link(graph, s, j, _flip=True, **attr_edge)
            for s in modifiers:
                # self._r_link_bipartite(graph, s, j, **attr_modifiers)
                link(graph, s, j, **attr_modifiers)
        return graph

    @staticmethod
    def _r_link_twice(graph, s, r, **attrs):
        """
        Creates two links (in opposite directions) between the nodes passed as arguments
        Parameters
        ----------
        graph
        s
        r
        attrs

        Returns
        -------

        """
        nodes = ('s{0}'.format(s), 'r{0}'.format(r))
        nodes_rev = ('r{0}'.format(r), ('s{0}'.format(s)))
        if attrs.get('_flip'):
            del attrs['_flip']
        # attrs.setdefault('arrowhead', 'normal')
        graph.add_edges_from([nodes, nodes_rev], **attrs)

    def sp_rxns_graph(self):
        """
        Creates a bipartite nx.DiGraph graph where one set of nodes is the model species
        and the other set is the model unidirectional reactions.

        Returns
        -------
        nx.Digraph 
            Graph that has the information for the visualization of the model
        """
        graph = nx.DiGraph(name=self.model.name, graph={'rankdir': 'LR'})
        for i, cp in enumerate(self.model.species):
            species_node = 's%d' % i
            slabel = parse_name(self.model.species[i])
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
                           kf=str(rule.rate_forward.get_value()) if not reaction['reverse'][0] else 'None',
                           kr=str(rule.rate_reverse.get_value()) if reaction['reverse'][0] else 'None',
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
            elif re.match('bind_.+_.+_to_.+', r.name) and r._function == 'catalyze':
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
            slabel = parse_name(cp)
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
                node_data = {'label': slabel, 'class': cp_class, 'stateVariables': [],
                             'NodeType': 'complex', "unitsOfInformation": []}
                graph.add_node(cp_node, **node_data)
                for idx, mp in enumerate(cp.monomer_patterns):
                    mp_node = 'mp{0}_{1}_{2}'.format(cp_length, cp_node, idx)
                    state_variables = []
                    for s, v in mp.site_conditions.items():
                        if isinstance(v, str):
                            state = {'variable': s, 'value': v}
                            state_variables.append({'id': mp_node, 'class': 'state variable', 'state': state})
                    node_data_mp = {'label': mp.monomer.name, 'stateVariables': state_variables,
                                    'class': 'macromolecule', 'unitsOfInformation': [], 'parent': cp_node}
                    graph.add_node(mp_node, **node_data_mp)

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

    def sp_rules_graph(self):
        """
        Creates a bipartite nx.DiGraph graph where one set of nodes is the model species
        and the other set is the model rules.

        Returns
        -------
        nx.Digraph
            Graph that has the information for the visualization of the model
        """
        graph = self.sp_rxns_bidirectional_graph()
        # Merge reactions into the rules that they come from
        self.merge_reactions2rules(graph)

        return graph

    def projected_graph(self, graph, project_to, reactions=None):
        """
        Project a bipartite graph into one of the sets of nodes

        Parameters
        ----------
        graph: nx.DiGraph
            a networkx bipartite graph
        project_to: str
            One of the following options `species_from_bireactions`,
            `species_from_rules`, `bireactions`, `rules`
        reactions: pysb.ComponentSet
            Model reactions

        Returns
        -------
        nx.DiGraph
            Projected graph
        """
        if project_to in ['species_from_bireactions', 'species_from_rules']:
            # Use dictionary with Values set to None to obtain and ordered set of nodes
            nodes = {n: None for n, d in graph.nodes(data=True) if d['bipartite'] == 0}
            from pyvipr.bipartite_projection import species_projected_graph as bipartite_projected_graph
            graph_projected = bipartite_projected_graph(graph, reactions, nodes.keys())
        elif project_to in ['bireactions', 'rules']:
            nodes = {n: None for n, d in graph.nodes(data=True) if d['bipartite'] == 1}
            graph_projected = bipartite.projected_graph(graph, nodes.keys())
        else:
            raise ValueError('Projection not valid')

        self.graph_merge_pair_edges(graph_projected, reactions=reactions)

        return graph_projected

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
                if isinstance(spInitial.value, pysb.Parameter):
                    sp_0 = spInitial.value.get_value()
                else:
                    sp_0 = float(spInitial.value.get_value())
                break
        return sp_0

    @staticmethod
    def graph_merge_pair_edges(graph, reactions=None):
        """
        Merges pair of edges that are reversed
        
        Parameters
        ----------
        graph: nx.DiGraph or nx.MultiDiGraph
            The networkx directed graph whose pairs of edges ((u, v), (v, u)) are going to be merged
        reactions: pysb.ComponentSet
            Model reactions
        
        Returns
        -------
        nx.Digraph 
            Graph that has the information for the visualization of the model
        """
        edges_to_delete = []
        edges_attributes = {}

        if graph.is_multigraph():
            graph_edges = graph.edges(keys=True)

            def reverse_edge(e):
                return e[1], e[0], e[2]

            def edge_reversible_attr(e):
                rxn_idx = int(e[2][1:])
                reaction = reactions[rxn_idx]
                reactants = set(reaction['reactants'])
                if int(e[0][1:]) in reactants:
                    # print(edge, rxn)
                    attr_reversible = {'source_arrow_shape': 'triangle', 'target_arrow_shape': 'triangle',
                                       'source_arrow_fill': 'hollow'}
                else:
                    attr_reversible = {'source_arrow_shape': 'triangle', 'target_arrow_shape': 'triangle',
                                       'source_arrow_fill': 'filled', 'target_arrow_fill': 'hollow'}
                return attr_reversible
        else:
            graph_edges = graph.edges()

            def reverse_edge(e):
                return e[::-1]

            def edge_reversible_attr(e):
                attr_reversible = {'source_arrow_shape': 'triangle', 'target_arrow_shape': 'triangle',
                                   'source_arrow_fill': 'filled'}
                return attr_reversible
        for edge in graph_edges:
            if edge in edges_to_delete:
                continue
            r_edge = reverse_edge(edge)
            if graph.has_edge(*r_edge):
                edges_attributes[edge] = edge_reversible_attr(edge)
                edges_to_delete.append(r_edge)
            else:
                attr_irreversible = {'source_arrow_shape': 'none', 'target_arrow_shape': 'triangle',
                                     'source_arrow_fill': 'filled'}
                edges_attributes[edge] = attr_irreversible

        # Remove duplicated bidirectional edges between nodes
        marker_set = set()
        if graph.is_multigraph():
            dup_edges_to_delete = []
            for dup_edge in edges_to_delete:
                rxn = (dup_edge[0], dup_edge[1])
                if rxn not in marker_set:
                    marker_set.add(rxn)
                else:
                    dup_edges_to_delete.append(dup_edge)
            dup_edges_to_delete = [reverse_edge(edge) for edge in dup_edges_to_delete]
            for link in dup_edges_to_delete:
                del edges_attributes[link]
            graph.remove_edges_from(edges_to_delete + dup_edges_to_delete)
        else:
            graph.remove_edges_from(edges_to_delete)
        nx.set_edge_attributes(graph, edges_attributes)
        return

    def merge_reactions2rules(self, graph):
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
            for i, rxn in enumerate(self.model.reactions_bidirectional):
                if rxn['rule'][0] == rule.name:
                    rxns.append('r{0}'.format(i))
            rxn_per_rule[(rule.name, r_idx)] = rxns
        node_attrs = {'shape': 'roundrectangle', 'background_color': '#ff4c4c',
                      'NodeType': 'rule', 'bipartite': 1}
        for rule_info, rxns in rxn_per_rule.items():
            rule = self.model.rules.get(rule_info[0])
            node_attrs['kf'] = str(rule.rate_forward.get_value())
            node_attrs['kr'] = str(rule.rate_reverse.get_value()) if rule.rate_reverse else 'None'
            node_attrs['label'] = rule_info[0]
            node_attrs['index'] = 'rule' + str(rule_info[1])
            self.merge_nodes(graph, rxns, rule_info[0], **node_attrs)
        return

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


def in_cp_list(cp, cp_list):
    if [s for s in cp_list if match_complex_pattern(s, cp, exact=False)]:
        return True
    else:
        return False


def get_cp_idx(cp, cp_list):
    idx = None
    for c, c_idx in cp_list:
        if match_complex_pattern(c, cp, exact=False):
            idx = c_idx
            break
    return idx


def parse_name(spec):
    """
    Function that writes short names of the species to name the nodes.
    It counts how many times a monomer_pattern is present in the complex pattern an its states
    then it takes only the monomer name and its state to write a shorter name to name the nodes.

    Parameters
    ----------
    spec : pysb.ComplexPattern
        Name of species to parse

    Returns
    -------
    Parsed name of species
    """
    m = spec.monomer_patterns
    lis_m = []
    name_counts = {}
    parsed_name = ''
    for i in range(len(m)):
        sp_name = str(m[i]).partition('(')[0]
        sp_comp = str(m[i]).partition('** ')[-2:]
        sp_comp = ''.join(sp_comp)
        sp_states = re.findall(r"['\"](.*?)['\"]", str(m[i]))  # Matches strings between quotes
        sp_states = [s.lower() for s in sp_states]
        # tmp_2 = re.findall(r"(?<=\').+(?=\')", str(m[i]))
        if not sp_states and not sp_comp:
            lis_m.append(sp_name)
        else:
            sp_states.insert(0, sp_name)
            sp_states.insert(0, sp_comp)
            sp_states.reverse()
            lis_m.append(''.join(sp_states))
    for name in lis_m:
        name_counts[name] = lis_m.count(name)

    for sp, counts in name_counts.items():
        if counts == 1:
            parsed_name += sp + '-'
        else:
            parsed_name += str(counts) + sp + '-'
    return parsed_name[:len(parsed_name) - 1]
