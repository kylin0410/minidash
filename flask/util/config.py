# Import build-in or 3rd-party modules
import collections.abc
import json
import os
import sys


def update(d, u):
    """
    Update nested dict structure.
    """
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def load_config(conf_data, conf_file):
    """
    Load config from file.
    """
    try:
        if not os.path.exists(conf_file):
            return
        # Just update setting when the key exists. For compatibility concern,
        # to prevent old config file overwrite new source code.
        with open(conf_file) as json_file:
            config_file = json.load(json_file)
            update(conf_data, config_file)
            # for key, value in config_file.items():
            #     if key in conf_data:
            #         conf_data[key] = value
    except Exception:
        tp, value, tb = sys.exc_info()


def save_config(conf_data, conf_file):
    """
    Save config to file.
    """
    with open(conf_file, 'w') as json_file:
        json.dump(conf_data, json_file, sort_keys=True, indent=2)
