from collections import OrderedDict
import networkx as nx
import sympy
import numpy as np
from pysb.simulator import SimulationResult
import matplotlib.colors as colors
import matplotlib.cm as cm
from pyvipr.static_viz import StaticViz, graph_to_json, dot_layout


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
    Class to visualize the dynamics of systems biology models defined in BNGL, SBML and PySB format.

    Parameters
    ----------
    simulation : pysb SimulationResult
        A SimulationResult instance of the model that is going to be visualized.
    sim_idx : Index of simulation to be visualized
    """
    mach_eps = np.finfo(float).eps

    def __init__(self, simulation, sim_idx=0):
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
        self.sp_graph = None
        self.passengers = []
        self.type_viz = ''

    def dynamic_view(self, type_viz='consumption'):
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
        >>> import numpy as np
        >>> tspan = np.linspace(0, 20000)
        >>> sim = ScipyOdeSimulator(model, tspan).run()
        >>> viz = ModelVisualization(sim)
        >>> data = viz.dynamic_view()

        Returns
        -------
        A Dictionary Object with all nodes and edges information that
        can be converted into Cytoscape.js JSON to be visualized
        """
        self.type_viz = type_viz
        self.sp_graph = StaticViz(self.model).species_graph()
        self.sp_graph.graph['view'] = 'dynamic'
        self.sp_graph.graph['nsims'] = self.nsims
        self.sp_graph.graph['tspan'] = self.tspan.tolist()
        g_layout = dot_layout(self.sp_graph)
        self._add_edge_node_dynamics()
        data = graph_to_json(sp_graph=self.sp_graph, layout=g_layout)
        return data

    def dynamic_compartments_view(self, type_viz='consumption'):
        self.type_viz = type_viz
        self.sp_graph = StaticViz(self.model).compartments_data_graph()
        self.sp_graph.graph['view'] = 'dynamic'
        self.sp_graph.graph['nsims'] = self.nsims
        self.sp_graph.graph['tspan'] = self.tspan.tolist()
        g_layout = dot_layout(self.sp_graph)
        self._add_edge_node_dynamics()
        data = graph_to_json(sp_graph=self.sp_graph, layout=g_layout)
        return data

    def dynamic_communities_view(self, type_viz='consumption', random_state=None):
        """

        Parameters
        ----------
        type_viz: str
            Type of visualization. It can be `consumption` to see how species are being consumed
            or `production` to see how the species are being produced.
        random_state: int
            Seed used by the random generator in community detection

        Returns
        -------

        """
        self.type_viz = type_viz
        self.sp_graph = StaticViz(self.model).communities_data_graph(random_state=random_state)
        self.sp_graph.graph['view'] = 'dynamic'
        self.sp_graph.graph['nsims'] = self.nsims
        self.sp_graph.graph['tspan'] = self.tspan.tolist()
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

    def matrix_bidirectional_rates(self):
        """
        Obtains the values of the reaction rates at all the time points of the simulation
        Returns
        -------
        An np.ndarray with the reaction rates values
        """
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
        This function obtains values for the size and color of the edges in the network.
        The color is a representation of the percentage of flux going through an edge.
        The edge size is a representation of the relative value of the reaction normalized to the maximum value that
        the edge can attain during the whole simulation.
        Returns
        -------
        Three dictionaries. The first one contains the information of the edge sizes at all time points.
        The second one contains the information of the edge colors at all time points.
        The third one contains the values of the reaction rates at all time points.
        """
        all_rate_colors = {}
        all_rate_sizes = {}
        all_rate_abs_val = {}

        rxns_matrix = self.matrix_bidirectional_rates()
        vals_norm = np.vectorize(self.mon_normalized)
        all_products = [rx['products'] for rx in self.model.reactions_bidirectional]
        all_reactants = [rx['reactants'] for rx in self.model.reactions_bidirectional]
        sp_imp = set(range(len(self.model.species))) - set(self.passengers)  # species with more than one edge
        # TODO: Make sure that product nodes that also have more than one incoming node, don't overwrite
        #  previous nodes edges attrs

        for sp in sp_imp:
            # Getting the indices of the reactions_bidirectional in which sp is a reactant and a product, respectively
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
                                                                     np.amax(np.abs(rxn_eps[tro_neg_idx])))

                        if tro_pos_idx.size != 0:
                            react_rate_size[tro_pos_idx] = vals_norm(rxn_eps[tro_pos_idx],
                                                                     np.amax(rxn_eps[tro_pos_idx]))

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
                                                                       np.amax(np.abs(prxn_eps[ptro_neg_idx])))

                        if ptro_pos_idx.size != 0:
                            preact_rate_size[ptro_pos_idx] = vals_norm(prxn_eps[ptro_pos_idx],
                                                                       np.amax(prxn_eps[ptro_pos_idx]))

                        prate_sizes = self.range_normalization(preact_rate_size, min_x=0, max_x=1)
                        edges_id = ('s{0}'.format(r), 's{0}'.format(sp))
                        all_rate_colors[edges_id] = prate_colors
                        all_rate_sizes[edges_id] = prate_sizes.tolist()
                        all_rate_abs_val[edges_id] = rxns_matrix[rp].tolist()
            else:
                raise ValueError('The type of process can only be `consumption` or `production`')

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
        Obtains the species concentration values and the relative concentration
        compared with the maximum concentration across all time points
        Returns
        -------
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

    @staticmethod
    def f2hex_edges(fx, vmin=-0.99, vmax=0.99):
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

        Returns
        -------
        A vector of colors in hex format that encodes the reaction rate values
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
        Normalize vector to the [0.5, 10] range
        Parameters
        ----------
        x: vector-like
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

    @staticmethod
    def mon_normalized(x, max_value):
        return x / max_value

