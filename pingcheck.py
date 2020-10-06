#!/usr/bin/env python
import json
import sys
from socket import gethostbyname, getfqdn, gaierror  # Supports only IPv4 :P
from time import sleep
from multiping import multi_ping
import logging

try:
    config = json.load(open('pingcheck.json'))
except FileNotFoundError:
    config = {
        "hosts": {
            "1.1.1.1": "Cloudflare DNS",
            "209.58.185.57": "Hongkong - hkg.v-speed.eu",
            "198.7.59.119": "Washington - lw.us.v-speed.eu",
            "85.17.20.97": "Amsterdam - lw.nl.v-speed.eu",
        },
        "logfile": "pingcheck.log",
        "timeout": 1,
        "loop_time": 2,
        "slow_ping": 0.5
    }
    with open('pingcheck.json', "w") as c:
        json.dump(config, c, indent=4)

# logging
logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
fileHandler = logging.FileHandler("{}".format(config['logfile']))
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)
rootLogger.setLevel(logging.DEBUG)

try:
    rootLogger.info("Started pingcheck...")
    while True:
        slowest_time = 0

        responses, no_responses = multi_ping(list(config['hosts'].keys()), timeout=config["timeout"], retry=3)

        for host, time in responses.items():

            # if ping time is to high
            if time > config["slow_ping"]:
                rounded_time = round(time, 3)
                rootLogger.warning(
                    "Slow ping to host: {} - {}, ping time: {}".format(host, config['hosts'][host], rounded_time))

            # calculate slowest ping for exact sleep time
            if time > slowest_time:
                slowest_time = time
        if len(no_responses):  # we've run into timeout value
            for nores_host in no_responses:
                rootLogger.critical("No response from host: {} - {}".format(nores_host, config['hosts'][nores_host]))

            if config["loop_time"] - config["timeout"] > 0:
                sleep(config["loop_time"] - config["timeout"])

        else:  # we keep exact loop time by substact highest ping time
            if slowest_time < config["loop_time"]:
                sleep(config["loop_time"] - slowest_time)

except KeyboardInterrupt:
    sys.exit()
