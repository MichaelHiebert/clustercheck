import numpy as np
from os import listdir
from os.path import isfile, join
import random
import json

from display import MetaDisplay

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

        if tp == 0: return 0,0,0

        precision = tp / (tp + fp)
        recall = tp / (tp + fn)

        fscore = 2 * (precision * recall) / (precision + recall)

        return precision, recall, fscore

    def json(self):
        """
            Returns this node in json form
        """

        pred_neighbor_list = [x.name for x in self.pred_neighbors]

        return {
            'name': self.name,
            'pred_neighbors': pred_neighbor_list
        }

    # def copy(self, source=True):
    #     """
    #         The graph NEEDS to be updated after a full-copy
    #     """
    #     preds = set([ClusterFCVertex(n.name) for n in self.pred_neighbors])
    #     reals = set([ClusterFCVertex(n.name) for n in self.neighbors])
    #     return ClusterFCVertex(self.name, neighbors=reals, pred_neighbors=preds)

    def __str__(self):
        return super().__str__() + ' :: {}'.format(set([v.name for v in self.pred_neighbors]))

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
        if vertex.name not in [n.name for n in self.vertices]:
            self.vertices.add(vertex)
        else:
            raise Exception('Duplicate IDs not allowed')

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

    def load_from_text_file(self, filepath):
        """
            Given a filepath to a text file with the FORMAT FROM THE BINARY LABELER,
            ingest it into this graph.
        """

        with open(filepath, 'r') as f:
            lines = f.read().split('\n')

        cur_dir = ''
        incorrect_faces = []

        for line in lines:
            if len(line) == 0: continue

            if line[0] == '*': # this is a folder
                # handle the previously
                self._handle_incorrects(cur_dir, incorrect_faces)

                cur_dir = line[1:]
                incorrect_faces = []
            else: # this is an incorrect face
                incorrect_faces.append(line)

        self._handle_incorrects(cur_dir, incorrect_faces)

        self.update()

    def _handle_incorrects(self, cur_dir, incorrect_faces):
        if cur_dir == '': return

        all_files = set([join(cur_dir,f) for f in listdir(cur_dir) if isfile(join(cur_dir, f))])
        if len(all_files) == 0: return

        incorrect_faces = set(incorrect_faces)

        corrects = all_files.difference(incorrect_faces)

        # add corrects and cluster them
        anchor_node = ClusterFCVertex(corrects.pop())
        self.add_vertex(anchor_node)

        for correct_name in corrects:
            node = ClusterFCVertex(correct_name)
            node.add_neighbor(anchor_node) # ground truth
            node.add_pred_neighbor(anchor_node)
            self.add_vertex(node)

        for incorrect_name in incorrect_faces:
            bad_node = ClusterFCVertex(incorrect_name)
            bad_node.add_pred_neighbor(anchor_node)
            self.add_vertex(bad_node)

    def load_clusters(self, filename):
        """
            load from a json file with clusters
        """
        node_dict = dict()

        self.vertices = set()
        self.alone = set()

        with open(filename) as f:
            j = json.loads(f.read())

        clusters = j['clusters']

        pred_neighs = []

        # load the ground truth
        for cluster in clusters:
            cluster = cluster['cluster']
            node_names = [n['name'] for n in cluster]
            node_neigh = [n['pred_neighbors'] for n in cluster]

            pred_neighs.extend(node_neigh)

            nodes = [ClusterFCVertex(name) for name in node_names]

            for node in nodes:
                node_dict[node.name] = node

            while len(nodes) > 0:
                node = nodes.pop(0)
                for other_node in nodes:
                    node.add_neighbor(other_node)

                self.add_vertex(node)

        for pred_neigh in pred_neighs:
            first = node_dict[pred_neigh.pop(0)]

            while len(pred_neigh) > 0:
                node_name = pred_neigh.pop(0)
                node_dict[node_name].add_pred_neighbor(first)
        self.update()

        vertex = list(self.vertices)[0]

    def _get_vertex(self, name):
        for vertex in list(self.vertices):
            if vertex.name == name: return vertex

        return None


    def get_current_true_clusters(self):
        bank = self.vertices.copy()

        clusters = []

        while len(bank) > 0:
            cluster_anchor = bank.pop()
            cluster = cluster_anchor.neighbors
            clusters.append(cluster)
            bank = bank.difference(cluster)

        return clusters

    def save_clusters(self, path):
        """
            Save to json
        """
        clusters = self.get_current_true_clusters()

        json_clusters = [
            { 'id': i, 'cluster': [node.json() for node in cluster] } for i, cluster in enumerate(clusters)
        ]

        json_dict = {
            'clusters': json_clusters
        }

        if path[-5] != '.json':
            path += '.json'

        with open(path, 'w') as f:
            f.write(json.dumps(json_dict, indent=4))

    def __str__(self):
        return '\n'.join([str(v) for v in self.vertices])

class MetaCluster:
    def __init__(self, id, num_clusters):
        self.id = id
        self.is_same = set([id])
        self.can_be = set([i for i in range(num_clusters)]).difference(self.is_same)
        self.cant_be = set()

    def add_cant(self, cluster):
        idx = cluster.id
        self.cant_be.update(cluster.is_same)
        self.can_be.difference_update(self.cant_be)

    def add_is(self, cluster):
        idx = cluster.id
        self.is_same.update(cluster.is_same)
        self.cant_be.update(cluster.cant_be)
        self.can_be.difference_update(self.cant_be.union(self.is_same))

    def still_potent(self):
        return len(self.can_be) > 0

class ClusterWrapper:
    def __init__(self, cluster_graph):
        self.graph = cluster_graph
        self.clusters = self.graph.get_current_true_clusters()


        self.num_clusters = len(self.clusters)

        self.meta_clusters = [MetaCluster(x, self.num_clusters) for x in range(self.num_clusters)] # seen clusters

    def suggest_pairing(self):
        """
            Returns a tuple of two filepaths if a pairing is available, else False
        """
        pluripotent = [x for x in self.meta_clusters if x.still_potent()]

        self.potency = sum([len(x.can_be) for x in pluripotent]), len(pluripotent)
            
        if len(pluripotent) == 0: return False

        cluster_one = random.choice(pluripotent)
        cluster_two = self.meta_clusters[random.choice(list(cluster_one.can_be))]

        return cluster_one,cluster_two

    def get_node_name_from_cluster(self, cluster):
        return random.choice(list(self.clusters[cluster.id])).name

    def is_good_pairing(self, c1, c2, callback=None):
        c1.add_is(c2)
        c2.add_is(c1)

        for same in c1.is_same:
            self.meta_clusters[same].add_is(c2)

        for same in c2.is_same:
            self.meta_clusters[same].add_is(c1)

        if callback is not None:
            callback()

    def is_bad_pairing(self, c1, c2, callback=None):
        c1.add_cant(c2)
        c2.add_cant(c1)

        for same in c1.is_same:
            self.meta_clusters[same].add_cant(c2)

        for same in c2.is_same:
            self.meta_clusters[same].add_cant(c1)


        if callback is not None:
            callback()

    def update_graph_and_return(self):
        for cluster in self.meta_clusters:
            idx = cluster.id
            random_node = random.choice(self.clusters[idx])
            for same in cluster.is_same:
                other_rand_node = random.choice(self.clusters[same])
                other_rand_node.add_neighbor(random_node)

        self.graph.update()

        return self.graph
                

if __name__ == "__main__":
    cg = ClusterGraph(set())

    cg.load_from_text_file('data/test.txt')
    cg.save_clusters('testtest')

    cg = ClusterGraph(set())

    cg.load_clusters('testtest.json')

    # print(vertex.pred_neighbors)

    # print(len(cg.get_current_true_clusters()))

    # m = MetaDisplay(ClusterWrapper(cg))

