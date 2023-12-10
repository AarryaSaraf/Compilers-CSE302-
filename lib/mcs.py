#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 14:06:53 2023

@author: aarrya.saraf
"""

from .ssa import *
from .tac import *
from .alloc import *

    
        
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
    #distinct temporaries
    distinct = {num for temp in temps for num in temp}
    #non connected graph 
    for t in distinct:
        IG[t] = (InterferenceGraphNode(t,[],0))    
    #time to build the connections now
    for target in distinct:
        IG[target].nbh.extend(list(set(IG[i].tmp for subset in temps if target in subset for i in subset - {target})))
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
    while (i):
        update(igraph.nodes[i], ans, igraph)
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
        
    for i in igraph.nodes.keys():
        if(igraph.nodes[i].value == None):
            continue
        return i
    return False
    
def update(node, ans, igraph):
    """
    Used to update our coloring order for the MCS. Always chooses first instead of randomly.

    Args:
        node (InterferenceGraphNode): a node from the interference graph
        ans (list[InterferenceGraphNode]): updates our MCS
        
    """
    node.value = None
    ans.append(node)
    for i in node.nbh:
        for j in igraph.nodes.keys():
            if j.tmp == i:
                igraph.nodes[j].value += 1
                break
    update(igraph(node.nbh[0]), ans)
    
