#!/usr/bin/env python
from __future__ import print_function
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
from config import DNAC_IP, DNAC_USER, DNAC_PASS

HEADERS= {'Content-Type' : 'application/json'}
class DNAC:
    def __init__(self, dnac_ip, username, password, port=443):
        self.dnac_ip = dnac_ip
        self.port = port
        self.base = 'https://{}:{}'.format(self.dnac_ip, self.port)
        self.session = {}
        self.login(self.dnac_ip, self.port, username, password)

    def login(self, dnac_ip, port, username, password):
        """Login to dnac"""
        url = self.base + '/api/system/v1/auth/token'

        result = requests.post(url=url, auth=HTTPBasicAuth(username, password), verify=False)
        result.raise_for_status()

        token = result.json()["Token"]
        self.session[dnac_ip] = token

    def get(self, mount_point, headers={}):
        """GET request"""
        url = self.base + "/{}".format(mount_point)
        #print (url)
        headers = {'x-auth-token' : self.session[self.dnac_ip], 'accept': 'application/json'}
        response = requests.get(url, headers= headers, verify=False)
        response.raise_for_status()
        data = response.json()
        return data

    def post(self, mount_point, payload, headers={}):
        """POST request"""
        url = url = self.base + "/{}".format(mount_point)
        headers = {'Content-Type': 'application/json', 'x-auth-token': self.session[self.dnac_ip]}
        response = requests.post(url=url, data=json.dumps(payload), headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        return data
    def put(self, mount_point, payload, headers={}):
        """POST request"""
        url = url = self.base + "{}".format(mount_point)
        headers = {'Content-Type': 'application/json', 'x-auth-token': self.session[self.dnac_ip]}
        response = requests.put(url=url, data=json.dumps(payload), headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        return data

    def delete(self, mount_point ):
        """POST request"""
        url = url = self.base + "{}".format(mount_point)
        headers = {'x-auth-token': self.session[self.dnac_ip]}

        response = requests.delete(url=url, headers=headers, verify=False)
        response.raise_for_status()
        return response

dnac = DNAC(DNAC_IP, DNAC_USER, DNAC_PASS)

def process_items(items):
    for ap in items:
        hierarchyname = APname = x = y = z = slot = antennaAzimuth0 = antennaAzimuth1 = antennaElevation0  = antennaElevation1 = None
        for key, val in ap.items():
            # print (key, json.dumps(val, indent=2))
            if key == "attributes":
                hierarchyname = val['heirarchyName']
                APname = val['name']
            if key == "position":
                x = val['x']
                y = val['y']
                z = val['z']
            if key == "radios":
                for radio in val:
                    for k2, v2 in radio.items():
                        if k2 == "attributes":
                            slot = v2['slotId']
                        if k2 == 'antenna':
                            if slot == 0:
                                antennaAzimuth0 = v2['azimuthAngle']
                                antennaElevation0 = v2['elevationAngle']
                            elif slot == 1:
                                antennaAzimuth1 = v2['azimuthAngle']
                                antennaElevation1 = v2['elevationAngle']
        s= (hierarchyname,APname,x,y,z,slot,antennaAzimuth0,antennaAzimuth1,antennaElevation0 ,antennaElevation1)
        if None in s:
            print("Warning, some elements None")
        print(f"{hierarchyname},{APname},{antennaAzimuth0}d,{antennaAzimuth1}d,{x},{y},{z},{antennaElevation0}d,{antennaElevation1}d")

sites = dnac.get('api/v1/group/?groupType=SITE')
print("AP_Positions")
print("#hierarchyname,APname,antennaAzimuth0,antennaAzimuth1,X,Y,Z,antennaElevation0,antennaElevation1")
for site in sites['response']:
    for info in site['additionalInfo']:
        if info['nameSpace'] == 'mapGeometry':
            #print(json.dumps(info, indent=2))
            siteid = site['id']
            # adam fix the metrics=false to stop side effect of background metric polling
            response = dnac.get('api/v1/dna-maps-service/domains/{}/aps?pageSize=9999&detailedView=true&metrics=false'.format(siteid))
            #print(json.dumps(response,indent=2))
            if response['items'] != []:
                process_items(response['items'])

