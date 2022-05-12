#!/usr/bin/env python3

import math
import json
import logging
import pickle
from os.path import exists

logger = logging.getLogger(__name__)


def load_dat(path):
    assert exists(path)
    with open(path, "rb") as fp:
        dat = pickle.load(fp)
    return dat

def remove_nan(xs):
    ret = []
    for x in xs:
        if math.isnan(x):
            break
        ret.append(x)
    return ret


def dat_to_json(dat):
    events = dict([[evt.name, value] for evt, value in dat.events.items()])
    data = {
        "title": dat.name,
        "times": list(dat.times),
        "bean_temp": remove_nan(list(dat.bts)),
        "env_temp": remove_nan(list(dat.ets)),
        "burner": remove_nan(list(dat.fps)),
        "air": remove_nan(list(dat.dps)),
        "events": events,
    }
    return data


def json_from_dat_file(path):
    dat = load_dat(path)
    return dat_to_json(dat)


def dat_file_to_json_file(src, dst):
    jdata = json_from_dat_file(src)
    with open(dst, "w") as fp:
        json.dump(jdata, fp)
    logger.info("Exported %s to %s", src, dst)
