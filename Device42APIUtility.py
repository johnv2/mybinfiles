#!/usr/bin/python
import urllib2
import base64


class Device42APIUtility:
  def __init__(self):
    self.username = ""
    self.password = ""
  
  def setCreds(self, username, password):
    self.username = username
    self.password = password
    
  def makeAPICall(self,url, reqtype='xml'):
    ### Make Request to Device42 API ###
    request = urllib2.Request(url)
    base64str = base64.encodestring('%s:%s' % (self.username, self.password))[:-1]
    request.add_header("X-Requested-With", "Curl Sample")
    request.add_header("Authorization", "Basic %s" % base64str)
    if (   reqtype == 'json' 
        or reqtype == 'json-p'
        or reqtype == 'jsonp'
        or reqtype == 'xml'
        or reqtupe == 'xhtml' ):
      request.add_header("Content-Type","application/%s" % reqtype)
    else:
      request.add_header("Content-Type","text/%s" % reqtype)
    search_results = urllib2.urlopen(request).read()
    return search_results



