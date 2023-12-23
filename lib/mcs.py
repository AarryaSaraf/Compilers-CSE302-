#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 14:06:53 2023

"""

from .ssa import *
from .tac import *
from .alloc import *


def transformer(live_outs, defs, uses, is_copy):
    """Takes the arguements and spits out the interference graph.

    Args:
        live_outs (list of list of SSATemps or TACTemps): list of live out sets
        defs (list of list of SSATemps or TACTemps)): list of def sets
        use (list of list of SSATemps or TACTemps): list of use sets
        is_copy (list of Bool): wether the instruction is a copy or not.
    """
    ans = []
    for i in range(0, len(defs)):
        interfering_temps = set()
        for x in live_outs[i]:
            interfering_temps.add(x)
            for y in defs[i]:
                interfering_temps.add(y)
            # we can't do register coalescing with this 
            # we aren't really sure why source and destination would interfere here instead of just destination...
            if is_copy[i]:
                for y in uses[i]:
                    interfering_temps.add(y)
        ans.append(interfering_temps)
    return buildIG(ans)


def buildIG(temps):
    """
    Parameters
    ----------
    temps : list[set[SSATemps]]
            in each set we have the variables which interfere with one another for 1 line
            the list just collects all such for 1 function


    Returns
    -------
    InterferenceGraph
    """
    IG = dict()
    # distinct temporaries
    distinct = {num for temp in temps for num in temp}
    # non connected graph
    for t in distinct:
        IG[t] = InterferenceGraphNode(t, [], 0)
    # time to build the connections now
    for target in distinct:
        IG[target].nbh.extend(
            list(
                set(
                    IG[i].tmp
                    for subset in temps
                    if target in subset
                    for i in subset - {target}
                )
            )
        )
    return InterferenceGraph(IG)


def mcs(igraph):
    """
    Function to return a list with the simplical elimination ordering
    using Maximum cardinality search as seen in class

    Args:
        igraph (InterferenceGraph): input who's SEO is to be found

    Returns:
        [InterferenceGraphNode]: Simplical Elimination ordering
    """
    i = all_none(igraph)
    ans = []
    while i:
        ans = update(igraph.nodes[i], ans, igraph)
        i = all_none(igraph)
    return ans


def all_none(igraph):
    """

    Parameters
    ----------
    Igraph (Interference Graph) : Checks if all nodes are visited

    Returns
    -------
    False if all are none
    Else Returns first unvisited node

    """
    for i, node in igraph.nodes.items():
        if node.value is not None:
            return i
    return False


def update(node, ans, igraph):
    """
    Used to update our coloring order for the MCS. Always chooses first instead of randomly.

    Args:
        node (InterferenceGraphNode): a node from the interference graph
        ans ([InterferenceGraphNode.tmp]): updates our MCS
        igraph (InterferenceGraph): our original graph

    """
    node.value = None
    ans.append(node.tmp)
    # update value for each neighbour
    for i in node.nbh:
        if igraph.nodes[i].value != None:
            igraph.nodes[i].value += 1
    nnode = None
    max = 0
    for i in node.nbh:
        if igraph.nodes[i].value != None and igraph.nodes[i].value > max:
            nnode = igraph.nodes[i]
            max = igraph.nodes[i].value
    if nnode == None:
        return ans
    return update(nnode, ans, igraph)
