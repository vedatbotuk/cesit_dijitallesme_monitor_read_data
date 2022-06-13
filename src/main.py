#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" Description """

from time import sleep
from datetime import datetime
import classes
import json
import requests
from os import path as path_exists


CONFIG_JSON = classes.get_setup()

# DEVICE_NAMES = {"IP","_ID"}
DEVICE_NAMES = {}
data_master = {}

IP_ADDRESSES = CONFIG_JSON['device_ips']
TIMEOUT = CONFIG_JSON['request_timeout']
LOOP_SLEEP = CONFIG_JSON['loop_sleep']
PATH_MASTER = CONFIG_JSON['path_data_master']

# macs = ['b8:27:eb:47:16:92', 'b8:27:eb:55:ea:75']
# IP_ADDRESSES = classes.find_ip_address_for_mac_address(macs, '192.168.1.0/24')
# exit()

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
    hhmm = ['{0:1.0f}'.format(*divmod(unix_time / 60, 60)), '{1:1.0f}'.format(*divmod(unix_time / 60, 60))]
    if hhmm[0] == '0':
        return hhmm[1] + ' dakika'
    else:
        return hhmm[0] + ' saat, ' + hhmm[1] + ' dakika'
    # return hhmm


def unix_time_to_date(unix_time):
    """ Description """
    unix_time = datetime.fromtimestamp(unix_time)
    return unix_time.strftime("%d-%b-%Y (%H:%M:%S)")


def main():
    """ Description """
    global DEVICE_NAMES, IP_ADDRESSES
    for x in IP_ADDRESSES:
        url = 'http://' + x + '/data.json'
        try:
            get_url = requests.get(url, timeout=TIMEOUT)
            get_data = json.loads(get_url.text)[0]
            device_name = get_data['_id']

            reset_time = get_data['Son Reset Tarihi']
            productive_run_time = get_data['Aktiv çalışma süresi']
            stop_time = get_data['Durma süresi']
            bobin_time = get_data['Bobin süresi']
            ariza_time = get_data['Arıza süresi']
            cozgu_time = get_data['Çözgü süresi']
            ayar_time = get_data['Ayar süresi']
            total_time = get_data['Toplam çalışma süresi']

            productivity = get_data['Verim']
            speed = get_data['Çalışma hızı']
            remainder_time = get_data['Tahmini kalan süre']

            DEVICE_NAMES.update({x: device_name})

            data_master['Devices'][device_name] = get_data

            data_master['Devices'][device_name]['Son Reset Tarihi'] = unix_time_to_date(reset_time)

            data_master['Devices'][device_name]['Aktiv çalışma süresi'] = unix_time_to_hhmm(productive_run_time)
            data_master['Devices'][device_name]['Durma süresi'] = unix_time_to_hhmm(stop_time)
            data_master['Devices'][device_name]['Bobin süresi'] = unix_time_to_hhmm(bobin_time)
            data_master['Devices'][device_name]['Arıza süresi'] = unix_time_to_hhmm(ariza_time)
            data_master['Devices'][device_name]['Çözgü süresi'] = unix_time_to_hhmm(cozgu_time)
            data_master['Devices'][device_name]['Ayar süresi'] = unix_time_to_hhmm(ayar_time)
            data_master['Devices'][device_name]['Toplam çalışma süresi'] = unix_time_to_hhmm(total_time)

            data_master['Devices'][device_name]['Verim'] = str(productivity * 100) + '%'

            try:
                data_master['Devices'][device_name]['Çalışma hızı'] = str(round(60 / speed, 1)) + ' düğüm/dakika'
            except ZeroDivisionError:
                data_master['Devices'][device_name]['Çalışma hızı'] = '0.0' + ' düğüm/dakika'
            data_master['Devices'][device_name]['Tahmini kalan süre'] = unix_time_to_hhmm(remainder_time)

            data_master['Devices'][device_name]['Status'] = 'Connected'
            data_master['Devices'][device_name]['IP-Address'] = x

        except Exception as e:
            if x in DEVICE_NAMES:
                print(e)
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
