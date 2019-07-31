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
        for s in self.model.species:
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

        for r in self.model.reactions:

            # edges
            reactants = r.getListOfReactants()
            products = r.getListOfProducts()
            if r.getReversible():
                attr_edge = {'source_arrow_shape': 'diamond', 'target_arrow_shape': 'triangle',
                             'source_arrow_fill': 'hollow', 'arrowhead': 'normal'}
            else:
                attr_edge = {'source_arrow_shape': 'none', 'target_arrow_shape': 'triangle',
                             'source_arrow_fill': 'filled', 'arrowhead': 'normal'}
            for s in reactants:
                for p in products:
                    sp_graph.add_edge(s.getSpecies(), p.getSpecies(), **attr_edge)

        return sp_graph

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
        hf.add_communities(graph, all_levels=all_levels, random_state=random_state)
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
        data = from_networkx(graph)
        return data
