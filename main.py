import sys
import argparse
from display import Display, MetaDisplay
from supernodegraph import NodeCGMW, NodeCG
from graph import ClusterWrapper

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A cluster-dataset label-helper.')
    parser.add_argument('mode', type=str, choices=['full', 'verify', 'meta'], help='The mode of this cluster-checker. Options are "full" (manually labelling an entire dataset from scratch), "verify" (verifying the accuracy of an existing dataset and then connecting clusters together), or "meta" (only connecting existing clusters together).')
    parser.add_argument('filepath', type=str, help='relative path to a folder with only images or subfolders with only images inside (if mode is "full") or relative path to a folder of folders of images, where each subfolder represents a cluster and the images within it are nodes (if mode is "verify") or the relative path to a json file with the same structure as is generated from the first step of a "verify" run (if mode is "meta") -- see README for more details.')
    parser.add_argument('--trust', type=int, choices=range(0,101), default=100, help='An integer between 0 and 100, where a lower number means we are more likely to check ourselves on existing clusters')


    args = parser.parse_args()
    option = args.mode
    dir_name = args.filepath
    name = dir_name.split('/')[-1]

    trust = args.trust

    print(name)

    if option == 'full':
        print('Launching brand-new cluster-labeller...')
        cg = NodeCGMW()
        cg.load_from_unorganized_folder(dir_name)
        cw = ClusterWrapper(cg)

        MetaDisplay(cw, trust=trust)
        
    elif option == 'verify':
        print('Launching intra-cluster checker...')
        Display(dir_name)

        print('Launching meta-cluster checker...')
        cg = NodeCGMW()
        cg.load_from_text_file('data/{}.txt'.format(name))
        cw = ClusterWrapper(cg)

        MetaDisplay(cw, trust=trust)

        print('Metrics', cg.metrics())
    elif option == 'meta':
        print('Launching meta-cluster checker...')
        cg = NodeCGMW()
        cg.load_from_json_file(dir_name)
        cw = ClusterWrapper(cg)

        MetaDisplay(cw, trust=trust)

        print('Metrics', cg.metrics())

