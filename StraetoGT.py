import requests
import xml.etree.ElementTree as ET
import time

TIME_FORMAT = '%Y%m%d'

class Worker:

    def __init__(self, url_root):
        self.url_root = url_root

    def initialize(self):
        res = requests.get(self.url_root + 'skema.xml')
        self.root = ET.fromstring(res.text)

    def find_current_schedule(self):
        print("Finding current schedule...")
        for schedule in self.root.findall('aaetlun'):
            start = time.strptime(schedule.get('fra'), TIME_FORMAT)
            end = time.strptime(schedule.get('til'), TIME_FORMAT)
            timenow = time.gmtime()
            if start < timenow and timenow < end:
                self.current_schedule_url = schedule.get('skra')
                print('...found ' + self.current_schedule_url)

    def download_current_schedule(self):
        if not hasattr(self, 'current_schedule_url'):
            self.find_current_schedule()

        print('Downloading: ' + self.current_schedule_url)