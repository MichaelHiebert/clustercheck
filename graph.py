import numpy as np

class FCVertex:
    """Fully Connected Vertex - the neighbor of my neighbor is my neighbor, ad infinitum"""

    def __init__(self, name, neighbors=None):
        self.name = name

        if neighbors is not None:
            self.neighbors = neighbors
        else:
            self.neighbors = set()

    def connected_to(self, other_vertex):
        return other_vertex in self.neighbors

    def add_neighbor(self, other_vertex):
        self.neighbors.add(other_vertex)
        other_vertex.neighbors.add(self)

    def _get_neighbors_rec(self, seen):
        seen.add(self)
        to_add = set()
        for n in self.neighbors.difference(seen):
            to_add.update(n._get_neighbors_rec(seen))

        seen.update(to_add)
        return seen

    def update(self, seen=None):
        self.neighbors = self._get_neighbors_rec(set())

        for neighbor in self.neighbors:
            if self.neighbors != neighbor.neighbors:
                neighbor.neighbors == self.neighbors.copy()
        
    def __str__(self):
        return '{} :: {}'.format(self.name, set([v.name for v in self.neighbors]))

class ClusterFCVertex(FCVertex):
    """Subtype of `FCVertex for use in evaluating clusters"""
    def __init__(self, name, neighbors=None, pred_neighbors=None):
        super(ClusterFCVertex, self).__init__(name, neighbors)

        if pred_neighbors is not None:
            self.pred_neighbors = pred_neighbors
        else:
            self.pred_neighbors = set()

    def add_pred_neighbor(self, other_vertex):
        self.pred_neighbors.add(other_vertex)
        other_vertex.pred_neighbors.add(self)

    def _get_pred_neighbors_rec(self, seen):
        seen.add(self)
        to_add = set()
        for n in self.pred_neighbors.difference(seen):
            to_add.update(n._get_pred_neighbors_rec(seen))

        seen.update(to_add)
        return seen

    def update_pred(self, seen=None):
        self.pred_neighbors = self._get_pred_neighbors_rec(set())

        for neighbor in self.pred_neighbors:
            if self.pred_neighbors != neighbor.pred_neighbors:
                neighbor.pred_neighbors == self.pred_neighbors.copy()

    def node_metrics(self):
        """
            Returns the calculated precision, recall, and fscore contribution of this specific node.

            True Postives are edges that exist in `pred` and also in `label`

            False Positives are edges that exist in `pred` but not in `label`

            True Negatives are edges not found in either, but are irrelevant anyways.

            False Negatives are edges not in `pred`, but are in `label`
        """

        tp = len(self.pred_neighbors.intersection(self.neighbors))
        fp = len(self.pred_neighbors.difference(self.neighbors))
        fn = len(self.neighbors.difference(self.pred_neighbors))

        precision = tp / (tp + fp)
        recall = tp / (tp + fn)

        fscore = 2 * (precision * recall) / (precision + recall)

        return precision, recall, fscore

class ClusterGraph:
    def __init__(self, vertices):
        self.vertices = vertices
        self.alone = set([vertex for vertex in self.vertices if len(vertex.neighbors) == 0])

    def update(self):
        for vertex in self.vertices:
            vertex.update()
            vertex.update_pred()

        self.alone = set([vertex for vertex in self.vertices if len(vertex.neighbors) == 0])

    def add_vertex(self, vertex):
        self.vertices.add(vertex)

    def to_contingency_matrix(self):
        """
            Returns this graph as a contingency matrix,
        """
        pass

    def metrics(self):
        running_metrics = np.array([0.,0.,0.])
        for vertex in self.vertices:
            running_metrics += np.array(list(vertex.node_metrics()))

        return running_metrics / len(self.vertices)

    def __str__(self):
        return '\n'.join([str(v) for v in self.vertices])


if __name__ == "__main__":
    A = FCVertex('A')
    B = FCVertex('B')
    C = FCVertex('C')
    D = FCVertex('D')
    E = FCVertex('E')
    F = FCVertex('F')
    G = FCVertex('G')
    H = FCVertex('H')

    cg = ClusterGraph(set([A,B,C,D,E,F,G,H]))

    A.add_neighbor(B)
    B.add_neighbor(C)
    C.add_neighbor(D)
    C.add_neighbor(E)
    D.add_neighbor(E)
    D.add_neighbor(F)
    G.add_neighbor(H)
    
    print(cg)
    print('***')

    cg.update()

    print(cg)
    print('***')

    G.add_neighbor(A)
    cg.update()

    print(cg)
    print('***')

