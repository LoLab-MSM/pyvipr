from pyvipr.static_viz import graph_to_json, dot_layout


class NetworkViz(object):
    def __init__(self, network):
        self.network = network

    def network_static_view(self):
        self.network.graph['name'] = ''
        d_layout = dot_layout(self.network)
        json = graph_to_json(self.network, layout=d_layout)
        return json

    def dynamic_network_view(self):
        # This is necessary because the javascript part chooses to render
        # a static or dynamic visualization depending on the name
        # of the function.
        g_layout = dot_layout(self.network)
        data = graph_to_json(sp_graph=self.network, layout=g_layout)
        return data
