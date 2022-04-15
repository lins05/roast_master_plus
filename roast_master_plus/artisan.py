#!/usr/bin/env python3

import os
import calendar
from genericpath import exists
import glob
import codecs
import datetime
import json
import logging
from posixpath import splitext
import sys
import time

logger = logging.getLogger(__name__)


def encodeLocal(x):
    if x is not None:
        return codecs.unicode_escape_encode(str(x))[0].decode("utf8")  # type: ignore
    return None


def dat_file_to_artisan_json(path):
    logger.info("parsing %s", path)
    with open(path, "r") as fp:
        jdata = json.load(fp)
    return dat_json_to_artisan_json(jdata)


def find_event_time_index(times, etime):
    """Find the time index where the event (Yellow/FC/End etc.) happens"""
    # Linear search, but it's ok for small scale.
    if etime > times[-1]:
        # The end event
        return len(times) - 1
    for idx, timeval in enumerate(times):
        if etime < timeval:
            return idx - 1


def calc_events(values, etype):
    """Given the list of sampled value of air/burner, find the events"""
    ret = []
    last_val = None
    for idx, value in enumerate(values):
        if value != last_val:
            last_val = value
            event = [idx, etype, to_special_value(value)]
            # merge consecutive changes
            if ret and ret[-1][0] == idx - 1 and abs(ret[-1][2] - value) <= 1:
                ret[-1] = event
            else:
                ret.append(event)
    return ret


def to_special_value(v):
    """The weird way of representign drum/air event values in artisan"""
    return v / 10 + 1


def dat_json_to_artisan_json(data):
    try:
        res = {}  # the interpreted data set
        res["mode"] = "C"

        title = data["title"]
        # title = 'Roasted 2022-04-12 22:57:03'
        dt = datetime.datetime.strptime(title, "Roasted %Y-%m-%d %H:%M:%S")
        utc_dt = dt + datetime.timedelta(seconds=time.timezone)

        res["roastdate"] = encodeLocal(str(dt.date()))
        res["roastisodate"] = encodeLocal(str(dt.date()))
        res["roasttime"] = encodeLocal(str(dt.time()))
        res["roastepoch"] = calendar.timegm(utc_dt.utctimetuple())
        res["roasttzoffset"] = time.timezone
        res["title"] = title
        res["roastertype"] = encodeLocal("三豆客 Q20")

        bt = data["bean_temp"]
        et = data["env_temp"]
        # make et the same length as bt
        et = et[: len(bt)]
        et.extend(-1 for _ in range(len(bt) - len(et)))
        sr = 1.0
        res["samplinginterval"] = 1.0 / sr
        tx = [x / sr for x in range(len(bt))]
        res["timex"] = tx
        res["temp1"] = et
        res["temp2"] = bt

        timeindex = [-1, 0, 0, 0, 0, 0, 0, 0]
        timeindex[0] = 0
        events = data["events"]
        times = data["times"]

        labels = ["Yellow", "FC", "FCe", "SC", "SCe", "End"]
        for i in range(1, 1 + len(labels)):
            event = events.get(labels[i - 1])
            if event:
                etime = event["time"]
                idx = find_event_time_index(times, etime)
                # print(f"{i=} {event=} {idx=}")
                if idx:
                    timeindex[i] = max(min(idx, len(tx) - 1), 0)
        res["timeindex"] = timeindex

        # 0 => air, 1 => drum, 2 => damper, 3 => burner
        air_type = 0
        burner_type = 3
        burner_values = data["burner"]
        air_values = data["air"]

        burner_events = calc_events(burner_values, burner_type)
        air_events = calc_events(air_values, air_type)

        specialevents = []
        specialeventstype = []
        specialeventsvalue = []
        specialeventsStrings = []
        for idx, etype, value in burner_events + air_events:
            specialevents.append(idx)
            specialeventstype.append(etype)
            specialeventsvalue.append(value)
            specialeventsStrings.append(str(value))

        if len(specialevents) > 0:
            res["specialevents"] = specialevents
            res["specialeventstype"] = specialeventstype
            res["specialeventsvalue"] = specialeventsvalue
            res["specialeventsStrings"] = specialeventsStrings

        return res
    except Exception as e:  # pylint: disable=broad-except
        logger.exception(e)
        return {}


def dat_file_to_artisan_json_file(src, dst):
    jdata = dat_file_to_artisan_json(src)
    logger.info("writing %s", dst)
    with open(dst, "w") as fp:
        json.dump(jdata, fp)


def main():
    dat_file_to_artisan_json_file(
        "/Users/lin/Documents/new-roasts/roast_20220412_225703_优可.json",
        "/Users/lin/Documents/new-roasts/roast_20220412_225703_优可.a.json",
    )


def setup_logging(level=logging.INFO):
    kw = {
        # 'format': '[%(asctime)s][%(pathname)s]: %(message)s',
        "format": "[%(asctime)s][%(module)s]: %(message)s",
        "datefmt": "%m/%d/%Y %H:%M:%S",
        "level": level,
        "stream": sys.stdout,
    }

    logging.basicConfig(**kw)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(
        logging.WARNING
    )

def sync_mtime(src, new, inc=0):
    mtime = os.stat(src).st_mtime + inc
    os.utime(new, (mtime, mtime))

def auto_export(directory):
    os.chdir(directory)
    if not exists('artisan'):
        os.makedirs('artisan')
    template_prefixes = ['自动曲线', 'template']
    for dat_file in sorted(glob.glob('*.dat')):
        if any([dat_file.startswith(x) for x in template_prefixes]):
            logger.info('Ignoring template %s ...', dat_file)
            continue
        logger.info('Processing %s ...', dat_file)

        name = splitext(dat_file)[0]
        artisan_json_file = f'artisan/{name}.a.json'
        artisan_file = f'artisan/{name}.alog'
        # print(f'{dat_file=} {artisan_file=}')

        if exists(artisan_json_file):
            sync_mtime(dat_file, artisan_json_file)
        if exists(artisan_file):
            sync_mtime(dat_file, artisan_file, 1)

        if exists(artisan_file):
            logger.info('artisan .alog already exists')
            continue
        if exists(artisan_json_file):
            logger.info('artisan .json already exists')
            continue
        from roast_master_plus import dat
        logger.info('Parsing .dat format ...')
        dat_json = dat.json_from_dat_file(dat_file)
        with open('/tmp/dat_tmp.json', 'w') as fp:
            json.dump(dat_json, fp)
        artisan_json = dat_json_to_artisan_json(dat_json)
        logger.info('Writing artisan .json %s ...', artisan_json_file)
        with open(artisan_json_file, 'w') as fp:
            json.dump(artisan_json, fp)
        sync_mtime(dat_file, artisan_json_file)
        logger.info('Done')

if __name__ == "__main__":
    setup_logging()
    # main()
    auto_export(sys.argv[1])
