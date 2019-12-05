import os
import sys
import networkx as nx


def data_to_json(value, widget):
    """
    Generate a json file from the data passed to the widget
    Parameters
    ----------
    value: pysb.Model, pysb.SimulationResult, str
        Value passed to the widget that is going to be visualized
    widget: Widget
        Widget instance

    Returns
    -------

    """

    if is_pysb_model(value):
        from pyvipr.pysb_viz.static_viz import PysbStaticViz

        viz = PysbStaticViz(value)
        jsondata = static_data(viz, widget)
        return jsondata

    elif is_pysb_sim(value):
        from pyvipr.pysb_viz.dynamic_viz import PysbDynamicViz

        viz = PysbDynamicViz(value, widget.sim_idx, widget.cmap)
        jsondata = dynamic_data(viz, widget)
        return jsondata

    elif isinstance(value, str):
        file_extension = os.path.splitext(value)[1]
        if file_extension in ['.bngl', '.sbml', '.xml', '.ka'] and widget.type_of_viz != 'sbgn_xml'\
                or value.startswith('BIOMD'):
            try:
                from pysb.importers.sbml import model_from_sbml, model_from_biomodels
                from pysb.importers.bngl import model_from_bngl
            except ImportError:
                raise Exception('PySB must be installed to visualize models from files')
            from pyvipr.pysb_viz.static_viz import PysbStaticViz

            if file_extension == '.bngl':
                model = model_from_bngl(value)
            elif file_extension == '.ka':
                import subprocess
                import re
                try:
                    import truml
                    subprocess.run(['truml', '-k', value], check=True)
                except (ImportError, subprocess.CalledProcessError):
                    raise Exception('Please install the TruML package from the python3 branch:\n'
                                    'pip install git+https://github.com/LoLab-VU/TRuML@python3')
                bngl_model_path = re.sub('ka', 'bngl', value)
                model = model_from_bngl(bngl_model_path)
                os.remove(bngl_model_path)
            elif file_extension in ['.sbml', '.xml']:
                model = model_from_sbml(value)
            elif value.startswith('BIOMD'):
                model = model_from_biomodels(value)
            viz = PysbStaticViz(model)
            jsondata = static_data(viz, widget)
            return jsondata
        elif file_extension == '.graphml' or widget.type_of_viz == 'sbgn_xml':
            with open(value, 'r') as file:
                data = file.read().replace('\n', '')
            return data
        elif file_extension == '.json':
            import json
            with open(value, 'r') as file:
                data = file.read().replace('\n', '')
            jsondata = json.loads(data)
            return jsondata
        elif file_extension == '.sif':
            with open(value, 'r') as file:
                data = file.read()
            data = data.rstrip('\n')
            return data
        else:
            raise ValueError('Format not supported')

    elif is_tellurium_model(value):
        if widget.type_of_viz.startswith('dynamic'):
            from pyvipr.tellurium_viz.dynamic_viz import TelluriumDynamicViz
            viz = TelluriumDynamicViz(value, widget.cmap)
            jsondata = dynamic_data(viz, widget)
        else:
            from pyvipr.tellurium_viz.static_viz import TelluriumStaticViz
            viz = TelluriumStaticViz(value)
            jsondata = static_data(viz, widget)
        return jsondata

    elif isinstance(value, (nx.DiGraph, nx.Graph, nx.MultiDiGraph, nx.MultiGraph, dict)):
        from pyvipr.network_viz.network_viz import NetworkViz
        viz = NetworkViz(value)
        if widget.type_of_viz:
            jsondata = getattr(viz, widget.type_of_viz)()
        else:
            jsondata = value
        return jsondata

    elif is_ecell_model(value):
        try:
            from pysb.importers.sbml import model_from_sbml
        except ImportError:
            raise Exception('PySB must be installed to visualize models from files')
        from pyvipr.pysb_viz.static_viz import PysbStaticViz
        import tempfile
        ecell4 = sys.modules['ecell4']
        f_sbml = tempfile.NamedTemporaryFile(suffix='.sbml')
        # In ecell4 species don't have initial conditions as attributes. Hence, the
        # initial conditions are passed as a dictionary to the save_sbml function.
        # If no initial conditions are passed ecell4 sets the initial condition of the
        # species to 0, and PySB throws an error when the initial condition of all the species
        # are zero. For visualization purposes we then set the initial conditions to 1.
        y0 = {sp.serial(): 1 for sp in value.list_species()}
        ecell4.util.ports.save_sbml(f_sbml.name, value, y0=y0)
        model = model_from_sbml(f_sbml.name)
        viz = PysbStaticViz(model)
        jsondata = static_data(viz, widget)
        return jsondata

    elif is_pysces_model(value):
        try:
            from pysb.importers.sbml import model_from_sbml
        except ImportError:
            raise Exception('PySB must be installed to visualize models from files')
        from pyvipr.pysb_viz.static_viz import PysbStaticViz
        import tempfile
        # Note: Importing a pysces model to sbml doesn't work in python 3.7
        pysces = sys.modules['pysces']
        f_sbml = tempfile.NamedTemporaryFile(suffix='.xml')
        pysces.interface.writeMod2SBML(value, f_sbml.name)
        model = model_from_sbml(f_sbml.name)
        viz = PysbStaticViz(model)
        jsondata = static_data(viz, widget)
        return jsondata

    else:
        raise TypeError('Only pysb Model, pysb SimulationResult, tellurium Model, '
                        'PySCeS Model, and networkx graphs are supported')


def static_data(viz_obj, w):
    try:
        if w.type_of_viz in ['sp_comm_louvain_view', 'sp_comm_louvain_hierarchy_view', 'sp_comm_asyn_lpa_view']:
            rs = w.random_state
            jsondata = getattr(viz_obj, w.type_of_viz)(random_state=rs)
        else:
            jsondata = getattr(viz_obj, w.type_of_viz)()
    except AttributeError:
        raise AttributeError('Type of static visualization not defined')
    return jsondata


def dynamic_data(viz_object, w):
    process = w.process
    try:
        if w.type_of_viz == 'dynamic_sp_comm_view':
            rs = w.random_state
            jsondata = getattr(viz_object, w.type_of_viz)(random_state=rs, type_viz=process)
        else:
            jsondata = getattr(viz_object, w.type_of_viz)(type_viz=process)
    except AttributeError:
        raise AttributeError('Type of visualization not defined')
    return jsondata


def is_pysb_model(obj):
    if 'pysb.core' in sys.modules:
        return isinstance(obj, sys.modules['pysb.core'].Model)
    else:
        return False


def is_pysb_sim(obj):
    if 'pysb.simulator' in sys.modules:
        return isinstance(obj, sys.modules['pysb.simulator'].SimulationResult)
    else:
        return False


def is_tellurium_model(obj):
    if 'tellurium' in sys.modules:
        return isinstance(obj, sys.modules['tellurium'].roadrunner.extended_roadrunner.ExtendedRoadRunner)
    else:
        return False


def is_pysces_model(obj):
    if 'pysces' in sys.modules:
        return isinstance(obj, sys.modules['pysces'].PyscesModel.PysMod)
    else:
        return False


def is_ecell_model(obj):
    if 'ecell4_base' in sys.modules:
        return isinstance(obj, sys.modules['ecell4_base'].core.NetworkModel)
    else:
        return False
