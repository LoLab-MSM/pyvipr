import networkx as nx
import sympy
import numpy as np
from pysb.simulator import SimulationResult
from pyvipr.pysb_viz.static_viz import PysbStaticViz
import pyvipr.util as hf
from pyvipr.util_networkx import from_networkx


class PysbDynamicViz(object):
    """
    Class to visualize the dynamics of systems biology models defined in PySB format.

    Parameters
    ----------
    simulation : pysb SimulationResult
        A SimulationResult instance of the model that is going to be visualized.
    sim_idx : Index of simulation to be visualized
    cmap : str or Colormap instance
        The colormap used to map the reaction rate values to RGBA colors. For more information
        visit: https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html
    """
    mach_eps = np.finfo(float).eps

    def __init__(self, simulation, sim_idx=0, cmap='RdBu_r'):
        if not isinstance(simulation, SimulationResult):
            raise TypeError('Argument must be a pysb SimulationResult object')
        self.model = simulation._model
        self.nsims = simulation.nsims
        if self.nsims == 1:
            self.y = simulation.all
        else:
            self.y = simulation.all[sim_idx]
        self.tspan = simulation.tout[sim_idx]
        param_values = simulation.param_values[sim_idx]
        self.param_dict = dict((p.name, param_values[i]) for i, p in enumerate(self.model.parameters))
        # Add expressions with constant value to dictionary of parameter values
        if self.model.expressions:
            for expr in self.model.expressions:
                self.param_dict[expr.name] = expr.get_value()
        self.sp_graph = None
        self.type_viz = ''
        self.cmap = cmap

    def dynamic_sp_view(self, type_viz='consumption'):
        """
        Generates a dictionary with the model dynamics data that can be converted in the Cytoscape.js JSON format

        Parameters
        ----------
        type_viz : str
            Type of the dynamic visualization, it can be 'consumption' or 'production'

        Examples
        --------
        >>> from pysb.examples.earm_1_0 import model
        >>> from pysb.simulator import ScipyOdeSimulator
        >>> import pyvipr.pysb_viz.dynamic_viz as viz
        >>> import numpy as np
        >>> tspan = np.linspace(0, 20000)
        >>> sim = ScipyOdeSimulator(model, tspan).run()
        >>> dyn_viz = viz.PysbDynamicViz(sim)
        >>> data = dyn_viz.dynamic_sp_view()

        Returns
        -------
        dict
            A Dictionary Object with all nodes and edges information that
            can be converted into Cytoscape.js JSON to be visualized
        """
        self.type_viz = type_viz
        self.sp_graph = PysbStaticViz(self.model).species_graph()
        self.sp_graph.graph['nsims'] = self.nsims
        self.sp_graph.graph['tspan'] = self.tspan.tolist()
        self._add_edge_node_dynamics()
        data = from_networkx(self.sp_graph)
        return data

    def dynamic_sp_comp_view(self, type_viz='consumption'):
        """
        Same as :py:meth:`dynamic_view` but the species nodes are grouped
        by the compartments they belong to

        """
        self.type_viz = type_viz
        self.sp_graph = PysbStaticViz(self.model).compartments_data_graph()
        self.sp_graph.graph['nsims'] = self.nsims
        self.sp_graph.graph['tspan'] = self.tspan.tolist()
        self._add_edge_node_dynamics()
        data = from_networkx(self.sp_graph)
        return data

    def dynamic_sp_comm_view(self, type_viz='consumption', random_state=None):
        """
        Same as :py:meth:`dynamic_view` but the species nodes are grouped
        by the communities they belong to. Communities are obtained using the 
        Louvain algorithm.

        Parameters
        ----------
        type_viz: str
            Type of visualization. It can be `consumption` to see how species are being consumed
            or `production` to see how the species are being produced.
        random_state: int
            Seed used by the random generator in community detection

        Returns
        -------
        dict
            A Dictionary Object with all nodes and edges information that
            can be converted into Cytoscape.js JSON to be visualized
        """
        self.type_viz = type_viz
        self.sp_graph = PysbStaticViz(self.model).species_graph()
        hf.add_louvain_communities(self.sp_graph, all_levels=False, random_state=random_state)
        self.sp_graph.graph['nsims'] = self.nsims
        self.sp_graph.graph['tspan'] = self.tspan.tolist()
        self._add_edge_node_dynamics()
        data = from_networkx(self.sp_graph)
        return data

    # def dynamic_node_dynamics(self, node):
    ## Node centric dynamics
    #     all_rate_colors = {}
    #     all_rate_sizes = {}
    #     all_rate_abs_val = {}
    #
    #     rxns_idxs = [idx for idx, rxn in enumerate(self.model.reactions_bidirectional)
    #                  if node in rxn['reactants'] or node in rxn['products']]
    #     rxns_matrix = self.matrix_bidirectional_rates(rxns_idxs=rxns_idxs)-
    #     for idx, reaction in enumerate(self.model.reactions_bidirectional[rxns_idxs]):
    #         reactants = set(reaction['reactants'])
    #         products = set(reaction['products'])
    #         for s in reactants:
    #             for p in products:
    #                 edges_id = ('s{0}'.format(s), 's{0}'.format(p))
    #                 all_rate_colors[edges_id] = rate_colors
    #                 all_rate_sizes[edges_id] = rate_sizes.tolist()
    #                 all_rate_abs_val[edges_id] = rxns_matrix[idx].tolist()


    def _add_edge_node_dynamics(self):
        """
        Add the edge size and color data as well as node color and values data
        Returns
        -------

        """
        edge_sizes, edge_colors, edge_qtips = self.edges_colors_sizes()
        nx.set_edge_attributes(self.sp_graph, edge_colors, 'edge_color')
        nx.set_edge_attributes(self.sp_graph, edge_sizes, 'edge_size')
        nx.set_edge_attributes(self.sp_graph, edge_qtips, 'qtip')

        node_abs, node_rel = self.node_data()
        nx.set_node_attributes(self.sp_graph, node_abs, 'qtip')
        nx.set_node_attributes(self.sp_graph, node_rel, 'rel_value')

    def matrix_bidirectional_rates(self, rxns_idxs=None):
        """
        Obtains the values of the reaction rates at all the time points of the simulation
        
        Returns
        -------
        np.ndarray 
            Array with the reaction rates values
        """
        if rxns_idxs is not None:
            rxns_bidirectional = self.model.reactions_bidirectional[rxns_idxs]
        else:
            rxns_bidirectional = self.model.reactions_bidirectional

        rxns_matrix = np.zeros((len(rxns_bidirectional), len(self.tspan)))

        # Calculates matrix of bidirectional reaction rates
        for idx, reac in enumerate(rxns_bidirectional):
            rate_reac = reac['rate']
            for p in self.param_dict:
                rate_reac = rate_reac.subs(p, self.param_dict[p])
            variables = [atom for atom in rate_reac.atoms(sympy.Symbol)]
            args = [0] * len(variables)  # arguments to put in the lambdify function
            for idx2, va in enumerate(variables):
                if str(va).startswith('__'):
                    args[idx2] = self.y[str(va)]
                else:
                    args[idx2] = self.param_dict[va.name]
            func = sympy.lambdify(variables, rate_reac, modules=dict(sqrt=np.lib.scimath.sqrt))
            react_rate = func(*args)
            rxns_matrix[idx] = react_rate
        return rxns_matrix

    def edges_colors_sizes(self):
        """
        This function obtains values for the size and color of the edges in the network.
        The color is a representation of the percentage of flux going through an edge.
        The edge size is a representation of the relative value of the reaction normalized to the maximum value that
        the edge can attain during the whole simulation.
        
        Returns
        -------
        tuple
            Three dictionaries. The first one contains the information of the edge sizes at all time points. 
            The second one contains the information of the edge colors at all time points.
            The third one contains the values of the reaction rates at all time points.
        """
        all_rate_colors = {}
        all_rate_sizes = {}
        all_rate_abs_val = {}

        rxns_matrix = self.matrix_bidirectional_rates()
        all_products = [rx['products'] for rx in self.model.reactions_bidirectional]
        all_reactants = [rx['reactants'] for rx in self.model.reactions_bidirectional]
        sp_imp = range(len(self.model.species))  # species indices
        # TODO: Make sure that product nodes that also have more than one incoming node, don't overwrite
        #  previous nodes edges attrs

        for sp in sp_imp:
            # Getting the indices of the reactions_bidirectional in which sp is either
            # a reactant or a product, respectively
            rxns_idx_reactant = [i for i, rx in enumerate(all_reactants) if sp in rx]
            rxns_idx_product = [i for i, rx in enumerate(all_products) if sp in rx]
            repeated_rxn = set(rxns_idx_reactant) & set(rxns_idx_product)
            # Obtain indices of reactions in which sp is only a product
            rxns_idx_product = [c for c in rxns_idx_product if c not in repeated_rxn]

            # Getting arrays to obtain producing and consuming reactions
            rxn_val_pos = np.where(
                np.concatenate((rxns_matrix[rxns_idx_reactant] > 0, rxns_matrix[rxns_idx_product] < 0)),
                rxns_matrix[rxns_idx_reactant + rxns_idx_product], 0)  # Reactants are consumed
            rxn_val_neg = np.where(
                np.concatenate((rxns_matrix[rxns_idx_reactant] < 0, rxns_matrix[rxns_idx_product] > 0)),
                rxns_matrix[rxns_idx_reactant + rxns_idx_product], 0)  # Reactants are produced

            rxn_val_pos = np.abs(rxn_val_pos)
            rxn_val_neg = np.abs(rxn_val_neg)
            # An array with the total of reaction rates at each time point
            rxn_val_pos_total = rxn_val_pos.sum(axis=0)
            rxn_val_neg_total = rxn_val_neg.sum(axis=0)

            # The max and min of the group of reaction rates. It can be used to assign size to edges
            # based in the max and min of the groups of reaction rates across all time points
            # if rxn_val_pos.size != 0:
            #     rxn_val_pos_max = np.amax(rxn_val_pos) + self.mach_eps
            #
            # if rxn_val_neg.size != 0:
            #     rxn_val_neg_max = np.amax(rxn_val_neg) + self.mach_eps

            sp_rr_dom = rxns_matrix[rxns_idx_reactant]
            sp_prr_dom = rxns_matrix[rxns_idx_product]

            if self.type_viz == 'consumption':
                for rx_idx, rx in enumerate(rxns_idx_reactant):
                    products = all_products[rx]
                    for p in products:
                        # Normalizing by the total flux in a node
                        # We ignore division by zero and invalid value in less than function warnings
                        # as they are handled later on by converting nan values to 0
                        with np.errstate(divide='ignore', invalid='ignore'):
                            react_rate_color = rxns_matrix[rx] / rxn_val_pos_total
                            rxn_neg_idx = np.where(react_rate_color < 0)
                            react_rate_color[rxn_neg_idx] = (
                                        rxns_matrix[rx][rxn_neg_idx] / rxn_val_neg_total[rxn_neg_idx])
                        np.nan_to_num(react_rate_color, copy=False)
                        rate_colors = hf.f2hex_edges(react_rate_color, cmap=self.cmap)

                        rxn_eps = sp_rr_dom[rx_idx] + self.mach_eps  # rxns_matrix[rx] + self.mach_eps
                        react_rate_size = np.zeros(len(rxn_eps))
                        tro_pos_idx = np.where(rxn_eps > 0)[0]
                        tro_neg_idx = np.where(rxn_eps < 0)[0]

                        if tro_neg_idx.size != 0:
                            rxn_neg_max = np.amax(np.abs(rxn_eps[tro_neg_idx]))
                            react_rate_size[tro_neg_idx] = np.array([rxn_neg/rxn_neg_max for
                                                                     rxn_neg in np.abs(rxn_eps[tro_neg_idx])])

                        if tro_pos_idx.size != 0:
                            rxn_pos_max = np.amax(rxn_eps[tro_pos_idx])
                            react_rate_size[tro_pos_idx] = np.array([rxn_pos/rxn_pos_max for
                                                                     rxn_pos in rxn_eps[tro_pos_idx]])

                        rate_sizes = hf.range_normalization(react_rate_size, min_x=0, max_x=1)
                        edges_id = ('s{0}'.format(sp), 's{0}'.format(p))
                        all_rate_colors[edges_id] = rate_colors
                        all_rate_sizes[edges_id] = rate_sizes.tolist()
                        all_rate_abs_val[edges_id] = rxns_matrix[rx].tolist()

            elif self.type_viz == 'production':
                for rp_idx, rp in enumerate(rxns_idx_product):
                    reactants = all_reactants[rp]
                    for r in reactants:
                        with np.errstate(divide='ignore', invalid='ignore'):
                            preact_rate_color = rxns_matrix[rp] / rxn_val_neg_total
                            prxns_neg_idx = np.where(preact_rate_color < 0)
                            preact_rate_color[prxns_neg_idx] = (
                                    rxns_matrix[rp][prxns_neg_idx] / rxn_val_pos_total[prxns_neg_idx])
                        np.nan_to_num(preact_rate_color, copy=False)
                        prate_colors = hf.f2hex_edges(preact_rate_color, cmap=self.cmap)

                        prxn_eps = sp_prr_dom[rp_idx] + self.mach_eps
                        preact_rate_size = np.zeros(len(prxn_eps))
                        ptro_pos_idx = np.where(prxn_eps > 0)[0]
                        ptro_neg_idx = np.where(prxn_eps < 0)[0]

                        if ptro_neg_idx.size != 0:
                            prxn_neg_max = np.amax(np.abs(prxn_eps[ptro_neg_idx]))
                            preact_rate_size[ptro_neg_idx] = np.array([prxn_neg/prxn_neg_max for
                                                                       prxn_neg in np.abs(prxn_eps[ptro_neg_idx])])

                        if ptro_pos_idx.size != 0:
                            prxn_pos_max = np.amax(prxn_eps[ptro_pos_idx])
                            preact_rate_size[ptro_pos_idx] = np.array([prxn_pos/prxn_pos_max for
                                                                       prxn_pos in prxn_eps[ptro_pos_idx]])

                        prate_sizes = hf.range_normalization(preact_rate_size, min_x=0, max_x=1)
                        edges_id = ('s{0}'.format(r), 's{0}'.format(sp))
                        all_rate_colors[edges_id] = prate_colors
                        all_rate_sizes[edges_id] = prate_sizes.tolist()
                        all_rate_abs_val[edges_id] = rxns_matrix[rp].tolist()
            else:
                raise ValueError('The type of process can only be `consumption` or `production`')

        return all_rate_sizes, all_rate_colors, all_rate_abs_val

    def node_data(self):
        """
        Obtains the species concentration values and the relative concentration
        compared with the maximum concentration across all time points
        
        Returns
        -------
        tuple
            Two dictionaries. The first one has the species concentration. The
            second one has the relative species concentrations
        """
        node_absolute = {}
        node_relative = {}
        for sp in range(len(self.model.species)):
            sp_absolute = np.absolute(self.y['__s{}'.format(sp)])
            sp_relative = (sp_absolute / sp_absolute.max()) * 100
            node_absolute['s{0}'.format(sp)] = sp_absolute.tolist()
            node_relative['s{0}'.format(sp)] = sp_relative.tolist()

        # all_nodes_values = pandas.DataFrame(all_rate_colors)
        return node_absolute, node_relative
