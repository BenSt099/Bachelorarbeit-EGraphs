"""This module implements an EGraph.

Classes:
    EGraph: Represents an Equality-Graph

Implementation:
    This implementation is based on egg (e-graphs-good) and the corresponding
    paper:
        title: egg: Fast and Extensible Equality Saturation
        year: 2021
        url: https://doi.org/10.1145/3434304

    The methods 'ematch', ... are based on this Google Colab notebook:
        url: https://colab.research.google.com/drive/1tNOQijJqe5tw-Pk9iqd6HHb2abC5aRid?usp=sharing

Visualisation:
    Visualising an EGraph can be done by calling egraph_to_dot() on the instance.
    It will return a string of the EGraph in DOT notation.
        url: https://graphviz.org/doc/info/lang.html
"""

from scipy.cluster.hierarchy import DisjointSet

from EClass import EClass
from ENode import ENode


class EGraph:
    """Class that represents an EGraph.

    Attributes:
        u: Union-find datastructure with EClass-IDs (See EClass.py).
        m: Dictionary with the following mapping: EClass-ID -> EClass.
        h: Dictionary with the following mapping: ENode -> E-Class-ID.
        pending: List of EClass-IDs that need to be fixed.
        is_saturated: Boolean that specifies if the EGraph is saturated or not.

    Methods:
        add_node()
        merge()
        rebuild()
        egraph_to_dot()
    """

    def __init__(self):
        """Initialises class. Takes no arguments."""
        self.u = DisjointSet()
        self.m = {}
        self.h = {}
        self.pending = []
        self.is_saturated = False

    def _add(self, enode):
        """Adds an ENode to the EGraph and returns the corresponding EClass-ID."""
        enode = self._canonicalize(enode)
        if enode.key in [key.key for key in self.h.keys()]:
            for x in self.h.keys():
                if x.key == enode.key:
                    return self.h[x]
        else:
            eclass_id = self._new_singleton_eclass(enode)
            for child in enode.arguments:
                self.m[child].parents.append((enode, eclass_id))
            self.h[enode] = eclass_id
            self.u.add(eclass_id)
            return eclass_id

    def add_node(self, ast_node):
        """Takes an AST, recursively transforms them into
        ENodes and adds them to the EGraph.
        """
        if ast_node is not None:
            if ast_node.left is not None and ast_node.right is not None:
                return self._add(
                    ENode(
                        ast_node.key, [self.add_node(ast_node.left), self.add_node(ast_node.right)]
                    )
                )
            elif ast_node.left is not None:
                return self._add(ENode(ast_node.key, [self.add_node(ast_node.left)]))
            elif ast_node.right is not None:
                return self._add(ENode(ast_node.key, [self.add_node(ast_node.right)]))
            else:
                return self._add(ENode(ast_node.key, []))

    def _new_singleton_eclass(self, enode):
        """Creates a new EClass."""
        new_eclass = EClass()
        new_eclass.nodes.append(enode)
        self.u.add(new_eclass.id)
        self.m[new_eclass.id] = new_eclass
        return new_eclass.id

    def _canonicalize(self, enode):
        """Returns the canonical ENode."""
        return ENode(enode.key, [self._find(child) for child in enode.arguments])

    def _find(self, eclass_id):
        """Searches in u to find root element of input."""
        return self.u.__getitem__(eclass_id)

    def merge(self, eclass_id1, eclass_id2):
        """Merges two EClasses in u via provided ID and returns the new root ID."""
        if self._find(eclass_id1) == self._find(eclass_id2):
            return self._find(eclass_id1)
        self.u.merge(eclass_id1, eclass_id2)
        new_id = self._find(eclass_id1)
        self.pending.append(new_id)
        return new_id

    def rebuild(self):
        """Rebuilds the EGraph by processing the pending-list."""
        for eclass in [self._find(eclass) for eclass in self.pending]:
            self._repair(eclass)
        self.pending = []

    def _repair(self, eclass_id):
        """Repairs the EGraph."""
        for parent in self.m[eclass_id].parents:
            self.h.pop(parent[0])
            pnode = self._canonicalize(parent[0])
            self.h[pnode] = self._find(parent[1])
        new_parents = []
        for parent in self.m[eclass_id].parents:
            pnode = self._canonicalize(parent[0])
            if pnode.key in [new_parent[0].key for new_parent in new_parents]:
                for new_parent in new_parents:
                    if new_parent[0].key == pnode.key:
                        self.merge(parent[1], new_parent[1])
            new_parents.append((pnode, self._find(parent[1])))
        self.m[eclass_id].parents = new_parents

    def ematch(self):
        """"""

    def equality_saturation(self):
        """"""

    def egraph_to_dot(self):
        """Returns a string of the EGraph in DOT notation."""
        dot_commands = [
            """digraph parent { 
            graph [compound=true] 
            node [fillcolor=white fontname=\"Times-Bold\" fontsize=20 
            shape=record style=\"rounded, filled\"]\n"""
        ]
        node_set = set()
        node_identifier = 0
        for subset in self.u.subsets():
            dot_commands.append(
                'subgraph "cluster-'
                + str(self._find(next(iter(subset))))
                + '" { graph [compound=true fillcolor=navajowhite '
                + 'style="dashed, rounded, filled"]\n'
            )
            for eclass_id in subset:
                for enode in self.m[eclass_id].nodes:
                    node_set.add((node_identifier, enode))
                    dot_commands.append(
                        '"'
                        + enode.key
                        + '"'
                        + '[label="<'
                        + str(node_identifier)
                        + "0> | \\"
                        + enode.key
                        + " | <"
                        + str(node_identifier)
                        + '1>"]\n'
                    )
                    node_identifier += 1
            dot_commands.append('}\n')

        for node_ident, enode in node_set:
            if enode.arguments:
                enode_arg0, enode_arg1 = enode.arguments
                dot_commands.append(
                    '"'
                    + enode.key
                    + '":'
                    + str(node_ident)
                    + '0 -> "'
                    + next(iter(self.m[enode_arg0].nodes)).key
                    + '" [lhead='
                    + '"cluster-'
                    + str(self._find(enode_arg0))
                    + '"'
                    + "]\n"
                )
                dot_commands.append(
                    '"'
                    + enode.key
                    + '":'
                    + str(node_ident)
                    + '1 -> "'
                    + next(iter(self.m[enode_arg1].nodes)).key
                    + '" [lhead='
                    + '"cluster-'
                    + str(self._find(enode_arg1))
                    + '"'
                    + "]\n"
                )
        dot_commands.append("}")
        return "".join(dot_commands)
