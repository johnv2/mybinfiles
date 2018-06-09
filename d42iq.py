#!/usr/bin/python

#import Device42APIUtility
import argparse
import sys
import os
import json
import string
import re
from Device42APIUtility import *

def parseArgs():
  ### Create an Argument Parser ###
  parser = argparse.ArgumentParser(description = 'Queries the Inventory')
  parser.add_argument('-u','--username', required=False, default='api_ro', help = "Device42 API Username")
  parser.add_argument('-p','--password', required=False, default='api_ro', help = "Device42 API Password")
  parser.add_argument('-f','--force', required=False, default=False, help = "Force reload cache?", action="store_true")
  parser.add_argument('-c','--cache', required=False, default='/tmp/d42iq.cache', help="Cache File Locaiton")
  parser.add_argument('-a','--allocation', required=False, default=False, help = "Display Allocation Model?", action="store_true")
  parser.add_argument('-w','--hardware', required=False, default=False, help = "Display Hardware Details", action="store_true")
  parser.add_argument('-1','--deviceonly', required=False, default=False, help = "List only one device per line?", action="store_true")

  arg_list = parser.parse_args()
  return arg_list

def main():
  server = "device42/"
  baseURL = "https://" + server
  url = baseURL + "/api/1.0/devices/all/"
  dev42 = Device42APIUtility()
  arg_list = parseArgs()

  if arg_list.force != False or not os.path.isfile(arg_list.cache):
    dev42.setCreds ( arg_list.username, password = arg_list.password )
    print "Refreshing Cache..."
    data = dev42.makeAPICall( url, "json" )
    jdata = json.loads(data)
    with open(arg_list.cache, 'wb') as outfile:
      json.dump(jdata, outfile)
    return
  else:
    with open(arg_list.cache) as infile:
      jdata = json.load(infile)


  for host in jdata['Devices'] :
    response=host

    if host['type'] == 'blade' or host['type'] == 'virtual' :
      if string.find(host['name'],"chi6")  > 0:
        response['building'] = "Stargate (chi6)"
      elif string.find(host['name'],"chi5") > 0 :
        response['building'] = "Savvis (chi5)"
      elif string.find(host['name'],"chi1") > 0 :
        response['building'] = "CBOT (chi1)"
      elif string.find(host['name'],"ewr3") > 0:
        response['building'] = "Carteret (ewr3)"
      elif string.find(host['name'],"ewr4") > 0:
        response['building'] = "Secaucus (ewr4)"

    if host['type'] == 'blade' :
      if 'blade_host_name' in response:
        response['rack'] = response['blade_host_name']
      else:
        response['rack'] = "BLADE"
      if 'slot_number' in response :
        response['start_at'] = response['slot_number']
      else:
        response['start_at'] = "0"
    elif  host['type'] == 'virtual' :
      if host['asset_no'] == "" :
        response['asset_no'] = "VM"
      elif host['asset_no'] not in response:
        response['asset_no'] = "VM"
      if 'virtual_host_name' in response:
        if response['virtual_host_name'] == '' or response['virtual_host_name'] == None:
          response['rack'] = "VIRTUAL"
        else:
          response['rack'] = response['virtual_host_name']
      else:
        response['rack'] = "VIRTUAL"
      response['start_at'] = "0"
      response['hw_model'] = "VIRTUAL"
    if 'ip_addresses' in response :
      ips = response['ip_addresses']
      for ip in ips:
        label = str(ip['label'])
        if label.lower().find("oob") >= 0:
          response['OOB'] = ip['ip']
      if 'OOB' not in response:
        response['OOB'] = "No OOB"
    else:
      response['OOB'] = "No OOB"

    if host['type'] == 'other' :
      if 'device_sub_type' in response:
        if host['device_sub_type'] == "Switched Rack PDU" :
          response['rack'] = "PDU"
          if string.find(host['name'],"chi6") > 0:
            response['building'] = "Stargate (chi6)"
          elif string.find(host['name'],"chi5") > 0:
            response['building'] = "Savvis (chi5)"
          elif string.find(host['name'],"ewr3") > 0:
            response['building'] = "Carteret (ewr3)"
          elif string.find(host['name'],"ewr4") > 0:
            response['building'] = "Secaucus (ewr4)"

    if 'building' not in response :
      response['building'] = "UNKNOWN"
    if 'rack' not in response :
      response['rack'] = "000"
    if 'start_at' not in response :
      response['start_at'] = 0
    if 'hw_model' not in response :
      response['hw_model'] = "UNKNOWN"



    if 'custom_fields' in response :
      fields = response['custom_fields']
      for field in fields:
        if field['key'] == 'Allocation Model':
          response['allocation'] = field['value']
      if 'allocation' not in response:
        response['allocation'] = "No Allocation Model"
    else:
      response['allocation'] = "No Allocation Model"

    response['cost'] = 0.0
    response['order_no'] = "N/A"
    if 'device_purchases' in response :
      purchases = response['device_purchases']
      for purchase in purchases:
        if 'cost' in purchase:
          if purchase['cost'] > 0:
            response['cost'] = purchase['cost']
        if 'order_no' in purchase:
            response['order_no'] = purchase['order_no']

    if string.find(response['building'],"chi") >= 0:
      response['city'] = "Chicago"
    elif string.find(response['building'],"ewr") >= 0:
      response['city'] = "New York"
    elif string.find(response['building'],"nyc") >= 0:
      response['city'] = "New York"
    else:
      if string.find(response['name'].lower(),"chi") >= 0:
        response['city'] = "Chicago"
      elif string.find(response['name'].lower(),"ewr") >= 0 :
        response['city'] = "New York"
      elif string.find(response['name'].lower(),"nyc") >= 0 :
        response['city'] = "New York"
      elif string.find(response['name'].lower(),"disposed") >= 0 :
        response['city'] = ""
      elif string.find(response['name'].lower(),"retired") >= 0 :
        response['city'] = ""
      else:
        response['city'] = "UNKNOWN"

    if response['hw_model'] :
      if re.match("^PowerEdge*", response['hw_model']) or re.match("ProLiant*", response['hw_model']) or re.match("^System x3[5,6,9]50*", response['hw_model']) or re.match("^VIRTUAL*", response['hw_model']):
        response['dfu_type'] = "Server"
      elif re.match("^Cisco*", response['hw_model']) or re.match("^j[f,g]s524*", response['hw_model']) or re.match("^cevChassis*", response['hw_model']) or re.match("ASA55", response['hw_model']) or re.match("^N[5,7]", response['hw_model']):
        response['dfu_type'] = "Network"
      elif re.match("^[2-6][0-9][0-9][0-9]*", response['hw_model']) or re.match("^DCS*", response['hw_model']) or re.match("^F5*", response['hw_model']) or re.match("^c7000*", response['hw_model']) or re.match("^PA-3020*", response['hw_model']) :
        response['dfu_type'] = "Network"
      elif re.match("^Juniper*", response['hw_model']) or re.match("^Nexus*", response['hw_model']) or re.match("nexus*", response['hw_model']) or re.match("Catalyst*", response['hw_model']) or re.match("Dell Powerconnect*", response['hw_model']):
        response['dfu_type'] = "Network"
      elif re.match("^Infi niStream*", response['hw_model']) or re.match("^Envision*", response['hw_model']) or re.match("Video conference appliance*", response['hw_model']):
        response['dfu_type'] = "Network"
      elif re.match("^EMC*", response['hw_model']) or re.match("^M[D,S]*", response['hw_model']) or re.match("^AX4*", response['hw_model']):
        response['dfu_type'] = "Storage"
      else:
        response['dfu_type'] = "Other"
    else:
      response['dfu_type'] = "Other"

    if arg_list.hardware:
      if 'cpucount' not in response or response['cpucount'] == None:
        response['cpucount'] = "X"
      if 'cpucore' not in response or response['cpucore'] == None:
        response['cpucore'] = "X"
      if 'cpuspeed' not in response or response['cpuspeed'] == None:
        response['cpuspeed'] = "X"
      if 'ram' not in response:
        response['ram_g'] = "0"
      else:
        if isinstance(response[u'ram'], unicode) or response.get('ram') == None:
          response['ram_g'] = "0"
        else:
          response['ram_g'] = str(str(int(response['ram'] / 1024)) + "G")
      if response['cpucount'] == "X" and response['cpucore'] == "X" and response['cpuspeed'] == "X":
        response['cpuinfo'] = ""
      elif response['cpucore'] == "X" and response['cpuspeed'] == "X":
         response['cpuinfo'] = str(response['cpucount']) + " CPUs"
      else:
        if isinstance(response[u'cpuspeed'], unicode):
          response['cpuspeed'] = "0"
          response['cpuinfo'] = str(response['cpucount']) + 'x' + str(response['cpucore']) + " @ " + "0Ghz"
        else:
          response['cpuinfo'] = str(response['cpucount']) + 'x' + str(response['cpucore']) + " @ " + str(int(response['cpuspeed']) / 1000.0) + "Ghz"

    if 'hw_model' not in response :
      response['hw_model'] = "UNKNOWN"

    if 'osver' not in response :
      response['osver'] = "NoOSVer"
    if 'os' not in response :
      response['os'] = "NoOS"
    response['osversion']=str(response['os'])+" - "+str(response['osver'])

    response['locate'] = string.replace(response['rack'],'Cabinet ','') + "-" + str(int(response['start_at']))

    if arg_list.deviceonly:
      print response['name']
    elif arg_list.allocation:
        print "{:<2s}|{:<2s}|{:<2s}|{:<2s}|{:<2s}|{:<2s}-{:<2s}|{:<2s}|{:<2s}|{:<2s}|{:<2s}|{:<2.2f}|{:<2s}|{:2s}|{:<300.300s}".format(response['name'], response['asset_no'],response['serial_no'],response['OOB'],response['building'],string.replace(response['rack'],'Cabinet ',''),str(int(response['start_at'])),response['hw_model'],response['service_level'],response['allocation'],response['order_no'],response['cost'],response['city'],response['dfu_type'],response['notes'].replace("\n", ";") if response['notes'] else 'None').strip()
    elif arg_list.hardware:
        print "{:<35.35s}|{:<6.6s}|{:<16.16s}|{:<15.15s}|{:<27.27s}|{:<25.25s}|{:<20.20s}|{:<15.15s}|{:<5.5s}|{:<25.25s}".format(response['name'],response['asset_no'],response['serial_no'],response['OOB'],response['building'],response['locate'],response['hw_model'],response['cpuinfo'],str(response['ram_g']),response['osversion'])
    else:
        print "{:<35.35s}|{:<6.6s}|{:<16.16s}|{:<15.15s}|{:<27.27s}|{:<25.25s}|{:<20.20s}|{:<25.25s}".format(response['name'],response['asset_no'],response['serial_no'],response['OOB'],response['building'],response['locate'],response['hw_model'],response['osversion'])

if __name__ == '__main__':
  main()

