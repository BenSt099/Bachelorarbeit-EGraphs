"""This module implements an EGraph.

Classes:
    EGraph: Represents an Equality-Graph

Implementation:
    This implementation is based on egg (e-graphs-good) and the corresponding
    paper:
        title: egg: Fast and Extensible Equality Saturation \n
        year: 2021 \n
        url: https://doi.org/10.1145/3434304

    (DISCLAIMER)
    The methods '_ematch', '_substitute', 'apply_rule', 'apply_rules' are based
    on a Google Colab notebook from Zachary DeVito (accessed 2024-11-29):
        url: https://colab.research.google.com/drive/1tNOQijJqe5tw-Pk9iqd6HHb2abC5aRid?usp=sharing

Visualisation:
    Visualising an EGraph can be done by calling egraph_to_dot() on the instance.
    It will return a string of the EGraph in DOT notation.
        url: https://graphviz.org/doc/info/lang.html
"""


from scipy.cluster.hierarchy import DisjointSet
import AbstractSyntaxTree
from EClass import EClass
from ENode import ENode
import graphviz
import pathlib
import math
import re


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

        _add(enode)
        _canonicalize(enode)
        _ematch(ast_node)
        _substitute()
        _find(eclass_id)
        _repair(eclass_id)
        _new_singleton_eclass(enode)
    """

    def __init__(self):
        """Initialises class. Takes no arguments."""
        self.u = DisjointSet()
        self.m = {}
        self.h = {}
        self.pending = []
        self.version = 0
        self.is_saturated = False

    def _add(self, enode):
        """Adds an ENode to the EGraph and returns the corresponding EClass-ID."""
        enode = self._canonicalize(enode)
        if enode.key not in ("/", "*", "+", "-", "<", ">") and enode.key in [
            key.key for key in self.h.keys()
        ]:
            for x in self.h.keys():
                if x.key == enode.key:
                    return self.h[x]
        elif enode in self.h.keys():
            return self.h[enode]
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
                        ast_node.key,
                        [self.add_node(ast_node.left), self.add_node(ast_node.right)],
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
        """Merges two EClasses in u via their IDs and returns the new root ID."""
        if self._find(eclass_id1) == self._find(eclass_id2):
            return self._find(eclass_id1)
        self.version += 1
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

    def _ematch(self, ast_node):
        """Takes a pattern and matches it to ENodes in the EGraph.

        (DISCLAIMER)
        This method is based on work of Zachary DeVito. For more information,
        please see the implementation section in the module's docstring."""

        def _match_in(node_pattern, eid, env):

            def enode_matches(node, enode, environment):
                if enode.key != node.key:
                    return False, environment
                new_environment = environment
                for arg_pattern, arg_eclass_id in zip(
                    [node.left, node.right], enode.arguments
                ):
                    matched, new_environment = _match_in(
                        arg_pattern, arg_eclass_id, new_environment
                    )
                    if not matched:
                        return False, environment
                return True, new_environment

            if (
                node_pattern.left is None
                and node_pattern.right is None
                and not re.match("[0-9]+", node_pattern.key)
            ):
                node_key = node_pattern.key
                if node_key not in env:
                    env = {**env}
                    env[node_key] = eid
                    return True, env
                else:
                    return env[node_key] is eid, env
            else:
                nodes = []
                for cl in eclasses:
                    if cl.id == eid:
                        nodes = cl.nodes
                for enode in nodes:
                    matches, env_new = enode_matches(node_pattern, enode, env)
                    if matches:
                        return True, env_new
                return False, env

        eclasses = set(self.m.values())
        list_of_matches = []
        for eclass_id in [eclass.id for eclass in eclasses]:
            is_a_match, environment = _match_in(ast_node, eclass_id, {})
            if is_a_match:
                list_of_matches.append((eclass_id, environment))
        return list_of_matches

    def _substitute(self, ast_node, environment):
        """Extends the EGraph with a substitution.

         (DISCLAIMER)
        This method is based on work of Zachary DeVito. For more information,
        please see the implementation section in the module's docstring."""
        if (
            ast_node.left is None
            and ast_node.right is None
            and not re.match("[0-9]+", ast_node.key)
        ):
            return environment[ast_node.key]
        else:
            if ast_node.left is None:
                enode = ENode(
                    ast_node.key,
                    [self._substitute(ast_node.right, environment)],
                )
            elif ast_node.right is None:
                enode = ENode(
                    ast_node.key,
                    [self._substitute(ast_node.left, environment)],
                )
            else:
                enode = ENode(
                    ast_node.key,
                    [
                        self._substitute(ast_node.left, environment),
                        self._substitute(ast_node.right, environment),
                    ],
                )
            return self._add(enode)

    def apply_rule(self, rule):
        """Apply one rule to the egraph."""
        list_of_matches = []
        for eclass_id, environment in self._ematch(rule.expr_lhs.root_node):
            list_of_matches.append((rule, eclass_id, environment))
        for rule, eclass_id, environment in list_of_matches:
            new_eclass_id = self._substitute(rule.expr_rhs.root_node, environment)
            self.merge(eclass_id, new_eclass_id)
        self.rebuild()

    def apply_rules(self, rules):
        """Apply multiple rules to the egraph."""
        list_of_matches = []
        for rule in rules:
            for eclass_id, environment in self._ematch(rule.expr_lhs.root_node):
                list_of_matches.append((rule, eclass_id, environment))
        for rule, eclass_id, environment in list_of_matches:
            new_eclass_id = self._substitute(rule.expr_rhs.root_node, environment)
            self.merge(eclass_id, new_eclass_id)
        self.rebuild()

    def _cost_model(self, key):
        """Returns the cost of a key (integer) based on a simple cost model."""
        costs = {"+": 1, "*": 2, "-": 1, "/": 3, "<": 1, ">": 1}
        if key not in costs.keys():
            return 0
        return costs[key]

    def _calculate_costs(self, eterm_id):
        """"""
        eclasses = set(self.m.values())
        has_changed = True
        costs = {eclass: (math.inf, None) for eclass in eclasses}

        def cost_for_enode(enode):
            return self._cost_model(enode.key) + sum(costs[eclass_id][0] for eclass_id in enode.arguments)

        while has_changed:
            has_changed = False
            for eclass in eclasses:
                new_cost = min((cost_for_enode(enode), enode) for enode in eclass.nodes)
                if costs[eclass][0] != new_cost[0]:
                    has_changed = True
                costs[eclass] = new_cost

        def extract_best_term(eclass_id):
            enode = costs[eclass_id][1]
            node = AbstractSyntaxTree.AbstractSyntaxTreeNode()
            if len(enode.arguments) == 2:
                node.key = enode.key
                node.left = enode.arguments[0]
                node.right = enode.arguments[1]
                extract_best_term(node.left)
                extract_best_term(node.right)
                return node
            if len(enode.arguments) == 1:
                node.left = enode.arguments[0]
                node.key = enode.key
                extract_best_term(node.left)
                return node
            else:
                node.key = enode.key
                return node
        return extract_best_term(self._find(eterm_id))

    def equality_saturation(self, rules, eclass_id):
        """Performs equality saturation."""
        while True:
            v = self.version
            best_term = self._calculate_costs(eclass_id)
            self.apply_rules(rules)
            if v == self.version:
                self.is_saturated = True
                return best_term

    def export_egraph_to_file(self, filepath, extension="pdf"):
        """Exports the EGraph into either svg or pdf file format."""
        if not pathlib.Path(pathlib.Path(filepath).parents[0]).exists() or not pathlib.Path(pathlib.Path(filepath).parents[0]).is_dir():
            return False, filepath
        egraph = self.egraph_to_dot()
        src = graphviz.Source(egraph)
        src.render(filename=pathlib.Path(filepath).stem + ".gv", directory=pathlib.Path(filepath).parents[0], format=extension)
        return True, filepath

    def egraph_to_dot(self, nodesep=0.5, ranksep=0.5):
        """Returns a string of the EGraph in DOT notation."""
        dot_commands = [
            "digraph parent { graph [compound=true, nodesep="
            + str(nodesep)
            + ", ranksep="
            + str(ranksep)
            + "]\n"
            + """node [fillcolor=white fontname=\"Times-Bold\" fontsize=20 
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
                    differentiator = ""
                    if enode.key in ("/", "*", "+", "-", "<", ">"):
                        differentiator = str(node_identifier)
                    node_set.add(
                        (str(self._find(next(iter(subset)))), node_identifier, enode)
                    )
                    dot_commands.append(
                        '"'
                        + enode.key
                        + differentiator
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
            dot_commands.append("}\n")

        for ecl_id, node_ident, enode in node_set:
            if enode.arguments:
                differentiator = ""
                differentiator_arg0 = ""
                differentiator_arg1 = ""
                enode_arg0, enode_arg1 = enode.arguments
                if enode.key in ("/", "*", "+", "-", "<", ">"):
                    differentiator = str(node_ident)
                if next(iter(self.m[enode_arg0].nodes)).key in (
                    "/",
                    "*",
                    "+",
                    "-",
                    "<",
                    ">",
                ):
                    for x, y, z in node_set:
                        if x == self.m[enode_arg0].id:
                            differentiator_arg0 = str(y)
                if next(iter(self.m[enode_arg1].nodes)).key in (
                    "/",
                    "*",
                    "+",
                    "-",
                    "<",
                    ">",
                ):
                    for x, y, z in node_set:
                        if x == self.m[enode_arg1].id:
                            differentiator_arg1 = str(y)
                dot_commands.append(
                    '"'
                    + enode.key
                    + differentiator
                    + '":'
                    + str(node_ident)
                    + '0 -> "'
                    + next(iter(self.m[enode_arg0].nodes)).key
                    + differentiator_arg0
                    + '" [lhead='
                    + '"cluster-'
                    + str(self._find(enode_arg0))
                    + '"'
                    + "]\n"
                )
                dot_commands.append(
                    '"'
                    + enode.key
                    + differentiator
                    + '":'
                    + str(node_ident)
                    + '1 -> "'
                    + next(iter(self.m[enode_arg1].nodes)).key
                    + differentiator_arg1
                    + '" [lhead='
                    + '"cluster-'
                    + str(self._find(enode_arg1))
                    + '"'
                    + "]\n"
                )
        dot_commands.append("}")
        return "".join(dot_commands)
