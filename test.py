from supernodegraph import NodeCV, NodeCG, NodeCGMW
import time

def scenario_one():
    print('***Scenario One***')

    actual_a1 = NodeCV('a1')
    predic_a1 = NodeCV('a1')
    actual_a2 = NodeCV('a2')
    predic_a2 = NodeCV('a2')
    actual_a3 = NodeCV('a3')
    predic_a3 = NodeCV('a3')

    actual_b1 = NodeCV('b1')
    predic_b1 = NodeCV('b1')
    actual_b2 = NodeCV('b2')
    predic_b2 = NodeCV('b2')
    actual_b3 = NodeCV('b3')
    predic_b3 = NodeCV('b3')

    actual_c1 = NodeCV('c1')
    predic_c1 = NodeCV('c1')
    actual_c2 = NodeCV('c2')
    predic_c2 = NodeCV('c2')

    actual = NodeCG(set([
        actual_a1,
        actual_a2,
        actual_a3,
        actual_b1,
        actual_b2,
        actual_b3,
        actual_c1,
        actual_c2
    ]))

    predicted = NodeCG(set([
        predic_a1,
        predic_a2,
        predic_a3,
        predic_b1,
        predic_b2,
        predic_b3,
        predic_c1,
        predic_c2
    ]))

    actual_a1.add_neighbor(actual_a2)
    actual_a2.add_neighbor(actual_a3)

    predic_a1.add_neighbor(predic_a2)
    predic_a1.add_neighbor(predic_a3)
    predic_a2.add_neighbor(predic_b1)

    actual_b1.add_neighbor(actual_b2)
    actual_b2.add_neighbor(actual_b3)

    predic_b1.add_neighbor(predic_b2)
    predic_b2.add_neighbor(predic_b3)

    actual_c1.add_neighbor(actual_c2)
    predic_c1.add_neighbor(predic_c2)

    cgmw = NodeCGMW(predicted=predicted, actual=actual)

    print('Expected', '(0.625, 1.0, 0.75)')
    print('Got     ', cgmw.metrics())

def scenario_two(per_cluster=50):
    print('***Scenario Two***')
    start = time.time()

    actual_a1 = NodeCV('a1')
    predic_a1 = NodeCV('a1')
    actual_a2 = NodeCV('a2')
    predic_a2 = NodeCV('a2')
    actual_a3 = NodeCV('a3')
    predic_a3 = NodeCV('a3')

    actual_b1 = NodeCV('b1')
    predic_b1 = NodeCV('b1')
    actual_b2 = NodeCV('b2')
    predic_b2 = NodeCV('b2')
    actual_b3 = NodeCV('b3')
    predic_b3 = NodeCV('b3')

    actual_c1 = NodeCV('c1')
    predic_c1 = NodeCV('c1')
    actual_c2 = NodeCV('c2')
    predic_c2 = NodeCV('c2')

    actual = NodeCG(set([
        actual_a1,
        actual_a2,
        actual_a3,
        actual_b1,
        actual_b2,
        actual_b3,
        actual_c1,
        actual_c2
    ]))

    predicted = NodeCG(set([
        predic_a1,
        predic_a2,
        predic_a3,
        predic_b1,
        predic_b2,
        predic_b3,
        predic_c1,
        predic_c2
    ]))

    actual_a1.add_neighbor(actual_a2)
    actual_a2.add_neighbor(actual_a3)

    predic_a1.add_neighbor(predic_a2)
    predic_a1.add_neighbor(predic_a3)
    predic_a2.add_neighbor(predic_b1)

    for i in range(4, per_cluster): # make a a cluster of 1000
        pv = NodeCV('a{}'.format(i))
        av = NodeCV('a{}'.format(i))
        actual.add_vertex(av)
        predicted.add_vertex(pv)
        av.add_neighbor(actual_a1)
        pv.add_neighbor(predic_c1)

    actual_b1.add_neighbor(actual_b2)
    actual_b2.add_neighbor(actual_b3)

    predic_b1.add_neighbor(predic_b2)
    predic_b2.add_neighbor(predic_b3)

    for i in range(4, per_cluster): # make b a cluster of 1000
        pv = NodeCV('b{}'.format(i))
        av = NodeCV('b{}'.format(i))
        actual.add_vertex(av)
        predicted.add_vertex(pv)
        av.add_neighbor(actual_b1)
        pv.add_neighbor(predic_c1)

    actual_c1.add_neighbor(actual_c2)
    predic_c1.add_neighbor(predic_c1)

    for i in range(4, per_cluster): # make c a cluster of 1000
        pv = NodeCV('c{}'.format(i))
        av = NodeCV('c{}'.format(i))
        actual.add_vertex(av)
        predicted.add_vertex(pv)
        av.add_neighbor(actual_c1)
        pv.add_neighbor(predic_c1)
    
    # c1.add_pred_neighbor(a1)

    predic_c1.add_neighbor(predic_a1)

    init_checkpoint = time.time() - start

    print('Graph initialized in {}s'.format(init_checkpoint))


    cgmw = NodeCGMW(predicted=predicted, actual=actual)

    metrics = cgmw.metrics()
    end = time.time()
    print('Got metrics in {}s'.format(end - start - init_checkpoint))

    print('Expected', '<NA>')
    print('Got     ', metrics)


    # cgmw.save_to_json_file('testest.json')

    # cgmw.load_from_json_file('testest.json')

    # print(cgmw.metrics())

    # print(g)

# def scenario

if __name__ == "__main__":
    
    scenario_one()

    print('\n')
    
    # for num_nodes in [100, 1000, 3000, 5000, 10_000]:
    # for num_nodes in [20_000]:
    for num_nodes in [1000]:
        print('Scenario Two executed for ~{} nodes'.format(3 * num_nodes))
        scenario_two(num_nodes)
        print('\n')
