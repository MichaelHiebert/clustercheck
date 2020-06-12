# clustercheck
A simple tool for verifying precision/recall of clusters.

## Usage

The default command syntax is:

```
python main.py <COMMAND_TYPE> <DATA_DIRECTORY> (<TRUST_FACTOR>)
```

where `COMMAND_TYPE` is one of
- `full` : meaning we will first verify the correctness of the clusters and then try to connect them back together
- `meta` : meaning we will only connect existing clusters together

`DATA_DIRECTORY` is either
- (if `full`) the relative path to a folder of folders of images, where each subfolder represents a cluster and the images within it are nodes.
- (if `meta`) the relative path to a json file with the same structure as is generated from the first step of a `full` run. See [json structure](#json-structure) for more details.

`TRUST_FACTOR` is an integer between 0 and 100, where a lower number means we are more likely to check ourselves on existing clusters

## Example Usage
```
python main.py full data/test
```

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