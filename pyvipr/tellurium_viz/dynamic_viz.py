import numpy as np
import tellurium
import networkx as nx
from pyvipr.tellurium_viz.static_viz import TelluriumStaticViz
from pyvipr.util_networkx import from_networkx
import pyvipr.util as hf
try:
    import tesbml as libsbml
except ImportError:
    import libsbml


class TelluriumDynamicViz(object):
    """
    class to visualize the dynamics of systems biology models defined in sbml or antimony format

    Parameters
    ----------
    sim_model: tellurium roadrunner
        A roadrunner instance after a simulation
    """
    mach_eps = np.finfo(float).eps

    def __init__(self, sim_model):
        if isinstance(sim_model, tellurium.roadrunner.extended_roadrunner.ExtendedRoadRunner):
            model_sbml = sim_model.getSBML()
            self.doc = libsbml.readSBMLFromString(model_sbml)
            self.model = self.doc.getModel()
        else:
            raise Exception('Model must be a roadrunner instance')

        required_selections = ['time'] + [s.getId() for s in self.model.species] + \
                              [r.getId() for r in self.model.reactions]
        sim_selections = sim_model.selections

        # Check that the simulation selections include all species and reactions rate values
        if not all(x in required_selections for x in sim_selections):
            raise ValueError('To use this visualization you must use '
                             'this simulator selection \n {0}'.format(required_selections))
        self.y = sim_model.getSimulationData()
        self.sp_graph = None
        self.type_viz = 'consumption'

    def dynamic_sp_view(self, type_viz='consumption'):
        """
        Generates a dictionary with the model dynamics data that can be converted in the Cytoscape.js JSON format

        Parameters
        ----------
        type_viz : str
            Type of the dynamic visualization, it can be 'consumption' or 'production'

        Returns
        -------
        dict
            A Dictionary Object with all nodes and edges information that
            can be converted into Cytoscape.js JSON to be visualized
        """
        self.type_viz = type_viz
        self.sp_graph = TelluriumStaticViz(self.model).species_graph()
        self.sp_graph.graph['nsims'] = 1
        self.sp_graph.graph['tspan'] = self.y['time'].tolist()
        self._add_edge_node_dynamics()
        data = from_networkx(self.sp_graph)
        return data

    def matrix_reaction_rates(self):
        rxns_matrix = np.zeros((len(self.model.reactions), len(self.y['time'])))

        # Calculates matrix of bidirectional reaction rates
        for idx, reac in enumerate(self.model.reactions):
            rxns_matrix[idx] = self.y[reac.getId()]
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

        rxns_matrix = self.matrix_reaction_rates()
        all_products = [[s.getSpecies() for s in rx.getListOfProducts()] for rx in self.model.reactions]
        all_reactants = [[s.getSpecies() for s in rx.getListOfReactants()] for rx in self.model.reactions]

        for sp in self.model.species:
            rxns_idx_reactant = [i for i, rx in enumerate(all_reactants) if sp.getId() in rx]
            rxns_idx_product = [i for i, rx in enumerate(all_products) if sp.getId() in rx]
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

            if self.type_viz == 'consumption':
                sp_rr_dom = rxns_matrix[rxns_idx_reactant]

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
                        rate_colors = hf.f2hex_edges(react_rate_color)

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
                        edges_id = (sp.getId(), p)
                        all_rate_colors[edges_id] = rate_colors
                        all_rate_sizes[edges_id] = rate_sizes.tolist()
                        all_rate_abs_val[edges_id] = rxns_matrix[rx].tolist()

            elif self.type_viz == 'production':
                sp_prr_dom = rxns_matrix[rxns_idx_product]

                for rp_idx, rp in enumerate(rxns_idx_product):
                    reactants = all_reactants[rp]
                    for r in reactants:
                        with np.errstate(divide='ignore', invalid='ignore'):
                            preact_rate_color = rxns_matrix[rp] / rxn_val_neg_total
                            prxns_neg_idx = np.where(preact_rate_color < 0)
                            preact_rate_color[prxns_neg_idx] = (
                                    rxns_matrix[rp][prxns_neg_idx] / rxn_val_pos_total[prxns_neg_idx])
                        np.nan_to_num(preact_rate_color, copy=False)
                        prate_colors = hf.f2hex_edges(preact_rate_color)

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
                        edges_id = (r, sp.getId())
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
        for sp in self.model.species:
            sp_absolute = np.absolute(self.y[sp.getId()])
            sp_relative = (sp_absolute / sp_absolute.max()) * 100
            node_absolute[sp.getId()] = sp_absolute.tolist()
            node_relative[sp.getId()] = sp_relative.tolist()

        # all_nodes_values = pandas.DataFrame(all_rate_colors)
        return node_absolute, node_relative

    def _add_edge_node_dynamics(self):
        """
        Add the edge size and color data as well as node color and values data
        Returns
        -------

        """
        edge_sizes, edge_colors, edge_qtips = self.edges_colors_sizes()
        nx.set_edge_attributes(self.sp_graph, edge_colors, 'edge_color')
        nx.set_edge_attributes(self.sp_graph, edge_sizes, 'edge_size')
        nx.set_edge_attributes(self.sp_graph, edge_qtips, 'edge_qtip')

        node_abs, node_rel = self.node_data()
        nx.set_node_attributes(self.sp_graph, node_abs, 'abs_value')
        nx.set_node_attributes(self.sp_graph, node_rel, 'rel_value')
