from graphviz import Digraph
from scipy.cluster.hierarchy import DisjointSet

from EClass import EClass
from ENode import ENode


class EGraph:
    def __init__(self):
        self.u = DisjointSet()  # eclassid
        self.m = dict()  # eclass-id -> EClass
        self.h = dict()  # ENode -> eclassid
        self.pending = list()
        self.is_saturated = False

    def add(self, enode):
        enode = self.canonicalize(enode)
        if enode.key in [key.key for key in self.h.keys()]:
            for x in self.h.keys():
                if x.key == enode.key:
                    return self.h[x]
        else:
            eclass_id = self.new_singleton_eclass(enode)
            for child in enode.arguments:
                self.m[child].parents.append((enode, eclass_id))
            self.h[enode] = eclass_id
            self.u.add(eclass_id)
            return eclass_id

    def add_node(self, node):
        if node is not None:
            if node.left is not None and node.right is not None:
                return self.add(
                    ENode(
                        node.key, [self.add_node(node.left), self.add_node(node.right)]
                    )
                )
            elif node.left is not None:
                return self.add(ENode(node.key, [self.add_node(node.left)]))
            elif node.right is not None:
                return self.add(ENode(node.key, [self.add_node(node.right)]))
            else:
                return self.add(ENode(node.key, []))

    def new_singleton_eclass(self, enode):
        s = EClass()
        s.nodes.append(enode)
        self.u.add(s.id)
        self.m[s.id] = s
        return s.id

    def canonicalize(self, enode):
        return ENode(enode.key, [self.find(child) for child in enode.arguments])

    def find(self, eclassid):
        return self.u.__getitem__(eclassid)

    def merge(self, id1, id2):
        if self.find(id1) == self.find(id2):
            return self.find(id1)
        self.u.merge(id1, id2)
        new_id = self.find(id1)
        self.pending.append(new_id)
        return new_id

    def rebuild(self):
        todo = [self.find(eclass) for eclass in self.pending]
        self.pending = list()
        for eclass in todo:
            self.repair(eclass)
        self.is_saturated = True

    def repair(self, id1):
        for item in self.m[id1].parents:
            self.h.pop(item[0])
            pnode = self.canonicalize(item[0])
            self.h[pnode] = self.find(item[1])
        new_parents = []
        for item in self.m[id1].parents:
            pnode = self.canonicalize(item[0])
            if pnode.key in [s[0].key for s in new_parents]:
                for x in new_parents:
                    if x[0].key == pnode.key:
                        self.merge(item[1], x[1])
            new_parents.append((pnode, self.find(item[1])))
        self.m[id1].parents = new_parents

    def ematch(self):
        pass

    def equality_saturation(self):
        pass

    def _old_graphviz_representation(self):
        graph = Digraph(
            name="parent",
            format="svg",
            node_attr={"shape": "polygon"},
            directory="graphviz-output",
            graph_attr=dict(compound="true"),
        )
        node_set = set()
        for subset in self.u.subsets():
            eclass_id = self.u.__getitem__(next(iter(subset)))
            sg = Digraph(
                name="cluster-" + str(eclass_id),
                graph_attr=dict(
                    compound="true",
                    style="dashed, rounded, filled",
                    fillcolor="navajowhite",
                ),
            )
            for ss in subset:
                cl = self.m[ss]
                for x in cl.nodes:
                    node_set.add(x)
                    sg.node(
                        name=x.key,
                        shape="square",
                        style="rounded, filled",
                        fontname="Times-Bold",
                        fontsize="20",
                        fillcolor="white",
                    )
            graph.subgraph(sg)
        for node in node_set:
            for x in node.arguments:
                k = "cluster-" + str(self.find(x))
                rand_node = next(iter(self.m[x].nodes))
                graph.edge(node.key, rand_node.key, lhead=k)
        # graph.render()
        return graph.pipe()

    def level_sort(self):
        subsets = self.u.subsets()
        root_sets = []
        for subset in subsets:
            if not self.m[next(iter(subset))].parents:
                root_sets.append(subset)
        # - roots found

        tree_lists = []  # tuple(height, tree)
        level_sort_set_list = []

        for root_set in root_sets:
            height = 0
            level_list = []
            current_level = list(root_set)
            while current_level:
                level_list.append(current_level)
                height += 1
                e_classes = []
                for class_id in current_level:
                    e_classes += self.m[class_id]
                current_level = []
                for e_class in e_classes:
                    for node in e_class.nodes:
                        for arg in node.arguments:
                            current_level.append(arg)

            tree_lists.append((height, level_list))

        tree_lists.sort(key=lambda item: item[0], reverse=True)

        longest_tree = tree_lists.pop(0)  # tuple(height, tree)
        longest_tree[1].reverse()

        for i in range(longest_tree[0]):  # initialize
            level_sort_set_list.append(set(longest_tree[1][i]))

        for tree in tree_lists:
            tree[1].reverse()
            for i in range(tree[0]):
                level_sort_set_list[i].add(tree[1][i])
        return level_sort_set_list

    def graphviz_representation(self):
        commands = [
            """digraph parent {
	            graph [compound=true, rankdir=TB]
	            node [shape=polygon]\n"""
        ]
        node_set = set()
        i = 0
        for subset in self.u.subsets():
            eclass_id = self.u.__getitem__(next(iter(subset)))

            commands.append(
                'subgraph "cluster-'
                + str(eclass_id)
                + '" '
                + """
            {
		    graph [compound=true fillcolor=navajowhite style="dashed, rounded, filled"]
            """
            )

            for ss in subset:
                cl = self.m[ss]
                for x in cl.nodes:
                    node_set.add((i, x))
                    commands.append(
                        '"'
                        + x.key
                        + '"'
                        + ' [label=" <'
                        + str(i)
                        + "0> |"
                        + x.key
                        + "| <"
                        + str(i)
                        + '1> ",fillcolor=white fontname="Times-Bold" fontsize=20 shape=record style="rounded, filled"]\n'
                    )
                    i += 1
            commands.append("}\n")

        for num, node in node_set:
            if node.arguments:
                x0, x1 = node.arguments
                k0 = '"cluster-' + str(self.find(x0)) + '"'
                k1 = '"cluster-' + str(self.find(x1)) + '"'
                rand_node0 = next(iter(self.m[x0].nodes))
                rand_node1 = next(iter(self.m[x1].nodes))
                commands.append(
                    '"'
                    + node.key
                    + '":'
                    + str(num)
                    + '0 -> "'
                    + rand_node0.key
                    + '" [lhead='
                    + k0
                    + "]\n"
                )
                commands.append(
                    '"'
                    + node.key
                    + '":'
                    + str(num)
                    + '1 -> "'
                    + rand_node1.key
                    + '" [lhead='
                    + k1
                    + "]\n"
                )

        commands.append("}")
        return "".join(commands)
