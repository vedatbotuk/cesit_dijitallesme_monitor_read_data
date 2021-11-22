#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" Description """

from time import sleep
import classes
import json
import requests
from os import path as path_exists


CONFIG_JSON = classes.get_setup()

# DEVICE_NAMES = {"IP","_ID"}
DEVICE_NAMES = {}
data_master = {}

ip_addresses = CONFIG_JSON['device_ips']
TIMEOUT = CONFIG_JSON['request_timeout']
LOOP_SLEEP = CONFIG_JSON['loop_sleep']
PATH_MASTER = CONFIG_JSON['path_data_master']


if path_exists.isfile(PATH_MASTER):
    try:
        data_master = json.load(open(PATH_MASTER, 'r'))
    except Exception as e:
        data_master = {
            "Devices": {}
        }

else:
    data_master = {
        "Devices": {}
    }

# TODO logging


def unix_time_to_hhmm(unix_time):
    """ Description """
    return '{0:02.0f}:{1:02.0f}'.format(*divmod(unix_time / 60, 60))


def unix_time_to_date(unix_time):
    """ Description """
    return unix_time.strftime("%d-%b-%Y (%H:%M:%S)")


def main():
    """ Description """
    global DEVICE_NAMES
    for x in ip_addresses:
        url = 'http://' + x + '/data.json'
        try:
            get_url = requests.get(url, timeout=TIMEOUT)
            get_data = json.loads(get_url.text)[0]
            device_name = get_data['_id']

            reset_time = get_data['Son Reset Tarihi']
            run_time = get_data['Çalışma süresi']
            speed = get_data['Çalışma hızı']
            remainder_time = get_data['Tahmini kalan süre']

            DEVICE_NAMES.update({x: device_name})

            data_master['Devices'][device_name] = get_data

            data_master['Devices'][device_name]['Son Reset Tarihi'] = unix_time_to_date(reset_time)
            data_master['Devices'][device_name]['Çalışma süresi'] = unix_time_to_hhmm(run_time)
            data_master['Devices'][device_name]['Çalışma hızı'] = str(round(speed * 60, 1)) + ' düğüm/dakika'
            data_master['Devices'][device_name]['Tahmini kalan süre'] = unix_time_to_hhmm(remainder_time)

            data_master['Devices'][device_name]['Status'] = 'Connected'
            data_master['Devices'][device_name]['IP-Address'] = x

        except Exception as e:
            if x in DEVICE_NAMES:
                data_master['Devices'][DEVICE_NAMES[x]]['Status'] = 'Not connected'


def write():
    with open(PATH_MASTER, 'w') as json_file:
        json.dump(data_master, json_file)


def loop():
    while True:
        main()
        write()
        sleep(LOOP_SLEEP)


if __name__ == '__main__':
    try:
        loop()

    except (KeyboardInterrupt, SystemExit):
        print('keyboard interrupt detected')
