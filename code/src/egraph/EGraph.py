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
        if enode in [key.key for key in self.h.keys()]:
            return self.h[enode]
        else:
            eclass_id = self.new_singleton_eclass(enode)
            for child in enode.arguments:
                self.m[child].parents.append((enode, eclass_id))
            self.h[enode] = eclass_id
            self.u.add(eclass_id)
            return eclass_id

    def add_node(self, node):
        if node != "":
            if node.left != "" and node.right != "":
                return self.add(
                    ENode(
                        node.key, [self.add_node(node.left), self.add_node(node.right)]
                    )
                )
            elif node.left != "":
                return self.add(ENode(node.key, [self.add_node(node.left)]))
            elif node.right != "":
                return self.add(ENode(node.key, [self.add_node(node.right)]))
            else:
                return self.add(ENode(node.key, []))

    def new_singleton_eclass(self, enode):
        s = EClass()
        s.nodes.append(enode)
        self.u.add(s)
        self.m[s.id] = s
        return s.id

    def canonicalize(self, enode):
        return ENode(enode.key, [self.find(child) for child in enode.arguments])

    def find(self, eclassid):
        return self.u.__getitem__(eclassid)

    def merge(self, id1, id2):
        if self.u.__getitem__(id1) == self.u.__getitem__(id2):
            return self.find(id1)
        self.u.merge(id1, id2)
        new_id = self.find(id1)
        self.pending.append(new_id)
        return new_id

    def rebuild(self):
        pass

    def repair(self, id1):
        pass

    def equality_saturation(self):
        pass

    def graphviz_representation(self):
        pass
