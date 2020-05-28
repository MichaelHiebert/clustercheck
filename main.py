import sys
from display import Display, MetaDisplay
from graph import ClusterGraph, ClusterWrapper

if __name__ == "__main__":
    option = sys.argv[1]
    dir_name = sys.argv[2]
    name = dir_name.split('/')[-1]

    if option == 'full':
        print('Launching intra-cluster checker...')
        Display(dir_name)

        print('Launching meta-cluster checker...')
        cg = ClusterGraph(set())
        cg.load_from_text_file('data/{}'.format('test.txt'))
        cw = ClusterWrapper(cg)

        MetaDisplay(cw)

        print('Metrics', cg.metrics())
    elif option == 'meta':
        cg = ClusterGraph(set())
        cg.load_clusters(dir_name)
        cw = ClusterWrapper(cg)

        MetaDisplay(cw)

        print('Metrics', cg.metrics)

