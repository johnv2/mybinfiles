#!/usr/bin/python
import os
import time
import random
import socket
import platform
import smtplib
import subprocess
import string
import sys 
import livestatus
import dmidecode
from optparse import OptionParser

# list of OMD_nodes from OMD returns SITES
execfile('./sites.mk')

if 'MASTER' in SITES:
    SITES['MASTER']['multisiteurl'] = 'http://pslchi6pmon/master/check_mk/'
    SITES['MASTER']['socket'] = 'tcp:pslchi6pmon1:6557'

def confirm_added(hostname, OS):
    if OS == "centos" or OS == "ubuntu":
        OS = "linux"
    elif OS == "Windows":
        OS = "windows"
       
    # livestatus won't reflect the new host until changes have been activated
    # so we'll cheat and just lookup the host directory
    if hostname.find("peak6.net") == -1:
        if hostname.find("chi6") >= 0:
            check_string = "%s -s -u %s:%s \"http://%s/master/check_mk/wato.py"\
                           "?mode=folder&folder=new/new_sg\"" % (
                           curl,
                           USERNAME,
                           PASSWORD,
                           OMDMASTER)

        else:
            check_string = "%s -s -u %s:%s \"http://%s/master/check_mk/wato.py"\
                           "?mode=folder&folder=new/new__sv\"" % (
                           curl,
                           USERNAME,
                           PASSWORD,
                           OMDMASTER)

    else:
        # we're adding to the snmp node
        if hostname.find("chi6") >= 0:
            check_string = "%s -s -u %s:%s \"http://%s/master/check_mk/"\
                           "wato.py?mode=folder&folder=snmp/snmp_sg/%s\"" % (
                           curl,
                           USERNAME,
                           PASSWORD,
                           OMDMASTER,
                           OS)

        else:
            check_string = "%s -s -u %s:%s \"http://%s/master/check_mk/wa"\
                           "to.py?mode=folder&folder=snmp/snmp_sv/%s\"" % (
                           curl,
                           USERNAME,
                           PASSWORD,
                           OMDMASTER,
                           OS)

    p_check = subprocess.Popen(check_string, shell=True, stdout=subprocess.PIPE)
    p_check_stdout = p_check.communicate()[0]

    if p_check_stdout.find("host=%s&folder" % hostname) >= 0: 
        send_debug("add_to_omd.py: Success: Host %s added" % hostname) if DEBUG else ''
        return True
    else:
        send_debug("add_to_omd.py: Error: Problem adding %s" % hostname) if DEBUG else ''
        return False

def get_omd_hosts(ls_conn):
    tcp_hosts = set()
    snmp_hosts = set()
    hosts = set()
    qry = "GET hosts\nColumns: host_name"
    results = ls_conn.query(qry)
    for host in results:
        host = host[0].lower()
        if host[0] == 'o':
            continue
        if '.' in host:
            snmp_hosts.add(host)
        else:
            tcp_hosts.add(host)

        hosts.add(host)

    return hosts, tcp_hosts, snmp_hosts

def parse_args():
    global DEBUG
    global EMAIL

    parser = OptionParser()

    parser.add_option("-a", "--email_address", dest="EMAIL_ADDR", default=False,
                      help="email address to receive alert messages")
    parser.add_option("-e", "--email", dest="EMAIL", action="store_true",
                      default=False, help="send email alerts")
    parser.add_option("-d", "--debug", dest="DEBUG", action="store_true",
                      default=False, help="enable debug mode")

    options, args = parser.parse_args()

    EMAIL = options.EMAIL
    EMAIL_ADDR = options.EMAIL_ADDR
    DEBUG = options.DEBUG

    return EMAIL, DEBUG

def send_debug(str):
    # Print message to console
    print str

    if EMAIL is True:
        try:
            EMAIL_ADDR
        except NameError: 
            EMAIL_ADDR = None

        if EMAIL_ADDR is None:
            EMAIL_ADDR = "jdoshier@peak6.com"

        EMAIL_TO = EMAIL_ADDR
        EMAIL_FROM = "python@peak6.com"
        EMAIL_SUBJECT = str
        EMAIL_SERVER = "smtp.peak6.net"
        EMAIL_CONNECTION = smtplib.SMTP(EMAIL_SERVER)
        EMAIL_BODY = string.join((
            "From: %s" % EMAIL_FROM,
            "To: %s" % EMAIL_TO,
            "Subject: %s" % str,
            "",
            ), "\r\n")
        EMAIL_CONNECTION.sendmail(EMAIL_FROM, EMAIL_TO, EMAIL_BODY)
        EMAIL_CONNECTION.quit()

def get_platform(hostname):
    global curl

    # Determine whether we're on Linux, Windows, Solaris
    OS = platform.system()

    if OS == "Windows":
        if os.path.isfile(WINCURLBIN):
            curl = WINCURLBIN
        else:
            if DEBUG:
                send_debug("add_to_omd.py: Error: can't find curl on %s" % hostname)
            sys.exit(1)

        OS = "windows"
        return OS, curl

    elif OS == "Linux":
        if os.path.isfile(LNXCURLBIN):
            curl = LNXCURLBIN
        else:
            if DEBUG:
                send_debug("add_to_omd.py: Error: can't find curl on %s" % hostname)
            sys.exit(1)

        if os.path.isfile("/etc/redhat-release"):
            OS = "centos"
            return OS, curl

        elif os.path.isfile("/etc/debian_version"):
            OS = "ubuntu"
            return OS, curl

    elif OS == "Sunos":
        if os.path.isfile(SUNCURLBIN):
            curl = SUNCURLBIN
        else:
            if DEBUG:
                send_debug("add_to_omd.py: Error: can't find curl on %s" % hostname)
            sys.exit(1)

        OS = "solaris"
        return OS, curl

    else:
        if DEBUG:
            send_debug("add_to_omd.py: Error: Cannot determine OS type for %s" % hostname)
        sys.exit(1)

def get_hostname():
    # Get hostname and confirm we have an IP in DNS
    hostname = socket.gethostname().lower()
    try:
        socket.gethostbyname(hostname)
        return hostname

    except socket.error:
        if DEBUG:
            send_debug("add_to_omd.py: Error: Could not determine %s IP" % hostname)
        sys.exit(1)

def get_location(hostname, LOCATIONS):
    global OMD_node
    global OMD_node_short

    for i in LOCATIONS:
        index = hostname.find(i)
      
        if index >= 0:
            # check_index tells us where to look to determine if the box is
            # prod/dev/stg only works with current naming standards ie.
            # sslchi6pmon1
            check_index = index + len(i)
    
            if i == "chi1":
                OMD_node = "SAVVIS"
                OMD_node_short = "sv"
            elif i == "chi6":
                OMD_node = "STARGATE"
                OMD_node_short = "sg"
            elif i == "chi5":
                OMD_node = "SAVVIS"
                OMD_node_short = "sv"
            elif i == "ewr3":
                OMD_node = "SAVVIS"
                OMD_node_short = "sv"
            elif i == "ewr4":
                OMD_node = "SAVVIS"
                OMD_node_short = "sv"

            # This is to make sure they're added to the correct OMD node
            if hostname[check_index]  == "d":
                OMD_node = OMD_node + "_dev"

            elif hostname[check_index] == "s":
                OMD_node = OMD_node + "_stage"
    
    try:
        OMD_node

    except NameError:
        if DEBUG:
            send_debug("add_to_omd.py: Error: Could not determine %s location" % hostname)
        sys.exit(1)

    return OMD_node, OMD_node_short

def search_livestatus(hostname, ls_conn):
    omd_hosts, omd_hosts_tcp, omd_hosts_snmp = get_omd_hosts(ls_conn)

    # Exception for hosts that don't show up in livestatus search results
    if (hostname == "pslchi6phfst1" or hostname == "pslchi6pmon1"):
        sys.exit(1)

    if hostname in omd_hosts:
        return True
    elif hostname in omd_hosts_tcp:
        return True
    elif hostname in omd_hosts_snmp:
        return True
    else:
        return False

def is_host_a_VM(hostname):
    t = dmidecode.processor()
    k, v = t.popitem()

    CPU = v['data']['Manufacturer']['Vendor']

    if CPU == "Bochs" or CPU == "000000000000":
        return True
    else:
        return False

def add_host(hostname, OS):
    transid = "%d%%2F%d" % (int(time.time()), random.getrandbits(32))

    add_string = "%s -s -u %s:%s \"http://%s/master/check_mk/wato.py?filled_in"\
                 "=edithost&_transid=%s&host=%s&contactgroups_use=on&attr_alia"\
                 "s=&attr_ipaddress=&parents_0=&_change_site=on&site=%s&_chang"\
                 "e_tag_agent=on&attr_tag_agent=cmk-agent%%7Ctcp&attr_tag_crit"\
                 "icality=prod&attr_tag_networking=lan&attr_tag_techunit=na&at"\
                 "tr_tag_snmp_community=%s&_change_tag_os=on&attr_tag_os=%s&sa"\
                 "ve=Save+%%26+Finish&folder=new%%2Fnew__%s&mode=newhost\"" % (
                  curl,
                  USERNAME,
                  PASSWORD,
                  OMDMASTER,
                  transid,
                  hostname,
                  OMD_node,
                  OMDSNMPSTRING,
                  OS,
                  OMD_node_short)

    p_add = subprocess.Popen(add_string, shell=True, stdout=subprocess.PIPE)
    p_add_stdout = p_add.communicate()[0]

    if p_add_stdout.find("called this page with a non-existing folder") >= 0:
        add_string2 = "%s -s -u %s:%s \"http://%s/master/check_mk/wato.py?fill"\
                      "ed_in=edithost&_transid=%s&host=%s&contactgroups_use=on"\
                      "&attr_alias=&attr_ipaddress=&parents_0=&_change_site=on"\
                      "&site=%s&_change_tag_agent=on&attr_tag_agent=cmk-agent%"\
                      "%7Ctcp&attr_tag_criticality=prod&attr_tag_networking=la"\
                      "n&attr_tag_techunit=na&attr_tag_snmp_community=%s&_chan"\
                      "ge_tag_os=on&attr_tag_os=%s&save=Save+%%26+Finish&folde"\
                      "r=new%%2Fnew_%s&mode=newhost\"" % (
                      curl,
                      USERNAME,
                      PASSWORD,
                      OMDMASTER,
                      transid,
                      hostname,
                      OMD_node,
                      OMDSNMPSTRING,
                      OS,
                      OMD_node_short)

        p2_add = subprocess.Popen(add_string2, shell=True,
            stdout=subprocess.PIPE)
        p_add_stdout2 = p2_add.communicate()[0]

        if p_add_stdout2.find("Error: called this page with a non-existing folder") >= 0:
            if DEBUG:
                send_debug("add_to_omd.py: Error: Adding %s to a non-existing folder" % hostname)

        else: 
            confirm_added(hostname, OS)

    else: 
        confirm_added(hostname, OS)

def file_exists(STOPFILE):
    try:
        with open('%s' % STOPFILE) as f:
            send_debug("add_to_omd.py: Error: STOPFILE exists on %s" % hostname)
            sys.exit(1)
    except IOError:
        pass


def find_master(OMDMASTER):
    try:
        socket.gethostbyname('%s' % OMDMASTER)
    except:
        if DEBUG:
            send_debug("add_to_omd.py: Error: Problem looking up %s in DNS on %s" % OMDMASTER, hostname)
            sys.exit(1)

def add_host_snmp(hostname, OS):
    transid = "%d%%2F%d" % (int(time.time()), random.getrandbits(32))

    add_string = "%s -s -u %s:%s \"http://%s/master/check_mk/wato.py?filled_in=editho"\
                 "st&_transid=%s&host=%s&contactgroups_use=on&attr_alias=&attr"\
                 "_ipaddress=&parents_0=&attr_tag_agent=cmk-agent%%7Ctcp&attr_"\
                 "tag_criticality=prod&attr_tag_networking=lan&attr_tag_techun"\
                 "it=na&attr_tag_snmp_community=%s&attr_tag_OS=%s&save=Save+%%"\
                 "26+Finish&folder=snmp%%2Fsnmp_%s%%2Flinux&mode=newhost\"" % (
                 curl,
                 USERNAME,
                 PASSWORD,
                 OMDMASTER,
                 transid,
                 hostname,
                 OMDSNMPSTRING,
                 OS,
                 OMD_node_short) 

    p_add = subprocess.Popen(add_string, shell=True, stdout=subprocess.PIPE)
    p_add_stdout = p_add.communicate()[0]

    if p_add_stdout.find("called this page with a non-existing folder") >= 0:
        add_string = "%s -s -u %s:%s \"http://%s/master/check_mk/wato.py?filled_in=ed"\
                     "ithost&_transid=%s&host=%s&contactgroups_use=on&attr_ali"\
                     "as=&attr_ipaddress=&parents_0=&attr_tag_agent=cmk-agent%"\
                     "%7Ctcp&attr_tag_criticality=prod&attr_tag_networking=lan"\
                     "&attr_tag_techunit=na&attr_tag_snmp_community=%s&attr_ta"\
                     "g_OS=%s&save=Save+%%26+Finish&folder=snmp%%2Fsnmp_%s%%2F"\
                     "linux&mode=newhost\"" % (
                     curl,
                     USERNAME,
                     PASSWORD,
                     OMDMASTER,
                     transid,
                     hostname,
                     OMDSNMPSTRING,
                     OS,
                     OMD_node_short) 

        p2_add = subprocess.Popen(add_string2, shell=True, stdout=subprocess.PIPE)
        p_add_stdout2 = p2_add.communicate()[0]

        if p_add_stdout2.find("called this page with a non-existing folder") >= 0:
            send_debug("add_to_omd.py: Error: Adding %s to a non-existing folder" % hostname) if DEBUG else ''

        else: 
            confirm_added(hostname, OS)

    else: 
        confirm_added(hostname, OS)

# Main   
def main():
    global SNMPSTRING
    global USERNAME
    global PASSWORD
    global WINCURLBIN
    global LNXCURLBIN
    global SUNCURLBIN
    global OMDSNMPSTRING
    global OMDMASTER
    global hostname

    # This is not the actual community string but how it's represented in OMD
    OMDSNMPSTRING = "everything"

    # credentials to auth with OMD via http
    USERNAME = "omdadmin"
    PASSWORD = "omd"

    # replace with libcurl in the future
    WINCURLBIN = "C:\check_mk\\automation\curl-7.27.0-rtmp-ssh2-ssl-sspi-zlib-winidn-static-bin-w64\curl.exe"
    LNXCURLBIN = "/usr/bin/curl"
    SUNCURLBIN = "/opt/csw/bin/curl"

    STOPFILE = "STOP-ADD_TO_OMD"

    OMDMASTER = "pslchi6pmon1"

    LOCATIONS = ["chi1", "chi5", "chi6", "ewr3", "ewr4"]

    EMAIL, DEBUG = parse_args()

    hostname = get_hostname()

    # do not run if we're on an OH machine
    if hostname[0] == 'o':
        sys.exit(1)

    # Search for a STOPFILE to see if we should be run or not
    file_exists('%s' % STOPFILE)

    # Make sure we can lookup the OMDMASTER in DNS
    find_master('%s' % OMDMASTER)

    OS, curl = get_platform(hostname)

    OMD_node, OMD_node_short = get_location(hostname, LOCATIONS)

    VM = is_host_a_VM(hostname)

    # For searching for hosts in OMD
    ls_conn = livestatus.MultiSiteConnection(SITES)

    if len(ls_conn.dead_sites().keys()) > 0:
        send_debug("add_to_omd.py: Warning: Won't add hosts when we have a dead site")
        sys.exit(1)

    if search_livestatus(hostname, ls_conn) is False:
        add_host(hostname, OS)

    else:
        if DEBUG:
            send_debug("add_to_omd.py: Warning: Host %s already exists" % hostname)

    if VM is False:
        hostname = hostname + ".peak6.net"

        if search_livestatus(hostname, ls_conn) is False:
            add_host_snmp(hostname, OS)

        else:
            if DEBUG:
                send_debug("add_to_omd.py: Warning: Host %s already exists" % hostname)

    else:
        if DEBUG:
            send_debug("add_to_omd.py: Warning: %s is a VM and was not added" % hostname)

if __name__ == "__main__":
    main()
