from collections import OrderedDict
import networkx as nx
import json
from .util_networkx import from_networkx
import collections
import sympy
import numpy as np
from pysb.simulator import SimulationResult
import matplotlib.colors as colors
import matplotlib.cm as cm
from pysbjupyter.static_viz import StaticViz, graph_to_json, dot_layout


class OrderedGraph(nx.DiGraph):
    """
    Networkx Digraph that stores the nodes in the order they are input
    """
    node_dict_factory = OrderedDict
    adjlist_outer_dict_factory = OrderedDict
    adjlist_inner_dict_factory = OrderedDict
    edge_attr_dict_factory = OrderedDict


class MidpointNormalize(colors.Normalize):
    """
    A class which, when called, can normalize data into the ``[vmin,midpoint,vmax] interval
    """

    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))


class ModelVisualization(object):
    """
    Class to visualize models and their dynamics

    Parameters
    ----------
    simulation : pysb SimulationResult
        A SimulationResult instance of the model that is going to be visualized.
    """
    mach_eps = np.finfo(float).eps

    def __init__(self, simulation):
        if not isinstance(simulation, SimulationResult):
            raise TypeError('Argument must be a pysb SimulationResult object')
        self.model = simulation._model
        self.tspan = simulation.tout[0]
        self.y = simulation.all
        param_values = simulation.param_values[0]
        self.param_dict = dict((p.name, param_values[i]) for i, p in enumerate(self.model.parameters))
        self.sp_graph = None
        self.passengers = []
        self.type_viz = ''

    def dynamic_view(self, type_viz='consumption', get_passengers=True):
        """
        Generates a dictionary with the model dynamics data that can be converted in the Cytoscape.js JSON format

        Parameters
        ----------
        type_viz : str
            Type of the dynamic visualization, it can be 'consumption' or 'production'
        get_passengers : bool
            if True, nodes that only have one incoming or outgoing edge are painted with a different color


        Examples
        --------
        >>> from pysb.examples.earm_1_0 import model
        >>> import numpy as np
        >>> viz = ModelVisualization(model)
        >>> data = viz.dynamic_view(tspan=np.linspace(0, 20000, 100))

        Returns
        -------
        A Dictionary Object that can be converted into Cytoscape.js JSON
        """
        self.type_viz = type_viz
        self.sp_graph = StaticViz(self.model).species_graph()
        self.sp_graph.graph['view'] = 'dynamic'
        self.sp_graph.graph['tspan'] = self.tspan.tolist()
        self.sp_graph.graph['name'] = self.model.name
        g_layout = dot_layout(self.sp_graph)
        self._add_edge_node_dynamics()
        data = graph_to_json(sp_graph=self.sp_graph, layout=g_layout)
        return data

    def _add_edge_node_dynamics(self):
        """
        Add the edge size and color data as well as node color and values data
        Returns
        -------

        """
        # in networkx 2.0 the order is G, values, names
        # in networkx 1.11 the order is G, names, values
        if float(nx.__version__) >= 2:
            edge_sizes, edge_colors, edge_qtips = self.edges_colors_sizes()
            nx.set_edge_attributes(self.sp_graph, edge_colors, 'edge_color')
            nx.set_edge_attributes(self.sp_graph, edge_sizes, 'edge_size')
            nx.set_edge_attributes(self.sp_graph, edge_qtips, 'edge_qtip')

            node_abs, node_rel = self.node_data()
            nx.set_node_attributes(self.sp_graph, node_abs, 'abs_value')
            nx.set_node_attributes(self.sp_graph, node_rel, 'rel_value')
        else:
            edge_sizes, edge_colors, edge_qtips = self.edges_colors_sizes()
            nx.set_edge_attributes(self.sp_graph, 'edge_color', edge_colors)
            nx.set_edge_attributes(self.sp_graph, 'edge_size', edge_sizes)
            nx.set_edge_attributes(self.sp_graph, 'edge_qtip', edge_qtips)

            node_abs, node_rel = self.node_data()
            nx.set_node_attributes(self.sp_graph, 'abs_value', node_abs)
            nx.set_node_attributes(self.sp_graph, 'rel_value', node_rel)

    @staticmethod
    def _get_max_rrs(rxns_matrix_sp, diff_par):
        # Tropicalization
        sp_rr = rxns_matrix_sp
        sp_rr_dom = np.zeros(sp_rr.shape)
        # sp_rr_neg = np.zeros(sp_rr.shape)
        for col in range(sp_rr.shape[1]):
            # Indices of positive and negative rates at each time point
            # log10 of the positive and negative reaction rates
            pos_idx = np.where(sp_rr[:, col] > 0)[0]
            neg_idx = np.where(sp_rr[:, col] < 0)[0]
            rr_pos = np.log10(sp_rr[:, col][pos_idx])
            rr_neg = np.log10(np.abs(sp_rr[:, col][neg_idx]))

            if rr_neg.size != 0:
                max_val_neg = np.amax(rr_neg)
                dom_rr_neg = [neg_idx[n] for n, i in enumerate(rr_neg)
                              if i > (max_val_neg - diff_par) and max_val_neg > -5]
                if not dom_rr_neg:
                    dom_rr_neg = neg_idx
                sp_rr_dom[:, col][dom_rr_neg] = sp_rr[:, col][dom_rr_neg]

            if rr_pos.size != 0:
                max_val_pos = np.amax(rr_pos)
                dom_rr_pos = [pos_idx[n] for n, i in enumerate(rr_pos)
                              if i > (max_val_pos - diff_par) and max_val_pos > -5]
                if not dom_rr_pos:
                    dom_rr_pos = pos_idx
                sp_rr_dom[:, col][dom_rr_pos] = sp_rr[:, col][dom_rr_pos]
        return sp_rr_dom

    def matrix_bidirectional_rates(self):
        rxns_matrix = np.zeros((len(self.model.reactions_bidirectional), len(self.tspan)))

        # Calculates matrix of bidirectional reaction rates
        for idx, reac in enumerate(self.model.reactions_bidirectional):
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

        Returns
        -------
        This function obtains values for the size and color of the edges in the network.
        The color is a representation of the percentage of flux going through an edge.
        The edge size is a representation of the relative value of the reaction normalized to the maximum value that
        the edge can attain during the whole simulation.
        """
        all_rate_colors = {}
        all_rate_sizes = {}
        all_rate_abs_val = {}

        rxns_matrix = self.matrix_bidirectional_rates()
        vals_norm = np.vectorize(self.mon_normalized)
        all_products = [rx['products'] for rx in self.model.reactions_bidirectional]
        all_reactants = [rx['reactants'] for rx in self.model.reactions_bidirectional]
        sp_imp = set(range(len(self.model.species))) - set(self.passengers)  # species with more than one edge
        # TODO: Make sure that product nodes that also have more than one incoming node, don't overwrite previous nodes edges attrs

        for sp in sp_imp:
            # Getting the indices of the reactions_bidirectional in which sp is a reactant and a product, respectively
            rxns_idx_reactant = [i for i, rx in enumerate(all_reactants) if sp in rx]
            rxns_idx_product = [i for i, rx in enumerate(all_products) if sp in rx]
            repeated_rxn = set(rxns_idx_reactant) & set(rxns_idx_product)
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

            # The max and min of the group of reaction rates
            if rxn_val_pos.size != 0:
                rxn_val_pos_max = np.amax(rxn_val_pos) + self.mach_eps

            if rxn_val_neg.size != 0:
                rxn_val_neg_max = np.amax(rxn_val_neg) + self.mach_eps

            # Tropicalization
            # TODO: Find a better way, so the function doesnt have to check if maxplus is false or true at each step
            # if maxplus:
            #     sp_rr_dom = self._get_max_rrs(rxns_matrix[rxns_idx_reactant], 1)
            # else:
            #     sp_rr_dom = rxns_matrix[rxns_idx_reactant]
            #     sp_prr_dom = rxns_matrix[rxns_idx_product]

            sp_rr_dom = rxns_matrix[rxns_idx_reactant]
            sp_prr_dom = rxns_matrix[rxns_idx_product]

            if self.type_viz == 'consumption':
                for rx_idx, rx in enumerate(rxns_idx_reactant):
                    products = all_products[rx]
                    for p in products:
                        # Normalizing by the total flux in a node
                        react_rate_color = rxns_matrix[rx] / rxn_val_pos_total
                        rxn_neg_idx = np.where(react_rate_color < 0)
                        react_rate_color[rxn_neg_idx] = (
                                    rxns_matrix[rx][rxn_neg_idx] / rxn_val_neg_total[rxn_neg_idx])
                        np.nan_to_num(react_rate_color, copy=False)
                        rate_colors = self.f2hex_edges(react_rate_color)

                        rxn_eps = sp_rr_dom[rx_idx] + self.mach_eps  # rxns_matrix[rx] + self.mach_eps
                        react_rate_size = np.zeros(len(rxn_eps))
                        tro_pos_idx = np.where(rxn_eps > 0)[0]
                        tro_neg_idx = np.where(rxn_eps < 0)[0]

                        if tro_neg_idx.size != 0:
                            react_rate_size[tro_neg_idx] = vals_norm(np.abs(rxn_eps[tro_neg_idx]),
                                                                     rxn_val_neg_max)

                        if tro_pos_idx.size != 0:
                            react_rate_size[tro_pos_idx] = vals_norm(rxn_eps[tro_pos_idx],
                                                                     rxn_val_pos_max)

                        rate_sizes = self.range_normalization(react_rate_size, min_x=0, max_x=1)
                        edges_id = ('s{0}'.format(sp), 's{0}'.format(p))
                        all_rate_colors[edges_id] = rate_colors
                        all_rate_sizes[edges_id] = rate_sizes.tolist()
                        all_rate_abs_val[edges_id] = rxns_matrix[rx].tolist()

            elif self.type_viz == 'production':
                for rp_idx, rp in enumerate(rxns_idx_product):
                    reactants = all_reactants[rp]
                    for r in reactants:
                        preact_rate_color = rxns_matrix[rp] / rxn_val_neg_total
                        prxns_neg_idx = np.where(preact_rate_color < 0)
                        preact_rate_color[prxns_neg_idx] = (
                                rxns_matrix[rp][prxns_neg_idx] / rxn_val_pos_total[prxns_neg_idx])
                        prate_colors = self.f2hex_edges(preact_rate_color)

                        prxn_eps = sp_prr_dom[rp_idx] + self.mach_eps
                        preact_rate_size = np.zeros(len(prxn_eps))
                        ptro_pos_idx = np.where(prxn_eps > 0)[0]
                        ptro_neg_idx = np.where(prxn_eps < 0)[0]

                        if ptro_neg_idx.size != 0:
                            preact_rate_size[ptro_neg_idx] = vals_norm(np.abs(prxn_eps[ptro_neg_idx]),
                                                                     rxn_val_pos_max)

                        if ptro_pos_idx.size != 0:
                            preact_rate_size[ptro_pos_idx] = vals_norm(prxn_eps[ptro_pos_idx],
                                                                     rxn_val_neg_max)

                        prate_sizes = self.range_normalization(preact_rate_size, min_x=0, max_x=1)
                        edges_id = ('s{0}'.format(r), 's{0}'.format(sp))
                        all_rate_colors[edges_id] = prate_colors
                        all_rate_sizes[edges_id] = prate_sizes.tolist()
                        all_rate_abs_val[edges_id] = rxns_matrix[rp].tolist()

        for sp in self.passengers:
            rxns_idx_reactant = [all_reactants.index(rx) for rx in all_reactants if sp in rx]
            for rx in rxns_idx_reactant:
                products = all_products[rx]
                for p in products:
                    edges_id = ('s{0}'.format(sp), 's{0}'.format(p))
                    all_rate_colors[edges_id] = ['#A4A09F'] * len(self.tspan)
                    all_rate_sizes[edges_id] = [0.5] * len(self.tspan)
                    all_rate_abs_val[edges_id] = rxns_matrix[rx].tolist()

        return all_rate_sizes, all_rate_colors, all_rate_abs_val

    def node_data(self):
        """
        Converts concentration values to colors to be used in the nodes
        :return: Returns a pandas data frame where each row is a node and each column a time point, with the color value
        """
        node_absolute = {}
        node_relative = {}
        for sp in range(len(self.model.species)):
            sp_absolute = self.y['__s{}'.format(sp)]
            sp_relative = (sp_absolute / sp_absolute.max()) * 100
            node_absolute['s{0}'.format(sp)] = sp_absolute.tolist()
            node_relative['s{0}'.format(sp)] = sp_relative.tolist()

        # all_nodes_values = pandas.DataFrame(all_rate_colors)
        return node_absolute, node_relative

    @staticmethod
    def f2hex_edges(fx, vmin=-0.99, vmax=0.99):
        """
        Converts reaction rates values to f2hex colors
        :param fx: Vector of reaction rates (flux)
        :param vmin: Value of minimum for normalization
        :param vmax: Value of maximum for normalization
        :return: This function returns a vector of colors in hex format that represents flux
        """

        norm = MidpointNormalize(vmin=vmin, vmax=vmax, midpoint=0)
        f2rgb = cm.ScalarMappable(norm=norm, cmap=cm.get_cmap('RdBu_r'))
        rgb = [f2rgb.to_rgba(rate)[:3] for rate in fx]
        colors_hex = [0] * (len(rgb))
        for i, color in enumerate(rgb):
            colors_hex[i] = '#{0:02x}{1:02x}{2:02x}'.format(*tuple([int(255 * fc) for fc in color]))
        return colors_hex

    @staticmethod
    def range_normalization(x, min_x, max_x, a=0.5, b=10):
        """
        Normalized vector to the [0.1,15] range
        :param x: Vector of numbers to be normalized
        :param min_x: Minimum value in vector x
        :param max_x: Maximum value in vector x
        :param a: Value of minimum used for the normalization
        :param b: Value of maximum used for the normalization
        :return: Normalized vector
        """
        return a + (x - min_x) * (b - a) / (max_x - min_x)

    @staticmethod
    def mon_normalized(x, max_value):
        return x / max_value

