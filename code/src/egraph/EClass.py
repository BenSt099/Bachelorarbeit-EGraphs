import uuid


class EClass:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.nodes = list()  # nodes in that eclass
        self.parents = list()  # Tuple(ENode, eclass-id)
