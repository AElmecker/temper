#!/usr/bin/env python3

import argparse
import time
from prometheus_client import start_http_server, Gauge, Counter
from temper import Temper, USBList
from prometheus_exporter_config import load_config_from_file

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", default="config.yml", help="Location of the configuration file to use")
args = parser.parse_args()

# Config
config = load_config_from_file(args.config)

def printList(prefix, list):
    text = prefix + "["
    first = True
    for item in list:
        if first:
            first = False
        else:
            text = text + ", "

        text = text + item
    print(text + "]")

printList("all keys: ", config.metrics.labels.all_keys)
printList("static keys: ", config.metrics.labels.static_keys)
printList("static values: ", config.metrics.labels.static_values)

# Metric definitions
data_read_count = Counter(
    name = 'data_read_total', 
    documentation = 'Total amount the service has tried to read data from the devices.',
    namespace=config.metrics.namespace,
    labelnames=config.metrics.labels.static_keys
).labels(*config.metrics.labels.static_values)

data_read_failures_count = Counter(
    name = 'data_read_failures_total', 
    documentation = 'Total amount of failures during reading data from the devices.',
    namespace=config.metrics.namespace,
    labelnames=config.metrics.labels.static_keys
).labels(*config.metrics.labels.static_values)

connected_devices_gauge = Gauge(
    name = 'devices_connected', 
    documentation = 'Currently connected devices data is read from.',
    namespace=config.metrics.namespace,
    labelnames=config.metrics.labels.static_keys
).labels(*config.metrics.labels.static_values)

device_sensor_thermal_gauge = Gauge(
    name = 'device_sensor_thermal_temperature', 
    documentation = 'Current temperature collected from the thermal sensor.',
    namespace=config.metrics.namespace,
    labelnames=config.metrics.labels.all_keys,
    unit='celsius'
)
device_sensor_humidity_gauge = Gauge(
    name = 'device_sensor_humidity_percent', 
    documentation = 'Current humidity in percent collected from the humidity sensor.',
    namespace=config.metrics.namespace,
    labelnames=config.metrics.labels.all_keys,
    unit='percent'
)

# data keys
data_key_internal_temperature = 'internal temperature'
data_key_internal_humidity = 'internal humidity'

def read_data_from_devices(t):
    # re-read USB list in case we have new plugged in device(s)
    usblist = USBList()
    t.usb_devices = usblist.get_usb_devices()
    return t.read()

def write_metrics(data_of_all_devices):
    connected_devices_gauge.set(len(data_of_all_devices))

    for device_data in data_of_all_devices:
        write_device_metrics(device_data)

def write_device_metrics(device_data):
    label_values = [*config.metrics.labels.static_values]

    for device_label in config.metrics.labels.device:
        data = device_data.get(device_label.key)
        if data is str:
            label_values.append(data)
        else:
            try:
                label_values.append(str(data))
            except:
                label_values.append('')

    printList("current label values:", label_values)

    if data_key_internal_temperature in device_data:
        device_sensor_thermal_gauge.labels(*label_values).set(float(device_data[data_key_internal_temperature]))

    if data_key_internal_humidity in device_data:
        device_sensor_humidity_gauge.labels(*label_values).set(float(device_data[data_key_internal_humidity]))


if __name__ == '__main__':
    t = Temper()
    start_http_server(
        port = config.server.port,
        certfile = config.server.certfile,
        keyfile = config.server.keyfile
    )

    while True:
        # Read data from devices and write metrics in the specified interval
        data_of_all_devices = None
        try:
            data_read_count.inc()
            data_of_all_devices = read_data_from_devices(t)
        except RuntimeError as re:
            print(f"failed reporting device data: {re}")
            data_read_failures_count.inc()

        if data_of_all_devices is not None:
            write_metrics(data_of_all_devices)

        time.sleep(config.metrics.scrape_interval_seconds)
