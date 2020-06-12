import sys
from display import Display, MetaDisplay
from supernodegraph import NodeCGMW, NodeCG
from graph import ClusterWrapper

if __name__ == "__main__":
    option = sys.argv[1]
    dir_name = sys.argv[2]
    name = dir_name.split('/')[-1]

    if len(sys.argv) == 4:
        trust = sys.argv[3]
    else:
        trust = 100 # default

    print(name)

    if option == 'full':
        print('Launching intra-cluster checker...')
        Display(dir_name)

        print('Launching meta-cluster checker...')
        cg = NodeCGMW()
        cg.load_from_text_file('data/{}.txt'.format(name))
        cw = ClusterWrapper(cg)

        MetaDisplay(cw, trust=trust)

        print('Metrics', cg.metrics())
    elif option == 'meta':
        cg = NodeCGMW()
        cg.load_from_json_file(dir_name)
        cw = ClusterWrapper(cg)

        MetaDisplay(cw, trust=trust)

        print('Metrics', cg.metrics())

