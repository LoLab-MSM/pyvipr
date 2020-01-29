import networkx as nx
from six import string_types
import tellurium
from pyvipr.util_networkx import from_networkx
import pyvipr.util as hf
import math

try:
    import tesbml as libsbml
except ImportError:
    import libsbml


class TelluriumStaticViz(object):
    """
    Class to generate static visualization of sbml models from tellurium
    """

    def __init__(self, model):
        if isinstance(model, tellurium.roadrunner.extended_roadrunner.ExtendedRoadRunner):
            model_sbml = model.getSBML()
            self.doc = libsbml.readSBMLFromString(model_sbml)
            self.model = self.doc.getModel()
        elif isinstance(model, string_types):
            self.doc = libsbml.readSBMLFromString(model)
            self.model = self.doc.getModel()
        elif isinstance(model, libsbml.SBMLDocument):
            self.doc = model
            self.model = self.doc.getModel()
        elif isinstance(model, libsbml.Model):
            self.model = model
        else:
            raise Exception('SBML Input is not valid')
        self.graph = None

    def species_graph(self):
        """
        Creates a graph of the model species interactions
        Returns
        -------
        nx.Digraph
            Graph that has the information for the visualization of the model
        """
        sp_graph = nx.DiGraph(name='Tellurium model')
        for s in self.model.getListOfSpecies():
            if s.getName():
                label = s.getName()
            else:
                label = s.getId()
            if s.getInitialConcentration() == 0 or math.isnan(s.getInitialConcentration()):
                color = "#2b913a"
            else:
                color = "#aaffff"

            node_data = dict(label=label,
                             background_color=color,
                             shape='ellipse',
                             NodeType='species',
                             spInitial=s.getInitialConcentration())
            sp_graph.add_node(s.getId(), **node_data)

        for r in self.model.getListOfReactions():
            if r.getReversible():
                attr_edge = {'source_arrow_shape': 'triangle', 'target_arrow_shape': 'triangle',
                             'source_arrow_fill': 'hollow', 'arrowhead': 'normal'}
            else:
                attr_edge = {'source_arrow_shape': 'none', 'target_arrow_shape': 'triangle',
                             'source_arrow_fill': 'filled', 'arrowhead': 'normal'}
            for s in r.getListOfReactants():
                for p in r.getListOfProducts():
                    sp_graph.add_edge(s.getSpecies(), p.getSpecies(), **attr_edge)

        return sp_graph

    def sp_rxns_graph(self):
        """
        Creates a bipartite nx.DiGraph graph where one set of nodes is the model species
        and the other set is the model bidirectional reactions.

        Returns
        -------
        nx.Digraph
            Graph that has the information for the visualization of the model
        """
        graph = nx.DiGraph(name='Tellurium model')
        for s in self.model.getListOfSpecies():
            if s.getName():
                label = s.getName()
            else:
                label = s.getId()
            if s.getInitialConcentration() == 0 or math.isnan(s.getInitialConcentration()):
                color = "#2b913a"
            else:
                color = "#aaffff"

            node_data = dict(label=label,
                             background_color=color,
                             shape='ellipse',
                             NodeType='species',
                             spInitial=s.getInitialConcentration(),
                             bipartite=0)
            graph.add_node(s.getId(), **node_data)

        for r in self.model.getListOfReactions():
            # reaction nodes
            if r.getName():
                label = r.getName()
            else:
                label = r.getId()

            graph.add_node(r.getId(),
                           label=label,
                           shape='roundrectangle',
                           background_color='#d3d3d3',
                           NodeType='reaction',
                           kf='',
                           kr='',
                           bipartite=1)

            if r.getReversible():
                attr_edge = {'source_arrow_shape': 'triangle', 'target_arrow_shape': 'triangle',
                             'source_arrow_fill': 'hollow', 'arrowhead': 'normal'}
            else:
                attr_edge = {'source_arrow_shape': 'none', 'target_arrow_shape': 'triangle',
                             'source_arrow_fill': 'filled', 'arrowhead': 'normal'}
            attr_modifiers = {'source_arrow_shape': 'diamond', 'target_arrow_shape': 'diamond',
                              'source_arrow_fill': 'filled'}
            for s in r.getListOfReactants():
                graph.add_edge(s.getSpecies(), r.getId(), **attr_edge)
            for s in r.getListOfProducts():
                graph.add_edge(r.getId(), s.getSpecies(), **attr_edge)
            for s in r.getListOfModifiers():
                graph.add_edge(s.getSpecies(), r.getId(), **attr_modifiers)

        return graph

    def sp_rxns_view(self):
        """
        Generate a dictionary that contains the species and reactions network information

        Returns
        -------
        dict
            A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
            contains all the information (nodes,edges, positions) to generate a cytoscapejs network.
        """
        graph = self.sp_rxns_graph()
        data = from_networkx(graph)
        return data

    def sp_view(self):
        """
        Generate a dictionary that contains the species network information

        Returns
        -------
        dict
            A Dictionary object that can be converted into Cytoscape.js JSON. This dictionary
            contains all the information (nodes,edges, positions) to generate a cytoscapejs network.
        """
        graph = self.species_graph()
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