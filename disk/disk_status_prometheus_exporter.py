#!/usr/bin/env python3

import argparse
import time
from prometheus_client import start_http_server, Gauge, Counter
from disk_status_prometheus_exporter_config import load_config_from_file

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", default="config.yml", help="Location of the configuration file to use")
args = parser.parse_args()

# Config
config = load_config_from_file(args.config)

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

disk_up_gauge = Gauge(
    name = 'disk_up', 
    documentation = 'Current status if the disk is connected to the system.',
    namespace=config.metrics.namespace,
    labelnames=config.metrics.labels.static_keys
).labels(*config.metrics.labels.static_values)

if __name__ == '__main__':
    start_http_server(
        port = config.server.port,
        certfile = config.server.certfile,
        keyfile = config.server.keyfile
    )

    while True:
        # Read data from devices and write metrics in the specified interval
        disk_status = 0
        try:
            data_read_count.inc()
            with open(config.status_file, 'r') as file:
                disk_status = int(file.read())
                disk_up_gauge.set(disk_status)
        except RuntimeError as re:
            print(f"failed reporting data: {re}")
            data_read_failures_count.inc()

        time.sleep(config.metrics.scrape_interval_seconds)
