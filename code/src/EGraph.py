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

    The methods

    - ``_ematch``
    - ``_substitute``
    - ``apply_rules``
    - ``get_eclasses``
    - ``equality_saturation``
    - ``_extract_term``

    are based on a Google Colab notebook from Zachary DeVito (accessed 2024-11-29):
        url: https://colab.research.google.com/drive/1tNOQijJqe5tw-Pk9iqd6HHb2abC5aRid?usp=sharing

Visualisation:
    Visualising an EGraph can be done by calling
    ``egraph_to_dot(self,nodesep=0.5,ranksep=0.5)``.
    It will return a string of the EGraph in DOT notation.
        url: https://graphviz.org/doc/info/lang.html
"""

from scipy.cluster.hierarchy import DisjointSet
from EClass import EClass
from ENode import ENode
import graphviz
import pathlib
import math
import uuid
import re


class EGraph:
    """Class that represents an EGraph.

    Attributes:
        - u: Union-find datastructure with EClass-IDs (See EClass.py).
        - m: Dictionary with the following mapping: EClass-ID -> EClass.
        - h: Dictionary with the following mapping: ENode -> E-Class-ID.
        - pending: List of EClass-IDs that need to be fixed.
        - is_saturated: Boolean that specifies if the EGraph is saturated or not.

    Methods:
        add_node(ast_node)
        merge(eclass_id1, eclass_id2)
        rebuild()
        apply_rule(rules)
        apply_rules(rules)
        equality_saturation(rules, etermid)
        export_egraph_to_file(filepath, extension="pdf")
        egraph_to_dot(nodesep=0.5, ranksep=0.5)

        _add(enode)
        _new_singleton_eclass(enode)
        _canonicalize(enode)
        _find(eclass_id)
        _repair(eclass_id)
        _ematch(node_pattern)
        _substitute(ast_node, environment)
        _cost_model(key)
        _extract_term(eterm_id)
        _preorder(ast_node)
    """

    def __init__(self):
        """Initialises class. Takes no arguments."""
        self.u = DisjointSet()
        self.m = {}
        self.h = {}
        self.pending = []
        self.version = 0
        self.str_repr = ""
        self.is_saturated = False

    def _add(self, enode):
        """Adds an ENode to the EGraph and returns the corresponding EClass-ID."""
        enode = self._canonicalize(enode)
        enode_args = [self._find(arg) for arg in enode.arguments]

        canonical_eclass_ids = []
        for x in self.h.keys():
            x.arguments = [self._find(arg) for arg in x.arguments]
            canonical_eclass_ids.append(x.arguments)
        if enode.key not in ("/", "*", "+", "-", "<<", ">>") and enode.key in [
            key.key for key in self.h.keys()
        ]:
            for x in self.h.keys():
                if x.key == enode.key:
                    return self.h[x]
        elif enode in self.h.keys():
            return self.h[enode]
        elif (
            enode.key in [key.key for key in self.h.keys()]
            and enode_args in canonical_eclass_ids
        ):
            for en in self.h.keys():
                en.arguments = [self._find(arg) for arg in en.arguments]
                if en.key == enode.key and en.arguments == enode.arguments:
                    return self.h[en]
        else:
            self.version += 1
            eclass_id = self._new_singleton_eclass(enode)
            for child in enode.arguments:
                self.m[child].parents.add((enode, eclass_id))
            self.h[enode] = eclass_id
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
        new_eclass.nodes.add(enode)
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
        for eclass in set([self._find(eclass) for eclass in self.pending]):
            self._repair(eclass)
        self.pending = []

    def _repair(self, eclass_id):
        """Repairs the EGraph."""
        for p_node, p_eclass in self.m[eclass_id].parents:
            # if p_node in self.h.keys():
            self.h.pop(p_node)
            p_node = self._canonicalize(p_node)
            self.h[p_node] = self._find(p_eclass)
        new_parents = set()
        for p_node, p_eclass in self.m[eclass_id].parents:
            p_node = self._canonicalize(p_node)
            if p_node.key in [new_parent[0].key for new_parent in new_parents]:
                for new_parent in new_parents:
                    if new_parent[0].key == p_node.key:
                        self.merge(p_eclass, new_parent[1])
            new_parents.add((p_node, self._find(p_eclass)))
        self.m[self._find(eclass_id)].parents = new_parents

    def _ematch(self, eclasses, node_pattern):
        """Takes a pattern and matches it to ENodes in the EGraph.

        (DISCLAIMER)
        This method is based on work of Zachary DeVito. For more information,
        please see the implementation section in the module's docstring.
        """

        def _match_in(node_pattern, eid, environment):
            def enode_matches(node_pattern, enode, environment):
                if enode.key != node_pattern.key:
                    return False, environment
                new_environment = environment
                for arg_pattern, arg_eclass_id in zip(
                    [node_pattern.left, node_pattern.right], enode.arguments
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
                if node_key not in environment:
                    environment = {**environment}
                    environment[node_key] = eid
                    return True, environment
                else:
                    return environment[node_key] is eid, environment
            else:
                for enode in eclasses[eid]:
                    matches, env_new = enode_matches(node_pattern, enode, environment)
                    if matches:
                        return True, env_new
                return False, environment

        list_of_matches = []
        for eclass_id in eclasses.keys():
            is_a_match, environment = _match_in(node_pattern, eclass_id, {})
            if is_a_match:
                list_of_matches.append((eclass_id, environment))
        return list_of_matches

    def _substitute(self, ast_node, environment):
        """Extends the EGraph with a substitution.

        (DISCLAIMER)
        This method is based on work of Zachary DeVito. For more information,
        please see the implementation section in the module's docstring.
        """
        if (
            ast_node.left is None
            and ast_node.right is None
            and not re.search("[0-9]+", ast_node.key)
        ):
            return environment[ast_node.key]
        else:
            if ast_node.left is None and ast_node.right is None:
                enode = ENode(
                    ast_node.key,
                    [],
                )
            elif ast_node.left is None:
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

    def get_eclasses(self):
        """
        Returns a dictionary with a mapping of eclasses to their enodes.

        (DISCLAIMER)
        This method is based on work of Zachary DeVito. For more information,
        please see the implementation section in the module's docstring.
        :return: dict with {eclass -> set(enode, ...)}
        """
        eclasses = {}
        eclasses_raw = set(self.m.values())
        for cl in eclasses_raw:
            eid = self._find(cl.id)
            if eid not in eclasses:
                eclasses[eid] = set(cl.nodes)
            else:
                for xx in set(cl.nodes):
                    xx.arguments = [self._find(arg) for arg in xx.arguments]
                    eclasses[eid].add(xx)

        return eclasses

    def _cost_model(self, key):
        """Returns the cost of a key (integer) based on a simple cost model."""
        costs = {"+": 1, "*": 2, "-": 1, "/": 3, "<<": 1, ">>": 1}
        if key not in costs.keys():
            return 0
        return costs[key]

    def _preorder(self, ast_node):
        """Traverses the tree (preorder) to create string representation."""
        if len(ast_node.arguments) == 2:
            self.str_repr += "(" + str(ast_node.key) + " "
            self._preorder(ast_node.arguments[0])
            self._preorder(ast_node.arguments[1])
            self.str_repr = self.str_repr.strip()
            self.str_repr += ") "
        else:
            self.str_repr += ast_node.key + " "

    def egraph_to_dot(self, nodesep=0.5, ranksep=0.5, marked_nodes = [], marked_eclasses = []):
        """Returns a string of the EGraph in DOT notation."""
        dot_commands = [
            "digraph parent { graph [compound=true, nodesep=" + str(nodesep)
            + ", ranksep=" + str(ranksep) + "]\n" + """node [fillcolor=white 
            fontname=\"Times-Bold\" fontsize=20 shape=record style=\"rounded, filled\"]\n"""
        ]
        node_set = set()
        node_identifier = 0
        for subset in self.u.subsets():
            fillcolor = 'fillcolor=\"navajowhite\"'
            ss = str(self._find(next(iter(subset))))
            if ss in marked_eclasses:
                fillcolor = 'fillcolor=\"crimson\"'
            dot_commands.append(
                'subgraph \"cluster-' + ss
                + '\" { graph [compound=true '
                + fillcolor
                + ' style="dashed, rounded, filled"]\n'
            )
            nodes_in_subset = set()

            for eclass_id in subset:
                for n in self.m[eclass_id].nodes:
                    nodes_in_subset.add(n)

            # for eclass_id in subset:
            #     for enode in self.m[eclass_id].nodes:
            for enode in nodes_in_subset:
                fillcol = ', fillcolor=\"white\"'
                differentiator = ""
                if enode.key in ("/", "*", "+", "-", "<<", ">>"):
                    differentiator = str(node_identifier)
                node_set.add(
                    (str(self._find(next(iter(subset)))), node_identifier, enode)
                )
                second_diff = enode.key
                if enode.key in ('<<', '>>'):
                    second_diff = enode.key[0] + '\\' + enode.key[1]
                if enode in marked_nodes:
                    fillcol = ', fillcolor=\"crimson\"'
                dot_commands.append(
                    '"' + enode.key + differentiator + '"'
                    + '[label="<' + str(node_identifier) + "0> | \\"
                    + second_diff + " | <" + str(node_identifier) + '1>" '
                    + fillcol + ']\n'
                )
                node_identifier += 1
            dot_commands.append("}\n")

        d = str(uuid.uuid4())
        for ecl_id, node_ident, enode in node_set:
            if enode.arguments:
                differentiator = ""
                differentiator_arg0 = ""
                differentiator_arg1 = ""
                enode_arg0, enode_arg1 = enode.arguments
                if enode.key in ("/", "*", "+", "-", "<<", ">>"):
                    differentiator = str(node_ident)

                k0 = next(iter(self.m[enode_arg0].nodes))
                k1 = next(iter(self.m[enode_arg1].nodes))

                if k0.key in ("/", "*", "+", "-", "<<", ">>",):
                    for eid, nodeid, nodeself in node_set:
                        if k0.key == nodeself.key and eid == str(
                            self._find(enode_arg0)
                        ):
                            differentiator_arg0 = str(nodeid)

                if k1.key in ("/", "*", "+", "-", "<<", ">>",):
                    for eid, nodeid, nodeself in node_set:
                        if k1.key == nodeself.key and eid == str(
                            self._find(enode_arg1)
                        ):
                            differentiator_arg1 = str(nodeid)

                if self._find(enode_arg0) == ecl_id:
                    dot_commands.append(
                        '"' + d + '" [height=0, width=0, shape=point]\n'
                        '"' + enode.key + differentiator + '":' + str(node_ident)
                        + '0 -> "' + d + '" [dir=none]\n'
                        + '"' + d + '" -> "'
                        + str(k0.key) + differentiator_arg0 + '" [lhead='
                        + '"cluster-' + str(self._find(enode_arg0)) + '"' + "]\n"
                    )
                    d = str(uuid.uuid4())
                else:
                    dot_commands.append(
                        '"' + enode.key + differentiator + '":' + str(node_ident)
                        + '0 -> "' + str(k0.key) + differentiator_arg0 + '" [lhead='
                        + '"cluster-' + str(self._find(enode_arg0)) + '"' + "]\n"
                    )

                if self._find(enode_arg1) == ecl_id:
                    dot_commands.append(
                        '"' + d + '" [height=0, width=0, shape=point]\n'
                        '"' + enode.key + differentiator + '":' + str(node_ident)
                        + '0 -> "' + d + '" [dir=none]\n'
                        + '"' + d + '" -> "'
                        + str(k1.key) + differentiator_arg1 + '" [lhead='
                        + '"cluster-' + str(self._find(enode_arg1)) + '"' + "]\n"
                    )
                    d = str(uuid.uuid4())
                else:
                    dot_commands.append(
                        '"' + enode.key + differentiator + '":' + str(node_ident)
                        + '1 -> "' + str(k1.key) + differentiator_arg1 + '" [lhead='
                        + '"cluster-' + str(self._find(enode_arg1)) + '"' + "]\n"
                    )
        dot_commands.append("}")
        return "".join(dot_commands)


def export_egraph_to_file(eg, filepath, extension="pdf"):
    """Exports the EGraph into either svg or pdf file format."""
    if (
        not pathlib.Path(pathlib.Path(filepath).parents[0]).exists()
        or not pathlib.Path(pathlib.Path(filepath).parents[0]).is_dir()
    ):
        return False, "False path."
    src = graphviz.Source(eg)
    try:
        src.render(
            filename=str(pathlib.Path(filepath).stem + ".gv"),
            directory=filepath.replace("\\", "/"),
            format=extension,
            cleanup=True,
        ).replace("\\", "/")
    except (
        ValueError
        and RuntimeError
        and graphviz.ExecutableNotFound
        and graphviz.RequiredArgumentError
        and graphviz.CalledProcessError
    ):
        return False, "Error occurred."
    return True, "Export successful to " + filepath


def equality_saturation(rules, etermid, egraph):
    """Performs equality saturation.

    (DISCLAIMER)
    This method is based on work of Zachary DeVito. For more information,
    please see the implementation section in the module's docstring.
    """
    dbg = []
    best = ""
    if not egraph.is_saturated:
        while True:
            v = egraph.version
            best = _extract_term(etermid, egraph)
            dbg.append(["Best Term: " + best, egraph.egraph_to_dot()])
            # print('BEST ', _extract_term(etermid, egraph))
            egraph, debug = apply_rules(rules, egraph)
            for x in debug:
                dbg.append(x)
            if v == egraph.version:
                break
    return egraph, dbg, best


def apply_rules(rules, egraph):
    """Apply multiple rules to the egraph.

    (DISCLAIMER)
    This method is based on work of Zachary DeVito. For more information,
    please see the implementation section in the module's docstring.
    """
    debug_info = []
    eclasses = egraph.get_eclasses()
    list_of_matches = []
    for rule in rules:
        for eclass_id, environment in egraph._ematch(eclasses, rule.expr_lhs.root_node):
            list_of_matches.append((rule, eclass_id, environment))
            debug_info.append(
                [
                    "MATCHED EClass with " + str(environment) + ".",
                    egraph.egraph_to_dot(marked_eclasses=[eclass_id]),
                ]
            )

    # print(f"VERSION {egraph.version}")
    for rule, eclass_id, environment in list_of_matches:
        new_eclass_id = egraph._substitute(rule.expr_rhs.root_node, environment)
        # if eclass_id != new_eclass_id:
        # print(f"{eclass_id} MATCHED {rule} with {environment}")

        debug_info.append(
            [
                "MERGE colored eclasses.",
                egraph.egraph_to_dot(marked_eclasses=[eclass_id, new_eclass_id]),
            ]
        )
        egraph.merge(eclass_id, new_eclass_id)
    debug_info.append(["MERGED.", egraph.egraph_to_dot()])
    debug_info.append(
        [
            "REBUILD colored eclasses.",
            egraph.egraph_to_dot(marked_eclasses=egraph.pending),
        ]
    )
    egraph.rebuild()
    debug_info.append(["EGraph was rebuilt. Done.", egraph.egraph_to_dot()])
    # print(egraph.egraph_to_dot())
    return egraph, debug_info


def _extract_term(eterm_id, egraph):
    """
    Extracts the best term from the egraph based on a simple cost model.

    (DISCLAIMER)
    This method is based on work of Zachary DeVito. For more information,
    please see the implementation section in the module's docstring.
    """
    eterm_id = egraph._find(eterm_id)
    eclasses = egraph.get_eclasses()
    has_changed = True
    costs = {eclass: (math.inf, None) for eclass in eclasses.keys()}

    def cost_for_enode(enode):
        return egraph._cost_model(enode.key) + sum(
            costs[egraph._find(eclass_id)][0] for eclass_id in enode.arguments
        )

    while has_changed:
        has_changed = False
        for eclass, enodes in eclasses.items():
            x = [(cost_for_enode(enode), enode) for enode in enodes]
            x.sort(key=lambda student: student[0])
            new_cost = min(x, key=lambda st: st[0])

            if costs[eclass][0] != new_cost[0]:
                has_changed = True
            costs[eclass] = new_cost

    def extract_best_term(eclass_id):
        enode = costs[eclass_id][1]
        return ENode(enode.key, [extract_best_term(eid) for eid in enode.arguments])

    egraph.str_repr = ""
    egraph._preorder(extract_best_term(eterm_id))
    egraph.str_repr = egraph.str_repr.strip()
    return egraph.str_repr
