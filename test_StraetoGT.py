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
        address = "http://localhost:{0}/test_data/".format(self.httpd.server_address[1])
        self.worker = StraetoGT.Worker(address)
        threading.Thread(target=self.httpd.serve_forever).start()

    def tearDown(self):
        self.httpd.shutdown()

    def testUrlUnzipping(self):
        self.worker.initialize()
        self.worker.download_current_schedule()



if __name__ == '__main__':
    unittest.main()
