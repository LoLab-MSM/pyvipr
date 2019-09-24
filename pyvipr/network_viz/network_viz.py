from pyvipr.util_networkx import from_networkx
import networkx as nx


class NetworkViz(object):
    def __init__(self, network):
        self.network = network.copy()

    def network_static_view(self):
        self.network.graph['name'] = ''
        json = from_networkx(self.network)
        return json

    def nx_function_view(self, nx_function, **kwargs):

        self.network.graph['name'] = ''
        result = nx_function(self.network, **kwargs)
        if nx_function.__name__ == 'girvan_newman':
            top_level_communities = next(result)
        else:
            top_level_communities = result

        top_level_communities = {idx: 'c_{0}'.format(comm) for comm, nodes in
                                 enumerate(top_level_communities) for idx in nodes}
        cnodes = set(top_level_communities.values())

        self.network.add_nodes_from(cnodes, NodeType='community')
        nx.set_node_attributes(self.network, top_level_communities, 'parent')
        json = from_networkx(self.network)
        return json

    def dynamic_network_view(self):
        # This is necessary because the javascript part chooses to render
        # a static or dynamic visualization depending on the name
        # of the function.
        data = from_networkx(self.network)
        return data
