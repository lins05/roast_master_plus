#!/usr/bin/env python3

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


def dat_to_json(dat):
    events = dict([[evt.name, value] for evt, value in dat.events.items()])
    data = {
        "title": dat.name,
        "times": list(dat.times),
        "bean_temp": list(dat.bts),
        "env_temp": list(dat.ets),
        "burner": list(dat.fps),
        "air": list(dat.dps),
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
