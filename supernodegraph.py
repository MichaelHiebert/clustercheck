from graph import ClusterVertex, ClusterGraph, CGMetricsWrapper
from os import listdir
from os.path import isfile, join

# Implementations of the Abstract Classes in `graph.py`

class SuperNodeCV():
    """
        A Supernode class that supports `NodeCV`
    """

    def __init__(self, neighbors=None):
        if neighbors is None:
            self.neighbors = set()
        else:
            self.neighbors = neighbors

class NodeCV(ClusterVertex):
    """
        An implementation of ClusterVertex that represents
        actual nodes in a cluster, connected to exactly one other
        node - the cluster node of the cluster it belongs to.

        There must ALWAYS be a connected supernode.
    """
    def __init__(self, name, supernode=None):
        super(NodeCV, self).__init__(name, set())

        if supernode is not None:
            self.supernode = supernode
        else:
            self.supernode = SuperNodeCV(neighbors=set([self]))


    def connected_to(self, other_vertex):
        return other_vertex in self.supernode.neighbors

    def add_neighbor(self, other_vertex):
        self.supernode.neighbors.update(other_vertex.supernode.neighbors)

        for vertex in other_vertex.supernode.neighbors:
            vertex.supernode = self.supernode

    def get_neighbors(self):
        return self.supernode.neighbors

    def isolate(self):
        self.supernode.neighbors.remove(self)
        self.supernode = SuperNodeCV(neighbors=set([self]))
    
    def json(self):
        return {
            'name': self.name,
            'neighbors': [v.name for v in self.get_neighbors()]
        }

class NodeCG(ClusterGraph):
    def __init__(self, vertices):
        self.vertices = vertices

    def add_vertex(self, vertex):
        self.vertices.add(vertex)

    def get_clusters(self):
        clusters = []

        vertices = set([vertex for vertex in self.vertices])

        while len(vertices) > 0:
            vertex = vertices.pop()
            cluster = set([vertex]).union(vertex.get_neighbors())
            clusters.append(cluster)
            vertices.difference_update(cluster)

        return clusters

    def get_vertex(self, vertex_name):
        for vertex in self.vertices:
            if vertex.name == vertex_name:
                return vertex
        return False

class NodeCGMW(CGMetricsWrapper):
    def __init__(self, predicted=None, actual=None):

        if predicted is None:
            predicted = NodeCG(set())

        if actual is None:
            actual = NodeCG(set())

        super(NodeCGMW, self).__init__(predicted=predicted, actual=actual)

    def load_from_text_file(self, text_file_path):
        with open(text_file_path, 'r') as f:
            lines = f.read().split('\n')
    
        cur_dir = ''
        incorrect_preds = []

        for line in lines:
            if len(line) == 0: continue

            if line[0] == '*': # this is a folder
                # handle the previously
                self._handle_incorrects(cur_dir, incorrect_preds)

                cur_dir = line[1:]
                incorrect_preds = []
            else: # this is an incorrect face
                incorrect_preds.append(line)

        self._handle_incorrects(cur_dir, incorrect_preds)

    def _handle_incorrects(self, cur_dir, incorrect_preds):
        if cur_dir == '': return

        all_files = set([join(cur_dir,f) for f in listdir(cur_dir) if isfile(join(cur_dir, f))])
        if len(all_files) == 0: return

        incorrect_preds = set(incorrect_preds)

        corrects = all_files.difference(incorrect_preds)

        # add corrects and cluster them
        anchor_node_pred = NodeCV(corrects.pop())
        anchor_node_actu = NodeCV(anchor_node_pred.name)
        self.actual.add_vertex(anchor_node_actu)
        self.predicted.add_vertex(anchor_node_pred)

        for correct_name in corrects:
            # predicted node
            node_pred = NodeCV(correct_name)
            node_pred.add_neighbor(anchor_node_pred)
            self.predicted.add_vertex(node_pred)

            # actual node
            node_actu = NodeCV(correct_name)
            node_actu.add_neighbor(anchor_node_actu)
            self.actual.add_vertex(node_actu)

        for incorrect_name in incorrect_preds:
            # add the actuals as being lone nodes
            bad_node_actu = NodeCV(incorrect_name)
            self.actual.add_vertex(bad_node_actu)

            # add predicted with wrong connections
            bad_node_pred = NodeCV(incorrect_name)
            bad_node_pred.add_neighbor(anchor_node_pred)
            self.predicted.add_vertex(bad_node_pred)

    def metrics(self):
        p,r,f = 0.0,0.0,0.0
        for actual_vertex in self.actual.vertices:
            predicted_vertex = self.predicted.get_vertex(actual_vertex.name)

            # add vertexwise metrics to our running scores
            p,r,f = [sum(x) for x in zip([p,r,f],self._metrics_per_vertex(actual_vertex, predicted_vertex))]

        p /= len(self.actual.vertices)
        r /= len(self.actual.vertices)
        f /= len(self.actual.vertices)

        return p,r,f

    def _metrics_per_vertex(self, actual_vertex, predicted_vertex):

        tp = len(predicted_vertex.get_neighbors().intersection(actual_vertex.get_neighbors()))
        fp = len(predicted_vertex.get_neighbors().difference(actual_vertex.get_neighbors()))
        fn = len(actual_vertex.get_neighbors().difference(predicted_vertex.get_neighbors()))

        if tp == 0: return 0,0,0

        precision = tp / (tp + fp)
        recall = tp / (tp + fn)

        fscore = 2 * (precision * recall) / (precision + recall)

        return precision, recall, fscore

    def save_to_json_file(self, json_file_path):
        import json

        json_dict = {
            'actual': self._graph_to_dict(self.actual),
            'predicted': self._graph_to_dict(self.predicted)
        }

        with open(json_file_path, 'w') as f:
            f.write(json.dumps(json_dict, indent=4))

    def _graph_to_dict(self, graph):
        # actual
        vertices = graph.vertices.copy()

        cluster_dict = dict()

        cluster_count = 0

        while len(vertices) > 0:
            vertex = vertices.pop()
            cluster = set([vertex]).union(vertex.get_neighbors())
            vertices.difference_update(cluster)
            vertex_names = [c_vertex.name for c_vertex in cluster]
            cluster_dict[cluster_count] = vertex_names
            cluster_count += 1
        
        return cluster_dict

    def load_from_json_file(self, json_file_path):
        import json

        with open(json_file_path, 'r') as f:
            json_dict = json.loads(f.read())

        self.actual = self._dict_to_graph(json_dict['actual'])
        self.predicted = self._dict_to_graph(json_dict['predicted'])

    def _dict_to_graph(self, json_dict):
        graph = NodeCG(set())
        for cluster in json_dict:
            node_names = json_dict[cluster]

            anchor_name = node_names.pop(0)
            anchor_node = NodeCV(anchor_name)
            graph.add_vertex(anchor_node)

            for node_name in node_names:
                node = NodeCV(node_name)
                node.add_neighbor(anchor_node)
                graph.add_vertex(node)
        
        return graph

            


        



