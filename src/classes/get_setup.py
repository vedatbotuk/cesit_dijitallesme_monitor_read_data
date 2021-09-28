import json


def get_setup(setup_path="/home/pi/cesit_dijitallesme_monitor_read_data/setup.json"):
    """ Description """
    with open(setup_path, 'r') as file:
        config_json = json.load(file)
        return config_json
