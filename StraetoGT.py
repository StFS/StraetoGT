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
log = logging.getLogger(__name__)
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

    def __init__(self, url_root, timenow=time.gmtime()):
        self.url_root = url_root

        # Download the file that describes the available schedules.
        url = self.url_root + 'skema.xml'
        log.info('Retrieving skema.xml from: %s', url)
        res = requests.get(url)
        log.debug('skema.xml contents:\n%s', res.text)
        schedule_tree = ET.fromstring(res.text)

        # Loop thorugh the schedule elements in that file and find
        # the current one.
        self.current_schedule_url = None
        log.info('Finding current schedule...')
        for schedule in schedule_tree.findall('aaetlun'):
            start = time.strptime(schedule.get('fra'), TIME_FORMAT)
            end = time.strptime(schedule.get('til'), TIME_FORMAT)
            if start < timenow and timenow < end:
                current_schedule = schedule.get('skra')
                log.info('Found current schedule: ' + current_schedule)

                if self.current_schedule_url is not None:
                    log.warning("Finding multiple current schedules. We'll use the last one we find.")

                self.current_schedule_url = self.url_root + current_schedule

        log.info('Downloading schedule: ' + self.current_schedule_url)
        response = urllib2.urlopen(self.current_schedule_url)
        compressedFile = StringIO.StringIO()
        compressedFile.write(response.read())
        #
        # Set the file's current position to the beginning
        # of the file so that zipfile.ZipFile can read
        # its contents from the top.
        #
        compressedFile.seek(0)

        log.info('Uncompressing schedule file in memory')
        self.decompressedFile = zipfile.ZipFile(compressedFile)

    def generate_stops(self):
        stops_xml = self.decompressedFile.open('stodvar.xml').read()
        log.debug('stops xml contents:\n%s', stops_xml)
        stops_tree = ET.fromstring(stops_xml)

        stops_gt = StringIO.StringIO()
        stops_gt.write('stop_id,stop_name,stop_lat,stop_lon\n')

        for stop in stops_tree.findall('stod'):
            stops_gt.write(stop.get('id') + ',')
            stops_gt.write(stop.get('nafn') + ',')
            stops_gt.write(stop.get('lat') + ',')
            stops_gt.write(stop.get('lon') + '\n')

        log.debug('GT stops.txt:\n%s', stops_gt.getvalue())
        return stops_gt.getvalue()

    def generate_routes(self):
        routes_xml = self.decompressedFile.open('leidir.xml').read()

        log.debug('routes xml contents:\n%s', routes_xml)
        routes_tree = ET.fromstring(routes_xml)

        routes_gt = StringIO.StringIO()
        routes_gt.write('route_id,route_short_name,route_long_name,route_type\n')

        for route in routes_tree.findall('leid'):
            routes_gt.write(route.get('lid') + ',')
            routes_gt.write(route.get('num') + ',')
            routes_gt.write(route.get('leid') + ',')
            routes_gt.write('3\n')

        log.debug('GT stops.txt:\n%s', routes_gt.getvalue())
        return routes_gt.getvalue()