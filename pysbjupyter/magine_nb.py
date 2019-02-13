from .pysbviz import networkxViz


def render_network(json_graph, layout_name='cose-bilkent'):
    return networkxViz(data=json_graph, type_of_viz='magine_graph',
                       layout_name=layout_name)
