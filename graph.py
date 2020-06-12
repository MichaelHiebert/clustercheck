class ClusterVertex:
    def __init__(self, name, neighbors=None):
        self.name = name
        
        if neighbors is not None:
            self.neighbors = neighbors
        else:
            self.neighbors = set()

    def connected_to(self, other_vertex):
        """
            Returns True if this vertex is connected to `other_vertex`, else False.
        """
        raise NotImplementedError

    def add_neighbor(self, other_vertex):
        """
            Add a neighbor `other_vertex` to this vertex and vice versa.
        """
        raise NotImplementedError

    def get_neighbors(self):
        """
            Returns a set of the neighbors of this vertex.
        """

    def isolate(self):
        """
            Remove all neighbors from this vertex.
        """
        raise NotImplementedError

    def json(self):
        """
            A toJSON() method.
        """
        raise NotImplementedError

    def __str__(self):
        return '{} :: {}'.format(self.name, [n.name for n in self.get_neighbors()])

    def __eq__(self, other):
        return isinstance(self, ClusterVertex) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

class ClusterGraph:
    """
        A graph of clusters
    """
    def __init__(self, vertices):
        """
            Every ClusterGraph has a set of vertices of abstract type `ClusterVertex`
        """
        self.vertices = vertices

    def add_vertex(self, vertex):
        """
            Adds a vertex to this `ClusterGraph`
        """
        raise NotImplementedError

    def get_clusters(self):
        """
            Return a list of sets of `ClusterVertex`, where each set represents a distinct cluster in this graph.
        """
        raise NotImplementedError

    def get_vertex(self, vertex_name):
        """
            Returns the vertex with the vertex_name if it exists, else False
        """
        raise NotImplementedError

class CGMetricsWrapper:
    """
        A meta-graph with two subgraphs: predicted and actual.

        We compare the nodes and edges of these two subgraphs to produce metrics.
    """

    def __init__(self, predicted=None, actual=None):
        self.predicted = predicted
        self.actual = actual

    def load_from_text_file(self, text_file_path):
        """
            Constructs a `ClusterGraph` based on text-file input from
            the binary labeler tool.
        """

        raise NotImplementedError

    def save_to_json_file(self, json_file_path):
        """
            Saves this CGMetricsWrapper to a json file.
        """
        raise NotImplementedError

    def load_from_json_file(self, json_file_path):
        """
            Constructs a `ClusterGraph` based on json-file input from the
            meta-labeler tool.
        """
        raise NotImplementedError

    def metrics(self):
        """
            Return the precision, recall, and fscore of this meta graph.
        """
        raise NotImplementedError

    def get_actual_vertex(self, vertex_name):
        return self.actual.get_vertex(vertex_name)

# * * * * * * * * * * * * * #
# NON-ABSTRACT GUI INTERFACES
# * * * * * * * * * * * * * #

def get_timestamp_string():
    from datetime import datetime
    dt = datetime.now()
    return '{}-{}-{}_{}:{}:{}'.format(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second)

import random

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
    def __init__(self, cg_metrics_wrapper):
        self.graph = cg_metrics_wrapper
        self.clusters = self.graph.actual.get_clusters()

        self.num_clusters = len(self.clusters)

        self.meta_clusters = [MetaCluster(x, self.num_clusters) for x in range(self.num_clusters)] # seen clusters

    def set_potency(self):
        pluripotent = [x for x in self.meta_clusters if x.still_potent()]
        self.potency,_ = sum([len(x.can_be) for x in pluripotent]), len(pluripotent)

    def suggest_pairing(self):
        """
            Returns a tuple of two cluster IDs if a pairing is available, else False
        """
        pluripotent = [x for x in self.meta_clusters if x.still_potent()]

        self.potency,_ = sum([len(x.can_be) for x in pluripotent]), len(pluripotent)
            
        if len(pluripotent) == 0: return False

        metacluster_one = random.choice(pluripotent)
        metacluster_two = self.meta_clusters[random.choice(list(metacluster_one.can_be))]

        return metacluster_one,metacluster_two

    def suggest_intra_pairing(self):
        """
            Returns a tuple of cluster IDs, where both are the same.
        """

        cluster = random.choice(list(self.meta_clusters))

        return cluster,cluster

    def get_node_name_from_cluster(self, meta_cluster):
        return random.choice(list(self.clusters[meta_cluster.id])).name

    def is_good_pairing(self, mc1, mc2, callback=None):
        mc1.add_is(mc2)
        mc2.add_is(mc1)

        for same in mc1.is_same:
            self.meta_clusters[same].add_is(mc2)

        for same in mc2.is_same:
            self.meta_clusters[same].add_is(mc1)

        if callback is not None:
            callback()

    def is_bad_pairing(self, mc1, mc2, callback=None):
        mc1.add_cant(mc2)
        mc2.add_cant(mc1)

        for same in mc1.is_same:
            self.meta_clusters[same].add_cant(mc2)

        for same in mc2.is_same:
            self.meta_clusters[same].add_cant(mc1)

        if callback is not None:
            callback()

    def problem_with_cluster(self, cluster, image1, image2, callback=None):
        act_cluster = self.clusters[cluster.id]

        if len(act_cluster) != 1: # if the length is one, there can be no problems
            node1 = self.graph.get_actual_vertex(image1)
            node2 = self.graph.get_actual_vertex(image2)

            act_cluster.remove(node1)
            if node2 in act_cluster: act_cluster.remove(node2) # just in case we check the same image?

            self._isolate_node_create_metacluster(node1)
            if node2 != node1: self._isolate_node_create_metacluster(node2) # just in case we check the same image?

        if callback is not None:
            callback()

    def _isolate_node_create_metacluster(self, node):
        node.isolate()

        num_clusters = len(self.meta_clusters)

        self.clusters.append(set([node]))

        for mc in self.meta_clusters:
            mc.can_be.add(num_clusters)

        self.meta_clusters.append(MetaCluster(num_clusters, num_clusters + 1))

        self._clean_meta_clusters(self)

    def _clean_meta_clusters(self, id):
        for i,c in enumerate(self.clusters):
            if len(c) == 0:
                to_rem = None
                for mc in self.meta_clusters:
                    if mc.id == i:
                        print('going to remove {}'.format(mc.id))
                        to_rem = mc

                    if i in mc.can_be: mc.can_be.remove(i)
                    if i in mc.cant_be: mc.cant_be.remove(i)
                    if i in mc.is_same: mc.is_same.remove(i)
                if to_rem is not None: self.meta_clusters.remove(mc)


    def update_graph_and_return(self):
        for metacluster in self.meta_clusters:
            idx = metacluster.id
            random_node = random.choice(self.clusters[idx])
            for same in metacluster.is_same:
                other_rand_node = random.choice(self.clusters[same])
                other_rand_node.add_neighbor(random_node)

        return self.graph

    def save(self, timestamp=None):
        if timestamp is None:
            timestamp = get_timestamp_string()
        self.graph.save_to_json_file('{}.json'.format(timestamp))