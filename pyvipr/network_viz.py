from pyvipr.static_viz import graph_to_json


class NetworkViz(object):
    def __init__(self, network):
        self.network = network

    def network_static_view(self):
        self.network.graph['name'] = ''
        json = graph_to_json(self.network)
        return json

    def dynamic_network_view(self):
        # This is necessary because the javascript part chooses to render
        # a static or dynamic visualization depending on the name
        # of the function.
        data = graph_to_json(sp_graph=self.network)
        return data
