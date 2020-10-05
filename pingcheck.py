#!/usr/bin/python3
import json
import sys
from socket import gethostbyname, getfqdn, gaierror  # Supports only IPv4 :P
from time import sleep
from multiping import multi_ping
import logging


config = json.load(open('pingcheck.json'))
localhost = getfqdn()

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()

fileHandler = logging.FileHandler("{}".format(config['logfile']))
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)
rootLogger.setLevel(logging.DEBUG)


hosts = {}
for host in config['hosts']:
    try:
        hosts[gethostbyname(host)] = {
            "name": host
        }

    except gaierror as e:
        print(e)
        print("FATAL: Couldn't resolve {} to IP.". format(host))
        sys.exit(-1)

try:
    while True:
        slowest_time = 0

        responses, no_responses = multi_ping(config['hosts'], config["timeout"], 0)

        for host, time in responses.items():

            # if ping time is to high
            if time > config["slow_ping"]:
                rounded_time = round(time, 3)
                rootLogger.info("Slow ping to host: {}, ping time: {}".format(hosts[host]["name"], rounded_time))

            # calculate slowest ping for exact sleep time
            if time > slowest_time:
                slowest_time = time

        if len(no_responses):  # we've run into timeout value
            for nores_host in no_responses:
                rootLogger.info("No response from host: {}".format(hosts[nores_host]["name"]))

            if config["loop_time"] - config["timeout"] > 0:
                sleep(config["loop_time"] - config["timeout"])

        else:  # we keep exact loop time by substact highest ping time
            sleep(config["loop_time"] - slowest_time)

except KeyboardInterrupt:
    sys.exit()
