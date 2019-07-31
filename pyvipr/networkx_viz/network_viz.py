from pyvipr.util_networkx import from_networkx


class NetworkViz(object):
    def __init__(self, network):
        self.network = network

    def network_static_view(self):
        self.network.graph['name'] = ''
        json = from_networkx(self.network)
        return json

    def dynamic_network_view(self):
        # This is necessary because the javascript part chooses to render
        # a static or dynamic visualization depending on the name
        # of the function.
        data = from_networkx(self.network)
        return data
