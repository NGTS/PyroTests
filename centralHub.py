#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
To use this code in your program:

import Pyro4

hub = Pyro4.Proxy('PYRONAME:central.hub')

# For example in the rain sensor program:
hub.report_in('rain_sensor')

'''

import threading
import time
import Pyro4

Pyro4.config.REQUIRE_EXPOSE = True

class CentralHub(object):

    '''
    Central hub object.

    This is exposed through Pyro and monitors the status of the
    individual helper processes running.

    The variables _ntimes and _sleeptime control the timeouts of
    the checks:

        * _sleeptime is the amount of time between each poll check
        * _ntimes is the number of checks after a True value where
            the status will remain True
            
    '''

    def __init__(self, output_filename):
        self.output_filename = output_filename

        self._ntimes = 5
        self._sleeptime = 2

        self.monitors = sorted(['rain_sensor', 'alcor', 'microphones',
                                'cloud_watcher', 'transparency'])
        self.status = {monitor: False for monitor in self.monitors}
        self.connections = {monitor: 0 for monitor in self.monitors}

        self.print_thread = threading.Thread(target=self.print_status)
        self.print_thread.daemon = True
        self.print_thread.start()

    @Pyro4.expose
    @property
    def ntimes(self):
        return self._ntimes

    @Pyro4.expose
    @ntimes.setter
    def ntimes(self, value):
        ''' Allows changing the `ntimes` parameter for running code '''
        self._ntimes = value

    @Pyro4.expose
    @property
    def sleeptime(self):
        return self._sleeptime

    @Pyro4.expose
    @sleeptime.setter
    def sleeptime(self, value):
        ''' Allows changing the `sleeptime` parameter for running code '''
        self._sleeptime = value

    def single_report_in(self, name):
        lower_name = name.lower()
        if lower_name not in self.monitors:
            return {'ok': False,
                    'reason': 'No monitor for {}. Available monitors: {}'.format(
                        name, list(self.monitors))}

        old_connections = self.connections[lower_name]
        self.connections[lower_name] = self._ntimes
        old_status = self.status[lower_name]
        self.status[lower_name] = True
        return {'ok': True, 'name': lower_name, 'previous': {
            'connections': old_connections, 'status': old_status,
        }}

    @Pyro4.expose
    def report_in(self, *names):
        out = []
        for name in names:
            out.append(self.single_report_in(name))
        return out

    def print_status(self):
        while True:
            print(self.status)

            StatusPresenter(self.status).render_to(self.output_filename)

            self.update_connections()
            time.sleep(self.sleeptime)

    def update_connections(self):
        for monitor in self.monitors:
            if self.connections[monitor] > 0:
                self.connections[monitor] -= 1

            if self.connections[monitor] <= 0:
                self.connections[monitor] = 0
                self.status[monitor] = False

class StatusPresenter(object):
    def __init__(self, status):
        self.status = status
        self.css_class = {True: 'goodqty', False: 'badqty'}

    @staticmethod
    def humanise(monitor):
        return monitor.replace('_', '')

    def format_status_row(self, monitor):
        status = self.status[monitor]
        css_class = self.css_class[status]
        return '<tr><td class="{css_class}">{text}</td></tr>'.format(
            text=self.humanise(monitor),
            css_class=css_class)

    def status_string(self):
        out = '<table class="scripts_running">{content}</table>'
        content = ''.join([self.format_status_row(monitor) for monitor in self.status])
        return out.format(content=content)

    def render_to(self, filename):
        with open(filename, 'w') as outfile:
            outfile.write(self.status_string())

if __name__ == '__main__':
    output_filename = '/home/ops/ngts/prism/monitor/scripts_running.php'

    hub = CentralHub(output_filename)
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(hub)
    ns.register('central.hub', uri)
    daemon.requestLoop()
