#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
To use this code in your program:

import Pyro4

hub = Pyro4.Proxy('PYRONAME:central.hub')

# For example in the rain sensor program:
hub.report_in('rain_sensor')
"""
import argparse
import threading
import time
import Pyro4

Pyro4.config.REQUIRE_EXPOSE = True

class CentralHub(object):
    """
    Central hub object.

    This is exposed through Pyro and monitors the status of the
    individual helper processes running.
    """

    def __init__(self):
        self._ntimes = {'rain_sensor': 10,
                        'alcor': 10,
                        'microphones': 10,
                        'cloud_watcher': 10,
                        'transparency': 10,
                        'data_transfer': 10,
                        'free_gb': 4320,
                        'uncopied_gb': 4320}
        self._sleeptime = 30

        self.monitors = sorted(list(self._ntimes.keys()))
        self.status = {monitor: False for monitor in self.monitors}
        self.connections = {monitor: 0 for monitor in self.monitors}

        self.print_thread = threading.Thread(target=self.print_status)
        self.print_thread.daemon = True
        self.print_thread.start()

    def single_report_in(self, name, arg):
        lower_name = name.lower()
        if lower_name not in self.monitors:
            return {'ok': False,
                    'reason': 'No monitor for {}. Available monitors: {}'.format(
                        name, list(self.monitors))}

        old_connections = self.connections[lower_name]
        self.connections[lower_name] = self._ntimes[lower_name]
        old_status = self.status[lower_name]
        if not arg:
            return_status = True
        else:
            return_status = arg
        self.status[lower_name] = return_status
        return {'ok': return_status, 'name': lower_name, 'previous': {
            'connections': old_connections, 'status': old_status,
        }}

    @Pyro4.expose
    def report_in(self, name, arg=None):
        out = self.single_report_in(name, arg)
        return out

    def print_status(self):
        while True:
            print(self.status)
            print(self.connections)
            self.update_connections()
            time.sleep(self.sleeptime)

    def update_connections(self):
        for monitor in self.monitors:
            if self.connections[monitor] > 0:
                self.connections[monitor] -= 1

            if self.connections[monitor] <= 0:
                self.connections[monitor] = 0
                self.status[monitor] = False

    @Pyro4.expose
    def get_status(self):
        return self.status

def main(args):
    hub = CentralHub()
    daemon = Pyro4.Daemon(args.daemon_host)
    ns = Pyro4.locateNS()
    uri = daemon.register(hub)
    ns.register('central.hub', uri)
    daemon.requestLoop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--daemon-host', required=False, default='10.2.5.32',
                        help='Host to publish daemon to')
    main(parser.parse_args())
