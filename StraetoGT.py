import requests
import xml.etree.ElementTree as ET
import time
import urllib2
import StringIO
import zipfile
import logging

TIME_FORMAT = '%Y%m%d'

#logging.basicConfig(level=logging.DEBUG)
# create logger
log = logging.getLogger('simple_example')
log.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
log.addHandler(ch)


class Worker:

    def __init__(self, url_root):
        self.url_root = url_root

    def initialize(self):
        url = self.url_root + 'skema.xml'
        log.info('Retrieving skema.xml from: %s', url)
        res = requests.get(url)
        log.debug('skema.xml contents:\n%s', res.text)
        self.root = ET.fromstring(res.text)

    def find_current_schedule(self, timenow=time.gmtime()):
        log.info("Finding current schedule...")
        for schedule in self.root.findall('aaetlun'):
            start = time.strptime(schedule.get('fra'), TIME_FORMAT)
            end = time.strptime(schedule.get('til'), TIME_FORMAT)
            if start < timenow and timenow < end:
                self.current_schedule_url = self.url_root + schedule.get('skra')
                log.info('...found ' + self.current_schedule_url)

    def download_current_schedule(self):
        if not hasattr(self, 'current_schedule_url'):
            self.find_current_schedule()

        log.info('Downloading: ' + self.current_schedule_url)

        response = urllib2.urlopen(self.current_schedule_url)
        compressedFile = StringIO.StringIO()
        compressedFile.write(response.read())
        #
        # Set the file's current position to the beginning
        # of the file so that gzip.GzipFile can read
        # its contents from the top.
        #
        compressedFile.seek(0)

        self.decompressedFile = zipfile.ZipFile(compressedFile)

    def generate_stops(self):
        stops = self.decompressedFile.open('stodvar.xml')
        log.info(stops.read())