#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 14:06:53 2023

@author: aarrya.saraf
"""

from .ssa import *
from .tac import *
from .alloc import *

    
        
def transformer(lin, de, use, cop):
    """Takes the arguements and spits out the interference graph.

    Args:
        lin (list of list of SSATemps or TACTemps): live in
        de (list of list of SSATemps or TACTemps)): def
        use (list of list of SSATemps or TACTemps): use
        cop (list of Bool): copy or not. List of booleans
    """
    ans = []
    for i in range(0,len(de)):
        temps = set()
        for x in lin[i]:
            temps.add(x)
            for y in de[i]:
                temps.add(y)
            if(cop[i]):
                for y in use[i]:
                    temps.add(y)
        ans.append(temps)
    return buildIG(temps)
            

        
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
        ans ([InterferenceGraphNode.tmp]): updates our MCS
        igraph (InterferenceGraph): our original graph
        
    """
    node.value = None
    ans.append(node.tmp)
    #update value for each neighbour
    for i in node.nbh:
        if(igraph.nodes[i].value !=None):
            igraph.nodes[i].value+=1
    nnode = None
    max = 0
    for i in node.nbh:
        if(igraph.nodes[i].value !=None and igraph.nodes[i].value>max):
            nnode = igraph.nodes[i]
            max = igraph.nodes[i].value
    if(nnode == None):
        return ans
    return update(nnode, ans, igraph)

def remove(igraph, tmp):
    """removes a node from the graph

    Args:
        igraph (InteferenceGraph): the graph to remove the node from
        tmp (SSATemp|TACTemp): the name of the node to be removed 

    Returns:
        InterferenceGraph: New Graph without the removed node
    """
    del igraph.nodes[tmp]
    for i in list(igraph.nodes.keys()):
        node = igraph.nodes[i]
        if tmp in node.nbh:
            node.nbh.remove(tmp)
    return igraph

def adder(igraph, tmp, a, b):
    """ add a node to the graph

    Args:
        igraph (InterferenceGrpah): OG graph
        tmp (Temp): temporary to be added
        a (Temp): temporary whos neighbours it copies
        b (Temp): temporary whos neighbours it copies

    Returns:
        _type_: _description_
    """
    nei = igraph.nodes[a].nbh + igraph.nodes[b].nbh
    igraph.nodes[tmp] = InterferenceGraphNode(tmp, nei, 0)
    return igraph