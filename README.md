# clustercheck
A simple tool for verifying precision/recall of clusters.

## Setup
```
conda env create -f environment.yml
conda activate clustercheck
```

## Usage

The default command syntax is:

```
python main.py <COMMAND_TYPE> <DATA_DIRECTORY> (<TRUST_FACTOR>)
```

where `COMMAND_TYPE` is one of
- `verify` : meaning we will first verify the correctness of the clusters and then try to connect them back together
- `meta` : meaning we will only connect existing clusters together

`DATA_DIRECTORY` is either
- (if `verify`) the relative path to a folder of folders of images, where each subfolder represents a cluster and the images within it are nodes.
- (if `meta`) the relative path to a json file with the same structure as is generated from the first step of a `verify` run. See [json structure](#json-structure) for more details.

`TRUST_FACTOR` is an integer between 0 and 100, where a lower number means we are more likely to check ourselves on existing clusters

## Example Usage
```
python main.py verify data/test
```

## Cluster Potency

At the onset of any uncertain clustering, there are a number of different states that the graph (and each of its nodes) could be in. Until it has been hand checked, our clustering could _evolve_ into any one of a number of different ground-truth clusterings. I've taken this concept and called it graph [potency](https://en.wikipedia.org/wiki/Cell_potency), after a similar property possessed by stem cells.

Potency is calculated by determining how many other existing clusters a specific cluster _could_ be, and graph potency is just the cluster-wise sum of this value.

A brief example:
```
Clusters
--------
A (could be B, C)
B (could be A, C)
C (could be A, B)
```

In this example above, the graph has potency `2 + 2 + 2 = 6`. Now, if we manually determine that `A != B`, we get:
```
Clusters
--------
A (could be C)
B (could be C)
C (could be A, B)
```
to arrive at potency `1 + 1 + 2 = 4`.

Potency is simply a helpful guage of how far along a graph is to being completely verified. The lower the potency, the more complete it is.

## JSON Structure
```
{
    'actual': {
        0: [
            'node_name',
            'node_name',
             ...
            'node_name'
        ],
        ...
        N: [
            'node_name',
             ...
        ]
    },

    'predicted': {
        0: [
            ...
        ],
        ...
    }
}
```