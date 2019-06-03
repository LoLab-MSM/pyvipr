import re
from collections import OrderedDict
from pysb.bng import generate_equations
from pysb.importers.bngl import model_from_bngl
from pysb.importers.sbml import model_from_sbml, model_from_biomodels
import os
import subprocess
import tempfile
import sys


def parse_name(spec):
    """
    Function that writes short names of the species to name the nodes.
    It counts how many times a monomer_pattern is present in the complex pattern an its states
    then it takes only the monomer name and its state to write a shorter name to name the nodes.

    Parameters
    ----------
    spec : pysb.ComplexPattern
        Name of species to parse

    Returns
    -------
    Parsed name of species
    """
    m = spec.monomer_patterns
    lis_m = []
    name_counts = OrderedDict()
    parsed_name = ''
    for i in range(len(m)):
        sp_name = str(m[i]).partition('(')[0]
        sp_comp = str(m[i]).partition('** ')[-2:]
        sp_comp = ''.join(sp_comp)
        sp_states = re.findall(r"['\"](.*?)['\"]", str(m[i])) # Matches strings between quotes
        sp_states = [s.lower() for s in sp_states]
        # tmp_2 = re.findall(r"(?<=\').+(?=\')", str(m[i]))
        if not sp_states and not sp_comp:
            lis_m.append(sp_name)
        else:
            sp_states.insert(0, sp_name)
            sp_states.insert(0, sp_comp)
            sp_states.reverse()
            lis_m.append(''.join(sp_states))
    for name in lis_m:
        name_counts[name] = lis_m.count(name)

    for sp, counts in name_counts.items():
        if counts == 1:
            parsed_name += sp + '-'
        else:
            parsed_name += str(counts) + sp + '-'
    return parsed_name[:len(parsed_name) - 1]


def rate_2_interactions(model, rate):
    """
    Obtains the interacting protein from a reaction rate
    Parameters
    ----------
    model : PySB model
    rate : str
    Returns
    -------

    """

    generate_equations(model)
    species_idxs = re.findall('(?<=__s)\d+', rate)
    species_idxs = [int(i) for i in species_idxs]
    if len(species_idxs) == 1:
        interaction = parse_name(model.species[species_idxs[0]])
    else:
        sp_monomers ={sp: model.species[sp].monomer_patterns for sp in species_idxs }
        sorted_intn = sorted(sp_monomers.items(), key=lambda value: len(value[1]))
        interaction = " ".join(parse_name(model.species[mons[0]]) for mons in sorted_intn[:2])
    return interaction


def find_nonimportant_nodes(model):
    """
    This function looks a the bidirectional reactions and finds the nodes that only have one incoming and outgoing
    reaction (edge)

    Parameters
    ----------
    model : pysb.Model
        PySB model to use

    Returns
    -------
    a list of non-important nodes
    """
    if not model.odes:
        generate_equations(model)

    # gets the reactant and product species in the reactions
    rcts_sp = sum([i['reactants'] for i in model.reactions_bidirectional], ())
    pdts_sp = sum([i['products'] for i in model.reactions_bidirectional], ())
    # find the reactants and products that are only used once
    non_imp_rcts = set([x for x in range(len(model.species)) if rcts_sp.count(x) < 2])
    non_imp_pdts = set([x for x in range(len(model.species)) if pdts_sp.count(x) < 2])
    non_imp_nodes = set.intersection(non_imp_pdts, non_imp_rcts)
    passengers = non_imp_nodes
    return passengers


def dispatch_pysb_files(value):
    functions = {'str': _handle_model_files, 'pysb.core.Model': _handle_pysb_model,
                 'tellurium.roadrunner.extended_roadrunner.ExtendedRoadRunner': _handle_tellurium_model,
                 'pysces.PyscesModel.PysMod': _handle_pysces_model,
                 'ecell4_base.core.NetworkModel': _handle_ecell4_model}
    data_type = str(type(value)).split("'")[1]
    result = functions[data_type](value)
    return result


def _handle_model_files(value):
    file_extension = os.path.splitext(value)[1]
    if file_extension == '.bngl':
        model = model_from_bngl(value)
    elif file_extension == '.sbml':
        model = model_from_sbml(value)
    elif value.startswith('BIOMD'):
        model = model_from_biomodels(value)
    # elif file_extension == '.ka':
    #     subprocess.run(['truml', '-k', value])
    #     bngl_model_path = re.sub('ka', 'bngl', value)
    #     model = model_from_bngl(bngl_model_path)
    #     os.remove(bngl_model_path)

    else:
        raise ValueError('Format not supported')
    return model


def _handle_pysb_model(value):
    return value


def _handle_tellurium_model(value):
    f_sbml = tempfile.NamedTemporaryFile(suffix='.sbml')
    value.exportToSBML(f_sbml.name)
    model = model_from_sbml(f_sbml.name)
    return model


def _handle_pysces_model(value):
    # Note: Importing a pysces model to sbml doesn't work in python 3.7
    pysces = sys.modules['pysces']
    f_sbml = tempfile.NamedTemporaryFile(suffix='.sbml')
    pysces.interface.writeMod2SBML(value, f_sbml.name)
    model = model_from_sbml(f_sbml.name)
    return model


def _handle_ecell4_model(value):
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
    return model
