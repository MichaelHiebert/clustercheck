from graph import ClusterFCVertex, ClusterGraph

def scenario_one():
    print('***Scenario One***')
    a1 = ClusterFCVertex('a1')
    a2 = ClusterFCVertex('a2')
    a3 = ClusterFCVertex('a3')

    b1 = ClusterFCVertex('b1')
    b2 = ClusterFCVertex('b2')
    b3 = ClusterFCVertex('b3')

    c1 = ClusterFCVertex('c1')
    c2 = ClusterFCVertex('c2')

    g = ClusterGraph(set([a1,a2,a3,b1,b2,b3,c1,c2]))

    a1.add_neighbor(a2)
    a2.add_neighbor(a3)

    a1.add_pred_neighbor(a2)
    a1.add_pred_neighbor(a3)
    a2.add_pred_neighbor(b1)

    b1.add_neighbor(b2)
    b2.add_neighbor(b3)

    b1.add_pred_neighbor(b2)
    b2.add_pred_neighbor(b3)

    c1.add_neighbor(c2)
    c1.add_pred_neighbor(c2)

    g.update()

    print(g.metrics())

def scenario_two(per_cluster=50):
    print('***Scenario Two***')
    a1 = ClusterFCVertex('a1')
    a2 = ClusterFCVertex('a2')
    a3 = ClusterFCVertex('a3')

    b1 = ClusterFCVertex('b1')
    b2 = ClusterFCVertex('b2')
    b3 = ClusterFCVertex('b3')

    c1 = ClusterFCVertex('c1')
    c2 = ClusterFCVertex('c2')

    g = ClusterGraph(set([a1,a2,a3,b1,b2,b3,c1,c2]))

    a1.add_neighbor(a2)
    a2.add_neighbor(a3)

    a1.add_pred_neighbor(a2)
    a1.add_pred_neighbor(a3)
    a2.add_pred_neighbor(b1)

    for i in range(4, per_cluster): # make c a cluster of 1000
        v = ClusterFCVertex('a{}'.format(i))
        g.add_vertex(v)
        v.add_neighbor(a1)
        v.add_pred_neighbor(c1)

    b1.add_neighbor(b2)
    b2.add_neighbor(b3)

    b1.add_pred_neighbor(b2)
    b2.add_pred_neighbor(b3)

    for i in range(4, per_cluster): # make c a cluster of 1000
        v = ClusterFCVertex('b{}'.format(i))
        g.add_vertex(v)
        v.add_neighbor(b1)
        v.add_pred_neighbor(c1)

    c1.add_neighbor(c2)
    c1.add_pred_neighbor(c2)

    for i in range(4, per_cluster): # make c a cluster of 1000
        v = ClusterFCVertex('c{}'.format(i))
        g.add_vertex(v)
        v.add_neighbor(c1)
        v.add_pred_neighbor(c1)
    
    c1.add_pred_neighbor(a1)

    g.update()

    print(g.metrics())

    print(g)

    g.save_clusters('testest')

    g.load_clusters('testest.json')

    print(g.metrics())

    print(g)

# def scenario

if __name__ == "__main__":
    # scenario_one()
    scenario_two(5)