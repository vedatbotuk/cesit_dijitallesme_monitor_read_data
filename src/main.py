#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" Description """

from time import sleep
import classes
import json
import requests


CONFIG_JSON = classes.get_setup()

data_master = {
    "Devices": {}
}

ip_addresses = CONFIG_JSON['device_ips']
TIMEOUT = CONFIG_JSON['request_timeout']
LOOP_SLEEP = CONFIG_JSON['loop_sleep']

# TODO logging


def main():
    for x in ip_addresses:
        url = 'http://' + x + '/data.json'
        try:
            get_url = requests.get(url, timeout=TIMEOUT)
            get_data = json.loads(get_url.text)
            device_name = get_data['id']
            data_master['Devices'][device_name] = get_data
        except Exception as e:
            # TODO: not connected key in json
            # print(e)
            pass


def write():
    with open(CONFIG_JSON['path_data_master'], 'w') as json_file:
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
