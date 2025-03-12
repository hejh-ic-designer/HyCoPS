import pickle
import os
from pprint import pprint
from copy import deepcopy
from typing import TYPE_CHECKING, Any
import itertools
import yaml


def load_yaml(yaml_path):
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)


def parse_yaml_docs(yaml_path):
    with open(yaml_path, 'r') as f:
        docs = list(yaml.safe_load_all(f))
    return docs


def pickle_deepcopy(to_copy: Any) -> Any:
    try:
        copy = pickle.loads(pickle.dumps(to_copy, -1))
        return copy
    except:
        return deepcopy(to_copy)
