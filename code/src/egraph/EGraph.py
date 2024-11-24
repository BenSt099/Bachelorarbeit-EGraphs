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

    def graphviz_representation(self):
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
