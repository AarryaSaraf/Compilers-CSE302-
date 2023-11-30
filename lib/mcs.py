#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 14:06:53 2023

@author: aarrya.saraf
"""

from .ssa import *
from .tac import *

class MemorySlot:
    pass


@dataclass
class AllocRecord:
    stacksize: int
    mapping: Dict[TACTemp | SSATemp, MemorySlot]


@dataclass
class Register(MemorySlot):
    name: str

@dataclass
class StackSlot(MemorySlot):
    offset: int


@dataclass
class InterferenceGraphNode:
    tmp: SSATemp | TACTemp
    nbh: List[Any]
    value : Int # none if visited and the integer value if not. 
                # initially set all of them to 0 

@dataclass
class InterferenceGraph:
    nodes: List[InterferenceGraphNode]
    
    
    
    
def buildIG(temps):
    """
    Parameters
    ----------
    temps : list of sets containing SSATemps
    live in
    
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
        now = IG[target]
        now.nbh.extend(IG[i] for subset in temps if target in subset for i in subset - {target})
    return InterferenceGraph(IG.values())
    

    
    
    
def mcs(igraph):
    """
    Function to return a list with the simplical elimination ordering
    using Maximum cardinality search as seen in class
    Input : an Interference graph
    output: Simplical Elimination ordering 
    """
    i = all_none(igraph)
    ans = []
    while (i != False):
        update(igraph.nodes[i], ans)
        i = all_none(igraph)
    return ans
    
def all_none(igraph):
    """
    
    Parameters
    ----------
    Igraph : Checks if all nodes are visited

    Returns
    -------
    False if all are none
    Else Returns first unvisited node

    """
    for i in igraph.nodes:
        if i.value == None:
            continue
        return True
    return False
    
def update(node, ans):
    """
    Used to update the MCS.
    Always chooses first instead of randomly
    input is a node in the graph and 
    ans the list of answers
    """
    node.value = None
    ans.append(node)
    for i in node.nbh:
        i.value += 1
    update(node.nbh[0], ans)
    
