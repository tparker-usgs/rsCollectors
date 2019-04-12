#!/usr/bin/env python

# -*- coding: utf-8 -*-

# I waive copyright and related rights in the this work worldwide
# through the CC0 1.0 Universal public domain dedication.
# https://creativecommons.org/publicdomain/zero/1.0/legalcode

# Author(s):
#   Tom Parker <tparker@usgs.gov>

""" Present a consolodated event stream from messages gathered from individual
    segment_gatherer processes.
"""


import collections
import threading
import signal
import time

import zmq
from posttroll.subscriber import Subscribe
import tomputils.util as tutil
from avoviirscollector.viirs import product_key


class ClientTask(threading.Thread):
    def __init__(self, msgs):
        threading.Thread.__init__(self)
        self.msgs = msgs

    def queue_msg(self, new_msg):
        key = product_key(new_msg)
        if key in self.msgs:
            queued_data = self.msgs[key].data
            new_data = new_msg.data
            queued_data['start_time'] = min(queued_data['start_time'],
                                            new_data['start_time'])
            queued_data['start_date'] = min(queued_data['start_date'],
                                            new_data['start_date'])
            queued_data['end_time'] = max(queued_data['end_time'],
                                          new_data['end_time'])
            queued_data['dataset'] += new_data['dataset']
        else:
            self.msgs[key] = new_msg

    def run(self):
        topic = "pytroll://AVO/viirs/granule"
        with Subscribe('', topic, True) as sub:
            for new_msg in sub.recv():
                try:
                    logger.debug("received message")
                    with msgs_lock:
                        self.queue_msg(new_msg)
                except Exception as e:
                    logger.error("Exception: {}".format(e))
                    logger.error(e)


class ServerTask(threading.Thread):
    def __init__(self, msgs):
        threading.Thread.__init__(self)
        self.msgs = msgs
        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://*:19091")

    def get_message_bytes(self):
        msg = None
        while not msg:
            try:
                with msgs_lock:
                    (topic, msg) = self.msgs.popitem(last=False)
            except KeyError:
                time.sleep(1)

        return bytes(msg.encode(), 'UTF-8')

    def run(self):
        while True:
            logger.debug("waiting for request")
            request = self.socket.recv()
            logger.debug("Received request: %s" % request)
            self.socket.send(self.get_message_bytes())
            logger.debug("message sent")


def main():
    # let ctrl-c work as it should.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    global logger
    logger = tutil.setup_logging("msg_broker errors")

    global msgs_lock
    msgs_lock = threading.Lock()

    # msgs = queue.Queue()
    msgs = collections.OrderedDict()
    client = ClientTask(msgs)
    client.start()
    logger.info("client started")
    server = ServerTask(msgs)
    server.start()
    logger.info("server started")
    client.join()


if __name__ == '__main__':
    main()