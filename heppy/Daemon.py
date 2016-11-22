#!/usr/bin/env python

import os
import time
import socket

from pprint import pprint

from heppy.EPP import REPP
from heppy.Error import Error
from heppy.Login import Login
from heppy.Client import Client
from heppy.Request import Request
from heppy.Response import Response
from heppy.SignalHandler import SignalHandler

class Daemon:
    def __init__(self, config):
        self.config = config
        self.is_external = False
        self.client = None
        self.handler = SignalHandler({
            'SIGINT':  self.quit,
            'SIGTERM': self.quit,
            'SIGHUP':  self.hello,
            'SIGUSR1': self.hello,
            'SIGUSR2': self.hello,
        })
        self.login_query = None

    def quit(self):
        global quit
        quit()

    def hello(self):
        print "\nHELLO\n"

    def start(self,args = {}):
        self.connect()
        self.login(args)

    def connect(self):
        if self.client is not None:
            return
        if self.is_external:
            self.connect_external()
        else:
            self.connect_internal()

    def login(self, args = {}):
        try:
            query = self.get_login_query(args)
            print Request.prettifyxml(query)
            reply = self.request(query)
            print Request.prettifyxml(reply)
        except Error as e:
            Error.die(2, 'failed perform login request')
        error = None
        try:
            response = Response.parsexml(reply)
            data = response.data
            pprint(data)
        except Error as e:
            error = e.message
            data = e.data
        if error is not None and data['resultCode']!='2002':
            Error.die(2, 'bad login response', data)
        print 'LOGIN OK'

    def get_login_query(self, args = {}):
        if self.login_query is None:
            greeting = self.client.get_greeting()
            greetobj = Response.parsexml(greeting)
            pprint(greetobj.data)
            request = Login.build(self.config, greeting, args)
            self.login_query = str(request)
        return self.login_query

    def connect_internal(self):
        self.client = REPP(self.config['epp'])

    def connect_external(self):
        try:
            self.client = Client(self.config['local']['address'])
            self.client.connect()
        except socket.error as e:
            os.system(self.config['zdir'] + '/eppyd ' + self.config.path + ' &')
            time.sleep(2)
            self.client = Client(self.config['local']['address'])

    def stop(self, args = {}):
        Error.die(3, 'stop not implemented', config)

    def request(self, query):
        with self.handler.block_signals():
            reply = self.client.request(query)
        return reply

    def smart_request(self, query):
        reply = self.request(query)
        response = Response.parsexml(reply)
        pprint(response.data)
        if response.data['result.code'] == '2002':
            self.login()
            reply = self.request(query)
        return reply

