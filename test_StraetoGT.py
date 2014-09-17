import appengine_config

import os
import unittest
import threading
import requests
import xml.etree.ElementTree as ET

import SimpleHTTPServer
import SocketServer
import StraetoGT

class StraetoGT_TestCase(unittest.TestCase):

    def setUp(self):
        handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        self.httpd = SocketServer.TCPServer(("", 0), handler)
        self.address = "http://localhost:{0}/test_data/".format(self.httpd.server_address[1])
        threading.Thread(target=self.httpd.serve_forever).start()

    def tearDown(self):
        self.httpd.shutdown()

    def testAll(self):
        worker = StraetoGT.Worker(self.address)
        worker.generate_stops()
        worker.generate_routes()


if __name__ == '__main__':
    unittest.main()
