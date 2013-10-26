#!/usr/env python
#-*- coding: utf-8 -*-
from __future__ import division
import zipfile
from pygraphml.GraphMLParser import *
from pygraphml.Graph import *
from pygraphml.Node import *
from pygraphml.Edge import *
from random import randint
from BeautifulSoup import BeautifulSoup
from datetime import date
from google import search
from instagram.client import InstagramAPI
from linkedin import linkedin
from lxml import etree,html
from pprint import pprint
from pygeocoder import Geocoder
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from StringIO import StringIO
from termcolor import colored, cprint
from TwitterSearch import *
from requests import session
from xml.dom import minidom
import atom.data, gdata.client, gdata.docs.client, gdata.docs.data, gdata.docs.service
import cookielib
import foursquare
import geopy
import geopy.distance
import google
import httplib,httplib2,json
import lxml
import oauth2 as oauth
import os
import re
import requests
import sqlite3
import string
import sys
import time, os, simplejson
import urllib
import urllib2
import webbrowser
import zlib

tweetList = []
globalUserList = []
nodeList = []
edgeList = []	
foursqTwitterSearch = []

report = ""
maltegoXML = ''
wirelessAPData = ""

#Gmail
google_username = ""
google_password = ""
google_drive_collection = "kkk"

#Instagram
#http://instagram.com/developer/register/
instagram_client_id = ""
instagram_client_secret = ""
instagram_access_token = ""

#Foursquare
foursquare_client_id = ""
foursquare_client_secret = ""
foursquare_access_token = ""


#Linkedin
linkedin_api_key = ""
linkedin_api_secret = ""
linkedin_oauth_user_token = ""
linkedin_oauth_user_secret = ""
linkedin_username = ""
linkedin_password = ""

#Flick
#Instructions on getting oauth token and secret
#http://librdf.org/flickcurl/api/flickcurl-auth-authenticate.html
flickr_key = ""
flickr_secret = ""
flickr_oauth_token = ""
flickr_oauth_secret = ""

#Twitter
twitter_consumer_key = ""
twitter_consumer_secret = ""
twitter_access_key = ""
twitter_access_secret = ""

#Wigle.net
wigle_username = ""
wigle_password = ""

requests.adapters.DEFAULT_RETRIES = 30

lat = ''
lng = ''

htmlHeader = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><head><meta charset="UTF-8"><title>Google Maps Example</title><script src=\'http://code.jquery.com/jquery.min.js\' type=\'text/javascript\'></script></head><body><script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script>'

def createDatabase():
	c = conn.cursor()
	sql = 'create table if not exists twitter (username TEXT, tweet TEXT unique, latitude TEXT, longitude TEXT , origLat TEXT, origLng TEXT)'
	sql1 = 'create table if not exists instagram (username TEXT, latitude TEXT, longitude TEXT, url TEXT unique , origLat TEXT, origLng TEXT)'
	#sql2 = 'create table if not exists flickr (URL TEXT unique, username TEXT, cameraModel TEXT, longitude TEXT, latitude TEXT, origLat TEXT, origLng TEXT)'
	sql2 = 'create table if not exists flickr (URL TEXT unique, description TEXT, username TEXT, cameraModel TEXT, longitude TEXT, latitude TEXT, origLat TEXT, origLng TEXT)'
	sql3 = 'create table if not exists macAddress (macAddress TEXT unique, manufacturer TEXT)'
	c.execute(sql)
	c.execute(sql1)
	c.execute(sql2)
	c.execute(sql3)	
	conn.commit()
	

conn = sqlite3.connect('geostalking.db')
createDatabase()

def normalize(s):
	if type(s) == unicode: 
       		return s.encode('utf8', 'ignore')
	else:
        	return str(s)
	        	
def createLink(label):
	xmlString = '<mtg:MaltegoLink xmlns:mtg="http://maltego.paterva.com/xml/mtgx" type="maltego.link.manual-link">'
	xmlString += '<mtg:Properties>'
	xmlString += '<mtg:Property displayName="Description" hidden="false" name="maltego.link.manual.description" nullable="true" readonly="false" type="string">'
	xmlString += '<mtg:Value/>'
	xmlString += '</mtg:Property>'
	xmlString += '<mtg:Property displayName="Style" hidden="false" name="maltego.link.style" nullable="true" readonly="false" type="int">'
	xmlString += '<mtg:Value>0</mtg:Value>'
	xmlString += '</mtg:Property>'
	xmlString += '<mtg:Property displayName="Label" hidden="false" name="maltego.link.manual.type" nullable="true" readonly="false" type="string">'
	xmlString += '<mtg:Value>'+label+'</mtg:Value>'
	xmlString += '</mtg:Property>'
	xmlString += '<mtg:Property displayName="Show Label" hidden="false" name="maltego.link.show-label" nullable="true" readonly="false" type="int">'
	xmlString += '<mtg:Value>0</mtg:Value>'
	xmlString += '</mtg:Property>'
	xmlString += '<mtg:Property displayName="Thickness" hidden="false" name="maltego.link.thickness" nullable="true" readonly="false" type="int">'
	xmlString += '<mtg:Value>2</mtg:Value>'
	xmlString += '</mtg:Property>'
	xmlString += '<mtg:Property displayName="Color" hidden="false" name="maltego.link.color" nullable="true" readonly="false" type="color">'
	xmlString += '<mtg:Value>8421505</mtg:Value>'
	xmlString += '</mtg:Property>'
	xmlString += '</mtg:Properties>'
	xmlString += '</mtg:MaltegoLink>'
	return xmlString

def createNodeImage(name,url):
	xmlString = '<mtg:MaltegoEntity xmlns:mtg="http://maltego.paterva.com/xml/mtgx" type="maltego.Image">'
	xmlString += '<mtg:Properties>'
	xmlString += '<mtg:Property displayName="Description" hidden="false" name="description" nullable="true" readonly="false" type="string">'
	xmlString += '<mtg:Value>'+name+'</mtg:Value>'
	xmlString += '</mtg:Property>'
	xmlString += '<mtg:Property displayName="URL" hidden="false" name="url" nullable="true" readonly="false" type="url">'
	xmlString += '<mtg:Value>'+url+'</mtg:Value>'
	xmlString += '</mtg:Property>'
	xmlString += '</mtg:Properties>'
	xmlString += '</mtg:MaltegoEntity>'
	return xmlString

def createNodeFacebook(displayName,url,uid):
	xmlString = '<mtg:MaltegoEntity xmlns:mtg="http://maltego.paterva.com/xml/mtgx" type="maltego.affiliation.Facebook">'
	xmlString += '<mtg:Properties>'
	xmlString += '<mtg:Property displayName="Name" hidden="false" name="person.name" nullable="true" readonly="false" type="string">'
	xmlString += '<mtg:Value>'+displayName+'</mtg:Value>'
	xmlString += '</mtg:Property>'
	xmlString += '<mtg:Property displayName="Network" hidden="false" name="affiliation.network" nullable="true" readonly="true" type="string">'
	xmlString += '<mtg:Value>Facebook</mtg:Value>'
	xmlString += '</mtg:Property>'
	xmlString += '<mtg:Property displayName="UID" hidden="false" name="affiliation.uid" nullable="true" readonly="false" type="string">'
	xmlString += '<mtg:Value>'+uid+'</mtg:Value>'
	xmlString += '</mtg:Property>'
	xmlString += '<mtg:Property displayName="Profile URL" hidden="false" name="affiliation.profile-url" nullable="true" readonly="false" type="string">'
	xmlString += '<mtg:Value>'+url+'</mtg:Value>'
	xmlString += '</mtg:Property>'
	xmlString += '</mtg:Properties>'
	xmlString += '</mtg:MaltegoEntity>'
	return xmlString

def createNodeUrl(displayName,url):
        xmlString = '<mtg:MaltegoEntity xmlns:mtg="http://maltego.paterva.com/xml/mtgx" type="maltego.URL">'
        xmlString += '<mtg:Properties>'
        xmlString += '<mtg:Property displayName="'+displayName+'" hidden="false" name="short-title" nullable="true" readonly="false" type="string">'
        xmlString += '<mtg:Value>'+displayName+'</mtg:Value>'
        xmlString += '</mtg:Property>'
        xmlString += '<mtg:Property displayName="'+displayName+'" hidden="false" name="url" nullable="true" readonly="false" type="url">'  
        xmlString += '<mtg:Value>'+displayName+'</mtg:Value>'
        xmlString += '</mtg:Property>'
        xmlString += '<mtg:Property displayName="Title" hidden="false" name="title" nullable="true" readonly="false" type="string">'
        xmlString += '<mtg:Value/>'    
        xmlString += '</mtg:Property>'
        xmlString += '</mtg:Properties>'
        xmlString += '</mtg:MaltegoEntity>'
	return xmlString

def createNodeLocation(lat,lng):
	xmlString = '<mtg:MaltegoEntity xmlns:mtg="http://maltego.paterva.com/xml/mtgx" type="maltego.Location">'
	xmlString += '<mtg:Properties>'
	xmlString += '<mtg:Property displayName="Name" hidden="false" name="location.name" nullable="true" readonly="false" type="string">'
	xmlString += '<mtg:Value>lat='+str(lat)+' lng='+str(lng)+'</mtg:Value>'
	xmlString += '</mtg:Property>'
	xmlString += '<mtg:Property displayName="Area Code" hidden="false" name="location.areacode" nullable="true" readonly="false" type="string">'
	xmlString += '<mtg:Value/>'
	xmlString += '</mtg:Property>'
	xmlString += '<mtg:Property displayName="Area" hidden="false" name="location.area" nullable="true" readonly="false" type="string">'
	xmlString += '<mtg:Value/>'
	xmlString += '</mtg:Property>'
	xmlString += '<mtg:Property displayName="Latitude" hidden="false" name="latitude" nullable="true" readonly="false" type="float">'
	xmlString += '<mtg:Value/>'
	xmlString += '</mtg:Property>'
	xmlString += '<mtg:Property displayName="Longitude" hidden="false" name="longitude" nullable="true" readonly="false" type="float">'
	xmlString += '<mtg:Value/>'
	xmlString += '</mtg:Property>'
	xmlString += '<mtg:Property displayName="Country" hidden="false" name="country" nullable="true" readonly="false" type="string">'
	xmlString += '<mtg:Value/>'
	xmlString += '</mtg:Property>'
	xmlString += '<mtg:Property displayName="Country Code" hidden="false" name="countrycode" nullable="true" readonly="false" type="string">'
	xmlString += '<mtg:Value/>'
	xmlString += '</mtg:Property>'
	xmlString += '<mtg:Property displayName="City" hidden="false" name="city" nullable="true" readonly="false" type="string">'
	xmlString += '<mtg:Value/>'
	xmlString += '</mtg:Property>'
	xmlString += '<mtg:Property displayName="Street Address" hidden="false" name="streetaddress" nullable="true" readonly="false" type="string">'	
	xmlString += '<mtg:Value/>'
	xmlString += '</mtg:Property>'
	xmlString += '</mtg:Properties>'
	xmlString += '</mtg:MaltegoEntity>'
	return xmlString

def cleanUpGraph(filename):
	newContent = []
	with open(filename) as f:
		content = f.readlines()
		for i in content:
			if '<key attr.name="node" attr.type="string" id="node"/>' in i:
				i = i.replace('name="node" attr.type="string"','name="MaltegoEntity" for="node"')
			if '<key attr.name="link" attr.type="string" id="link"/>' in i:
				i = i.replace('name="link" attr.type="string"','name="MaltegoLink" for="edge"')
			i = i.replace("&lt;","<")
			i = i.replace("&gt;",">")
			i = i.replace("&quot;",'"')
			print i.strip()
			newContent.append(i.strip())

	f = open(filename,'w')
	for item in newContent:
		f.write("%s\n" % item)
	f.close()
	        	
def createGoogleMap(dataList,lat,lng):
	html = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
	html += '<html xmlns="http://www.w3.org/1999/xhtml">'
	html += '<head>'
	html += '<title>Google Maps Example</title>'
	html += "<script src='http://code.jquery.com/jquery.min.js' type='text/javascript'></script>"
	html += '</head>'
	html += '<body>'
	html += '<script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script>'
	html = ''
	html += '<script type="text/javascript">'
	html += 'var infowindow = null;'
	html += ' $(document).ready(function () { initialize();  });'
	html += '    function initialize() {'
	html += '        var centerMap = new google.maps.LatLng('+str(lat)+','+str(lng)+');'
	html += '        var myOptions = {'
	html += '            zoom: 14,'
	html += '            center: centerMap,'
	html += '            mapTypeId: google.maps.MapTypeId.ROADMAP'
	html += '        }\n'
	html += '        var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);'
	html += '	  var marker = new google.maps.Marker({'
	html += '      	  	position: centerMap,'
	html += '     		map: map,'
	html += '		title: "Checkpoint"'
	html += '	  });'
	html += '        setMarkers(map, sites);'
	html += '	    infowindow = new google.maps.InfoWindow({'
	html += '                content: "loading..."'
	html += '            });'
	html += '        var bikeLayer = new google.maps.BicyclingLayer();'
	html += '		bikeLayer.setMap(map);'
 	html += '   }'
	html += '   var sites = ['
	
	for i in dataList:	
		popupHtml = ''
		popupHtml += i[0]+'<br>'
		popupHtml += i[1]+','+i[2]+'<br>'
		moreInfo = i[4]
		popupHtml += moreInfo.decode('utf-8')
		popupHtml = popupHtml.replace('\n',' ').replace('\r',' ')
		
		if len(i[3].strip())<1:
			i[3] = 'http://img820.imageshack.us/img820/9217/gtz7.png'
			#i[3]='https://maps.google.com/mapfiles/kml/shapes/man.png'
		#point = '["'+i[0]+'","'+i[1]+'","'+i[2]+'","'+i[3]+'",'"+popupHtml+"'],"
		point = "['"+i[0]+"',"+i[1]+","+i[2]+" ,'"+i[3]+"','"+popupHtml+"'],"
		#point = "['"+i[0]+"',"+i[1]+","+i[2]+" ,'"+i[3]+"','"+str(normalize(popupHtml.encode('ascii','replace')))+"'],"
		#point = "['"+i[0]+"',"+i[1]+","+i[2]+" ,'"+i[3]+"',''],"
		#point = "[\""+str(normalize(i[0].encode('ascii','replace')))+"\","+str(normalize(i[1].encode('ascii','replace')))+","+str(normalize(i[2].encode('ascii','replace')))+" ,'"+str(normalize(i[3].encode('ascii','replace')))+"','"+str(normalize(popupHtml.encode('ascii','replace')))+"'],"
		html += point	
			
	html += '    ];'

	html += '    function setMarkers(map, markers) {'
	html += '        for (var i = 0; i < markers.length; i++) {'
	html += '            var sites = markers[i];'
	html += '            var siteLatLng = new google.maps.LatLng(sites[1], sites[2]);'
	html += ' 	     var myIcon = {'
	html += '		url : sites[3],'
	html += '		size: new google.maps.Size(60,60)'
	html += '	     };'
	html += '            var marker = new google.maps.Marker({'
	html += '                position: siteLatLng,'
	html += '                map: map,'
	html += '                title:sites[0],'
	html += '                html: sites[4],'
	html += '	         icon: myIcon'
	html += '            });'
	html += '            var contentString = "Some content";'
	html += '            google.maps.event.addListener(marker, "click", function () {'
	html += '                infowindow.setContent(this.html);'
	html += '                infowindow.open(map, this);'
	html += '            });'
	html += '        }'
	html += '    }'
	html += '</script>'
	html += '<div id="map_canvas" style="width: 800px; height: 600px;"></div>'

	"""
	html += '</body>'
	html += '</html>'
	"""
	return html
	
def uploadGoogleDocs(fullPath,file_type):
	collection = google_drive_collection 		
	fhandle = open(fullPath)
	file_size = os.path.getsize(fhandle.name)
	directory,filename = os.path.split(fullPath)
	print '[*] Uploading: '+filename+' to Google Docs!'
	docsclient = gdata.docs.client.DocsClient(source='RPi Python-GData 2.0.17')
	print '[*] Logging in...',
	try:
	    docsclient.ClientLogin(google_username, google_password, docsclient.source);
	except (gdata.client.BadAuthentication, gdata.client.Error), e:
	    sys.exit('Unknown Error: ' + str(e))
	except:
	    sys.exit('Login Error, perhaps incorrect username/password')
	print 'Login success!'
        uri = 'https://docs.google.com/feeds/upload/create-session/default/private/full'
        print 'Fetching collection ID...',
        try:
                resources = docsclient.GetAllResources(uri='https://docs.google.com/feeds/default/private/full/-/folder?title=' + collection + '&title-exact=true')
        except:
                sys.exit('ERROR: Unable to retrieve resources')
        # If no matching resources were found
        if not resources:
                sys.exit('Error: The collection "' + collection + '" was not found.')
        uri = resources[0].get_resumable_create_media_link().href
        print 'success!'
        uri += '?convert=false'
        print 'Starting uploading of file...',
        uploader = gdata.client.ResumableUploader(docsclient, fhandle, file_type, file_size, chunk_size=1048576, desired_class=gdata.data.GDEntry)
        new_entry = uploader.UploadFile(uri, entry=gdata.data.GDEntry(title=atom.data.Title(text=os.path.basename(fhandle.name))))
        print 'Upload success!'

def checkGoogleDocsExist(filename):
	print '[*] Checking Google Docs if File Exists'
	docsclient = gdata.docs.client.DocsClient(source='RPi Python-GData 2.0.17')
	# Get a list of all available resources (GetAllResources() requires >= gdata-2.0.15)
	print '[*] Logging in...',
	try:
	    docsclient.ClientLogin(google_username, google_password, docsclient.source);
	except (gdata.client.BadAuthentication, gdata.client.Error), e:
	    sys.exit('[!] Unknown Error: ' + str(e))
	except:
	    sys.exit('[!] Login Error, perhaps incorrect username/password')
	print 'Login success!'

        q = gdata.docs.client.DocsQuery(
            title=filename,
            title_exact='true',
            show_collections='true'
        )
        client = gdata.docs.service.DocsService()
        client.ClientLogin(google_username,google_password)
        try:
                folder = docsclient.GetResources(q=q).entry[0]
        except IndexError:
                print '[*] File does not exists!'
                return False
        cprint('[!] File: '+filename+' exists!','white')
        #print '[!] File: '+filename+' exists!'
        return True

def changePublicGoogleDocs(filename):
	print '[*] Change: '+filename+' Access to Public'
	docsclient = gdata.docs.client.DocsClient(source='RPi Python-GData 2.0.17')
	# Get a list of all available resources (GetAllResources() requires >= gdata-2.0.15)
	print '[*] Logging in...',
	try:
	    docsclient.ClientLogin(google_username, google_password, docsclient.source);
	except (gdata.client.BadAuthentication, gdata.client.Error), e:
	    sys.exit('Unknown Error: ' + str(e))
	except:
	    sys.exit('Login Error, perhaps incorrect username/password')
	print 'Login success!'

        q = gdata.docs.client.DocsQuery(
            title=filename,
            title_exact='true',
            show_collections='true'
        )
        client = gdata.docs.service.DocsService()
        client.ClientLogin(google_username,google_password)
        folder = docsclient.GetResources(q=q).entry[0]
        #print docsclient.GetResource(folder).title.text
        #print docsclient.GetResource(folder).resource_id.text
        resource_id = docsclient.GetResource(folder).resource_id.text
        acl_feed = docsclient.GetResourceAcl(folder)
        for acl in acl_feed.entry:
              print acl.role.value, acl.scope.type, acl.scope.value
        acl1 = gdata.docs.data.AclEntry(
                scope=gdata.acl.data.AclScope(value='', type='default'),
                role=gdata.acl.data.AclRole(value='reader'),
                batch_operation=gdata.data.BatchOperation(type='insert'),
        )
        acl_operations = [acl1]
        docsclient.BatchProcessAclEntries(folder, acl_operations)
        print 'Permissions change success!'
        return docsclient.GetResource(folder).resource_id.text

def loginWigle(wigle_username,wigle_password):
	payload = {
		'credential_0': wigle_username,
		'credential_1': wigle_password,
		'destination': '%2Fgps%2Fgps%2Fmain',
		'noexpire': 'on'
	}
	headers = {
		"Content-Type": "application/x-www-form-urlencoded",
		"Connection": "keep-alive",
		"Host": "wigle.net",
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:24.0) Gecko/20100101 Firefox/24.0",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Accept-Language": "en-US,en;q=0.5",
		"Accept-Encoding": "1",
		"Referer":"https://wigle.net/",
		"Content-Length": "85"
	}
	with session() as c:
		request = c.post('https://wigle.net//gps/gps/main/login', data=payload, headers=headers)
	wigle_cookie = request.headers.get('Set-Cookie')
	return wigle_cookie

def wigleHTML(inputHTML):
	html = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
	html += '<html xmlns="http://www.w3.org/1999/xhtml">'
	html += '<head>'
	html += '<title>Wigle Maps Export</title>'
	html += "<script src='http://code.jquery.com/jquery.min.js' type='text/javascript'></script>"
	html += '</head>'
	html += '<body>'
	html += '<script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script>'
	html += inputHTML
	html += '</body>'
	html += '</html>'
	text_file = open('wigle.html', "w")
	text_file.write(html)
	text_file.close()

def convertWigle2KML(filename):
	print "[*] Convert Wigle Database to KML format"
	f = open(filename,"r")
	data = f.readlines()
	infrastructureList = []
	adhocList = []
	wepList = []
	nowepList = []
	count=0
	for row in data:
		try: 
			if count>1:
				splitString = row.split('~')
				bssid = splitString[1]
				ssid = splitString[0]
				channel = splitString[15]
				coordinates = splitString[12]+","+splitString[11]
				qos = splitString[18].strip()
				lastseen = splitString[8]
				type = splitString[4]
				wep = splitString[10]					

				newAP = "<Placemark>\n<description>\n<![CDATA[\nSSID: "+ssid+"<BR>\n"
				newAP += "BSSID: "+bssid+"<BR>\n"
				newAP += "TYPE: "+type+"<BR>\n"
				newAP += "WEP: "+wep+"<BR>\n"
				newAP += "CHANNEL: "+channel+"<BR>\n"
				newAP += "QOS: "+qos+"<BR>\n"	
				newAP += "Last Seen: "+lastseen+"\n"
				if wep=="Y":
					newAP += "]]>\n</description>\n<name><![CDATA["+ssid+"]]></name>\n<Style>\n<IconStyle>\n<Icon>\n<href>http://irongeek.com/images/wapwep.png</href>\n</Icon>\n</IconStyle>\n</Style>\n<Point id='1'>\n<coordinates>"+coordinates+"</coordinates>\n</Point>\n</Placemark>"	
				else:
					newAP += "]]>\n</description>\n<name><![CDATA["+ssid+"]]></name>\n<Style>\n<IconStyle>\n<Icon>\n<href>http://irongeek.com/images/wap.png</href>\n</Icon>\n</IconStyle>\n</Style>\n<Point id='1'>\n<coordinates>"+coordinates+"</coordinates>\n</Point>\n</Placemark>"	
				newAP += "\n"
				
				if wep=="Y":			
					wepList.append(newAP)	
				else:
					nowepList.append(newAP)
			count+=1
		except IndexError:
			continue
	f.close()
	filenameParts = filename.split(".dat")
	newFilename = filenameParts[0]+".kml"
	print "[*] Convert wigle database to: "+str(newFilename)
	f = open(newFilename,"w")
	f.write('<?xml version="1.0" encoding=\"UTF-8\"?><kml xmlns=\"http://earth.google.com/kml/2.0\"><Folder><name>WiGLE Data</name><open>1</open>\n')
	f.write('<Folder><name>WEP</name><open>1</open>')
	for i in wepList:
		f.write(i)
	f.write('</Folder>\n')
	f.write('<Folder><name>No WEP</name><open>1</open>')
	for i in nowepList:
		f.write(i)
	f.write('</Folder>\n')
	f.write("</Folder></kml>")
	f.close()

def lookupMacAddress(macAddr):
	resultList = {}
	url = 'http://hwaddress.com/?q='+str(macAddr)
	#url = 'http://hwaddress.com/?q='+urllib.urlencode(str(macAddr))
	r = requests.get(url)
	html = r.content
	soup = BeautifulSoup(html)
	htmlBox1 = soup.find('table',attrs={'class':'framedlight'})
	soup2 = BeautifulSoup(str(htmlBox1))
	htmlBox2 = soup2.findAll('a',text=True)
	try:
		if len(htmlBox2)>1:
			return htmlBox2[14]
	except TypeError as e:
		pass
def parseWigleDat(filename):
	print "[*] Extracting MAC addresses from Wigle database: "+filename
	global report
	report += '\n\n[*] Wireless Access Points Database from Wigle'
	tempList = []
	macAddrDict = {}
	with open(filename) as f:
		content = f.readlines()
	counter=0
	for i in content:
		if counter>0:
			macAddr = i.split('~')[0][0:8]
			if macAddr not in tempList:
				tempList.append(macAddr)
		counter+=1
	for i in tempList:
		#print "[*] Looking for vendor name: "+str(i)

		c = conn.cursor()
		c.execute('select manufacturer from macAddress where macAddress=?',(str(i),))
		dataList1 = []
		dataList1 = c.fetchone()
		if dataList1 != None:
			print "[*] Retrieving match for vendor name: "+str(dataList1[0])
			macAddrDict[i] = str(dataList1[0])
		else:
			vendorName =lookupMacAddress(i)
			if vendorName!=None:
				print "Found vendor name: "+str(i)+" - "+str(vendorName)
				tmpList = []
				tmpList.append([str(i),str(vendorName)])
				write2Database('macAddress',tmpList)
				macAddrDict[i] = vendorName
	for k,v in macAddrDict.items():
		print "[*] "+k, 'corresponds to', v
	counter=0
	for i in content:
		if counter>0:
			locLat = i.split('~')[11]
			locLng = i.split('~')[12]
			global lat, lng
			pt1 = geopy.Point(lat, lng)
			pt2 = geopy.Point(locLat, locLng)
			dist = geopy.distance.distance(pt1, pt2).meters
			global 	wirelessAPData
			if i.split('~')[4]!='infra':
				resultStr = i.split('~')[4]+'\t'+i.split('~')[0]+'\t'+i.split('~')[11]+', '+i.split('~')[12]+'\t\t'+str(dist)+' meters'+'\t'+str(macAddrDict.get(i.split('~')[0][0:8]))	
				wirelessAPData += '\n'+str(resultStr)
				report += '\n'+resultStr
				cprint(resultStr,'white')
			else:
				resultStr = i.split('~')[4]+'\t'+i.split('~')[0]+'\t'+i.split('~')[11]+', '+i.split('~')[12]+'\t\t'+str(dist)+' meters'+'\t'+str(macAddrDict.get(i.split('~')[0][0:8]))
				wirelessAPData += '\n'+str(resultStr)
				report += '\n'+resultStr
				print resultStr
		counter+=1

	"""
	locLat = i.split('~')[11]
	locLng = i.split('~')[12]
	global lat, lng
	pt1 = geopy.Point(lat, lng)
	pt2 = geopy.Point(locLat, locLng)
	dist = geopy.distance.distance(pt1, pt2).meters
	tempMacAddr =lookupMacAddress(macAddr)
	try:
			print i.split('~')[4]+'\t'+i.split('~')[0]+'\t'+i.split('~')[11]+', '+i.split('~')[12]+'\t\t'+str(dist)+' meters'+'\t'+tempMacAddr
	except TypeError as e:
		continue
		counter+=1
	"""
	
def downloadWigle(lat,lng,wigle_cookie):
	print "[*] Downloading Wigle database from Internet"
	variance=0.002
	lat1 = str(float(lat)+variance)
	lat2 = str(float(lat)-variance)
	lgn1 = str(float(lng)-variance)
	lgn2 = str(float(lng)+variance)
	currentYear = date.today().year-1	
	h = httplib2.Http(".cache")
	url = "http://wigle.net/gpsopen/gps/GPSDB/confirmquery/?variance="+str(variance)+"&latrange1="+lat1+"&latrange2="+lat2+"&longrange1="+lgn1+"&longrange2="+lgn2+"&lastupdt="+str(currentYear)+"0101000000&credential_0="+wigle_username+"&credential_1="+wigle_password+"&simple=true"	
	filename = str(lat)+"_"+str(lng)+".dat"
	newFilename = filename.split(".dat")[0]+".kml"
	if os.path.lexists(filename) and not os.path.lexists(newFilename):
		print "[*] File exists: "+filename
		print "[*] File not exists: "+newFilename
		convertWigle2KML(filename)
	if not os.path.lexists(filename):
		cookie = wigle_cookie
		if cookie!=None:
			resp, content = h.request(url, "GET")
			headers = {'Cookie': cookie}
			resp, content = h.request(url, "GET",headers=headers)
			if "too many queries" not in content:
				print "[*] Saving wigle database to: "+str(filename)
				f = open(filename,"w")
				f.write(content)
				f.close()
				print "[*] Converting Wigle database to KML format."
				convertWigle2KML(filename)
			else:
				print "[*] Please try again later"
		else:
			url = "http://wigle.net/gpsopen/gps/GPSDB/confirmquery/?variance="+str(variance)+"&latrange1="+lat1+"&latrange2="+lat2+"&longrange1="+lgn1+"&longrange2="+lgn2+"&lastupdt="+str(currentYear)+"0101000000&credential_0="+wigle_username+"&credential_1="+wigle_password+"&simple=true"
			resp, content = h.request(url, "GET")
			headers = {'Cookie': resp['set-cookie']}
			headers = {'Cookie': cookie}
			resp, content = h.request(url, "GET",headers=headers)
	if os.path.lexists(filename):
		print "[*] Wigle database already exists: "+filename		
	fullPath = os.getcwd()+"/"+newFilename
	fhandle = open(fullPath)
	file_size = os.path.getsize(fhandle.name)
	file_type='application/vnd.google-earth.kml+xml'
	directory,filename = os.path.split(fullPath)
	if not checkGoogleDocsExist(newFilename):
		file_type='application/vnd.google-earth.kml+xml'
	        uploadGoogleDocs(fullPath,file_type)
	resourceID = (changePublicGoogleDocs(newFilename)).strip("file:")
	mapLink = "http://maps.google.com/maps?q=docs://"+resourceID+"&output=embed"
	html = ''
	html += '<iframe width="800" height="600" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="'+mapLink+'"></iframe><br /><small><a href="'+mapLink+'" style="color:#0000FF;text-align:left">View Larger Map</a></small>'
	return html
	
def address2geocoordinate(address):
        results = Geocoder.geocode(address)
        return results[0].coordinates[0],results[0].coordinates[1]

def retrieveGoogleResults(username):
	global report
	report += '\n\n[*] Google Search Results for: '+str(username)
	results = []
	keyword = username
	tmpStr = "\n************ Google Search Results for "+username+" ************\n"
	print tmpStr
	try:
		for url in search(keyword, stop=20):
			results.append(url)
		google.cookie_jar.clear()
		for i in results:
			print i
			tmpStr += i+'\n'
			report += '\n'+str(normalize(i))
		print "\n"
		return tmpStr
	except urllib2.HTTPError:
		return ""
def retrieveLinkedinData(username):
	print '\n[*] Searching on Linkedin for: '+username
	global report
	if " " in username:
		firstname, lastname = username.split(" ")
	else:
		firstname = username
		lastname = ""
	consumer = oauth.Consumer(linkedin_api_key, linkedin_api_secret)
	access_token = oauth.Token(
	            key=linkedin_oauth_user_token,
	            secret=linkedin_oauth_user_secret)
	client = oauth.Client(consumer, access_token)

	resp, content = client.request("http://api.linkedin.com/v1/people-search?first-name="+firstname+"&last-name="+lastname,"GET","")
	if resp['status']=="200":
		report += "\n\n[*] Linkedin Search Results"
		report += '\nUsername: '+username
		RETURN_URL = "http://127.0.0.1"	
		authentication = linkedin.LinkedInDeveloperAuthentication(linkedin_api_key, linkedin_api_secret,
	                                                          linkedin_oauth_user_token, linkedin_oauth_user_secret,
	                                                          RETURN_URL, linkedin.PERMISSIONS.enums.values())
		application = linkedin.LinkedInApplication(authentication)
		peopleIDList = []
		userList = []	

		count = 10	
		total = 30
		start = 0
		while count<total:
			results =  application.search_profile(selectors=[{'people': ['first-name', 'last-name', 'id', 'headline', 'picture-url']}], params={'first-name': firstname, 'last-name': lastname,'count': 25, 'start': 0})
			total = int(results['people']['_total'])					
			for x in results['people']['values']:
				print x['headline']
				peopleIDList.append([x['id'],x['headline'],x['firstName'],x['lastName']])
			start+=25
			count+=25		

		for x in peopleIDList:
			resp,content = client.request("http://api.linkedin.com/v1/people/id="+str(x[0]), "GET", "")
			
			xmldoc = minidom.parseString(content)
			firstnameResult = xmldoc.getElementsByTagName('first-name') 
			lastnameResult = xmldoc.getElementsByTagName('last-name') 
			headlineResult = xmldoc.getElementsByTagName('headline') 
			urlResult = xmldoc.getElementsByTagName('url') 
			url = " ".join(t.nodeValue for t in urlResult[0].childNodes if t.nodeType == t.TEXT_NODE)
			r = re.compile('id=(.*?)&authType')
			m = r.search(url)
			if m:
				id = m.group(1)
				mobileUrl = "https://touch.www.linkedin.com/#profile/"+id
				userList.append([[0],x[1],x[2],x[3],mobileUrl])			

		driver = webdriver.Chrome()
		driver.get("https://touch.www.linkedin.com/login.html")
		driver.find_element_by_id('username').send_keys(linkedin_username)
		driver.find_element_by_id('password').send_keys(linkedin_password)
		WebDriverWait(driver, 60).until(lambda driver :driver.find_element_by_id('login-button'))
		driver.find_element_by_id("login-button").click()
		if "session" not in driver.current_url:
			time.sleep(1)
		checkWorking = ""
		for user in userList:	
			mobileUrl = user[4]	
			if user[3].lower()!="private":
				#resp = requests.head(mobileUrl)
				#print resp.status_code
				#if resp.status_code=="200":
				driver.get(mobileUrl)
				#WebDriverWait(driver, 10).until(lambda driver :driver.find_element_by_class_name('profile-photo'))
				WebDriverWait(driver, 60).until(lambda driver :driver.find_element_by_class_name('profile-photo'))
				time.sleep(5)
				
				report += '\nFull name: '+user[2]+' '+user[3]
				report += '\nHeadline: '+user[1]
				report += '\nUrl: '+user[4]
				
				WebDriverWait(driver, 60).until(lambda driver :driver.find_element_by_xpath('//*[@id="profile-view-scroller"]/div/div[2]/div[3]/section[1]'))
				try:
					location = driver.find_element_by_xpath('//*[@id="profile-view-scroller"]/div/div[1]/div[2]/div[1]/div/div[2]/h4/span[1]').text
					industry = driver.find_element_by_xpath('//*[@id="profile-view-scroller"]/div/div[1]/div[2]/div[1]/div/div[2]/h4/span[2]').text
					report += '\nLocation: '+location+'\n'
					report += '\nIndustry: '+industry+'\n\n'
					working = driver.find_element_by_xpath('//*[@id="profile-view-scroller"]/div/div[2]/div[3]/section[1]').text
					if len(checkWorking)!=len(working):
						profilePic = driver.find_element_by_class_name('profile-photo').get_attribute("src")
						print profilePic
						report += '\nProfile Picture: '+profilePic
						checkWorking = working
						tempWorking = working.split("\n")	
						#print len(tempWorking[2:len(tempWorking)])
						tempWorking1 = tempWorking[2:len(tempWorking)]
						count=1
						while count<len(tempWorking1):
							print tempWorking[count]+"\t"+tempWorking[count+1]+"\t"+tempWorking[count+2]
							count+=3	
				except:
					continue
			try:
				education = driver.find_element_by_xpath('//*[@id="profile-view-scroller"]/div/div[2]/div[3]/section[2]').text
				#print education.split("\n")
			except:
				continue
			time.sleep(2)

def retrieveInstagramData(lat,lng):
	global report
	report += '[*] Instagram Search Results'
	print "\n[*] Downloading Instagram Data based on Geolocation"
	count=50
	api = InstagramAPI(access_token=instagram_access_token)
	mediaList = api.media_search(count=count, lat=lat, lng=lng)
	instagramMediaList = []
	for media in mediaList:
		username = str(normalize(media.user.username)).replace("'","\\'")
		global globalUserList
		username = str(normalize(username))
		if username not in globalUserList:
			globalUserList.append(username)
		username = 'http://instagram.com/'+username
		print '[*] Found '+str(username)+'\t('+str(media.location.point.latitude)+','+str(media.location.point.longitude)+")"
		report+="\nFound: "+str(media.images['thumbnail'].url)
		report+="\nUsername: "+str(username)
		report+="\nGeolocation "+str(media.location.point.latitude)+','+str(media.location.point.longitude)+'\n'
		instagramMediaList.append([str(username),str(media.location.point.latitude),str(media.location.point.longitude),media.images['thumbnail'].url,lat,lng])
	return instagramMediaList
	

def retrieveFlickrData(lat,lng):
	print "\n[*] Downloading Flickr Data Based on Geolocation"
	global report
	report += '\n[*] Flickr Search Results'
	resultsList = []
	import flickrapi
	h = httplib2.Http(".cache")
	flickr = flickrapi.FlickrAPI(flickr_key)
	retries=0
	while (retries < 3):
		try:
			photos = flickr.photos_search(lat=lat,lon=lng,accuracy='16',radius='1',has_geo='1',per_page='50')
			break
		except:
			cprint('[!] Flickr Error: Retrying.','white')
		retries = retries + 1

	print "[*] Continue Downloading Flickr Data"
	for i in photos[0]:
		url = 'http://www.flickr.com/photos/'+i.get('owner')+'/'+i.get('id')
		resp, content = h.request(url, "GET")
		soup = BeautifulSoup(str(content))
		
		geoLocUrl = 'http://www.flickr.com/photos/'+i.get('owner')+'/'+i.get('id')+'/meta'
		resp, content = h.request(geoLocUrl, "GET")
		root = lxml.html.fromstring(content)
			
		doc = lxml.html.document_fromstring(content)
		photoLat = doc.xpath('//*[@id="main"]/div[2]/table[2]/tbody/tr[26]/td/text()')
		photoLng= doc.xpath('//*[@id="main"]/div[2]/table[2]/tbody/tr[27]/td/text()')

		if photoLat and 'deg' in str(photoLat[0]) and 'deg' in str(photoLng[0]):
			newPhotoLat = photoLat[0].replace('deg','').replace("'","").replace('"','').split(' ')
			newPhotoLng = photoLng[0].replace('deg','').replace("'","").replace('"','').split(' ')
			photoLatStr = str(float(newPhotoLat[0])+float(newPhotoLat[2])/60+float(newPhotoLat[3])/3600)
			photoLngStr = str(float(newPhotoLng[0])+float(newPhotoLng[2])/60+float(newPhotoLng[3])/3600)

			#photoLatStr = str(float(newPhotoLat[0])+float(newPhotoLat[2])/60+float(newPhotoLat[3])/3600)
			#photoLngStr = str(float(newPhotoLng[0])+float(newPhotoLng[2])/60+float(newPhotoLng[3])/3600)

			pt1 = geopy.Point(lat, lng)
			pt2 = geopy.Point(photoLatStr, photoLngStr)
			dist = geopy.distance.distance(pt1, pt2).meters

			outputStr = '[*] Found Matching Geocoordinates in Flickr Data: ('+str(photoLatStr)+','+str(photoLngStr)+')\t'+str(dist)+' meters'
			report += '\n'+outputStr
			#print geoLocUrl
		
			userName = soup.find('span',attrs={'class':'photo-name-line-1'})
			#print userName.text
			
			cameraModel = root.cssselect("html body.zeus div#main.clearfix div.photo-data table tbody tr.lookatme td a")
			if cameraModel:
				cameraModelText = cameraModel[0].text
			else:
				cameraModelText = ''
			
			#url #title #username #cameraModel #latitude #longitude
			url1 = 'http://www.flickr.com/photos/'+str(i.get('owner'))+'/'+str(i.get('id'))
			description = i.get('title')
			resultsList.append([normalize(url1),normalize(description),str(normalize(userName.text)),cameraModelText,normalize(photoLatStr),normalize(photoLngStr),lat,lng])
			print outputStr
	return resultsList
	
def googlePlusSearch(username):
	global report       		
	print "\n[*] Searching Google+ for Possible Matches: "+username
	googlePlusUserList = []
	username = urllib.quote_plus(username)
	url = 'https://plus.google.com/s/'+username+'/people'	
	r = requests.get(url)
	html = r.content
	root = lxml.html.fromstring(html)
	count = 0
	e1 = root.cssselect("html body.je div.NPa div#content.maybe-hide div.z2a div.Kxa div#contentPane.jl div.o-B-Qa div.LE div.wfe div.iSd div.Yyd div.tec div.Nxc div.vtb div.bae div.Xce div.uec div.ge div.Sxa a.T7a")
	e2 = root.cssselect("html body.je div.NPa div#content.maybe-hide div.z2a div.Kxa div#contentPane.jl div.o-B-Qa div.LE div.wfe div.iSd div.Yyd div.tec div.Nxc div.vtb div.bae div.Xce div.uec div.ge div.lkb a.lb img.ue")
	for x in e1:
		userName = x.text
		userID = x.get('href').strip('/')
		imageSrc = e2[count].get('src')
		if imageSrc.startswith('//'):
			imageSrc = 'https:'+imageSrc
		tmpStr = userName+'\thttps://plus.google.com/'+userID+'\t'+imageSrc
		print tmpStr
		report += "\n\n[*] Google+ Search Results"
		report += '\nUsername: '+userName
		report += '\nUrl: '+userID
		report += '\nProfile Picture: '+imageSrc
		googlePlusUserList.append([userName,userID,imageSrc])
		print "\nFound "+str(normalize(userName))
		count+=1
	return googlePlusUserList
	


def retrieve4sqOnTwitterResults():
	global report
	report += '\n\n[*] Retrieving Tweets for Foursquare Check In'
	print '\n\n[*] Retrieving Tweets for Foursquare Check In (Experiemental)'
	try:
		tmpList = []
		for element in foursqTwitterSearch:	
			geoLat = element[1]
			geoLng = element[2]	
			stripLoc = (element[0].replace('4sq.com/','')).strip()
			tso = TwitterSearchOrder() 	
			tso.setKeywords([stripLoc]) 
			tso.setCount(7) 
			tso.setIncludeEntities(False)
			ts = TwitterSearch(
				consumer_key = twitter_consumer_key,
				consumer_secret = twitter_consumer_secret,
				access_token = twitter_access_key ,
				access_token_secret = twitter_access_secret
			 )
			for tweet in ts.searchTweetsIterable(tso): 
				print tweet
				screenName = (normalize(tweet['user']['screen_name']))
				tweetMsg = normalize(tweet['text'])
				tmpStr = '@%s: %s' % (screenName, tweetMsg )
				global lat, lng
				geoLat = lat
				geoLng = lng

				report += '\n'+tmpStr.decode("utf8")
				tmpStr = '@%s: %s (%s,%s)' % (screenName, tweetMsg,geoLat,geoLng )
				print str(normalize(tmpStr.encode('ascii','ignore')))

				tweetText = ''
				try:	
					tweetText = tweet['text'].replace("'","\\'")
					tweetText = str(normalize(tweetText.encode('ascii','ignore')))
					#print tweetText
				except: 
					continue
				tmpList.append(['https://www.twitter.com/'+str(normalize(tweet['user']['screen_name'])),geoLat, geoLng,'',tweetText])
				global globalUserList
				if str(normalize(tweet['user']['screen_name'])) not in globalUserList:
					globalUserList.append(str(normalize(tweet['user']['screen_name'])))				
				tempList1 = []
				tempList1.append(['https://www.twitter.com/'+str(normalize(tweet['user']['screen_name'])),(tweet['text']).encode('ascii','ignore'),geoLat, geoLng ,lat,lng])	
				write2Database('twitter',tempList1)
		return tmpList
	except TwitterSearchException as e: 
		print(e)

def retrieveTwitterResults(lat,lng):
	lat = float(lat)
	lng = float(lng)
	global report
	try:
		start_time = time.time()
		report += '\n\n[*] Twitter Geolocation Search Results'
		print "\n[*] Retrieving Tweets Based on Geolocation"
		tso = TwitterSearchOrder() 
		tso.setGeocode(lat,lng,1)
		tso.setKeywords(['']) 
		tso.setCount(7) 
		tso.setIncludeEntities(False)
		ts = TwitterSearch(
			consumer_key = twitter_consumer_key,
			consumer_secret = twitter_consumer_secret,
			access_token = twitter_access_key ,
			access_token_secret = twitter_access_secret
		 )
		for tweet in ts.searchTweetsIterable(tso): 
			if time.time()>start_time+15.0:
			#if time.time()>start_time+30.0:
				break
			else:
				screenName = (normalize(tweet['user']['screen_name']))
				tweetMsg = normalize(tweet['text'])
				geoLat = ""
				geoLng = ""
				try:
					geoLat, geoLng = str(tweet['geo']['coordinates']).replace('[','').replace(']','').strip().split(',')
					geoLng = geoLng.strip()
				except TypeError:
						continue
				tmpStr = '@%s: %s (%s,%s)' % (screenName, tweetMsg,geoLat,geoLng )
				try:
					print str(normalize(tmpStr.encode('ascii','ignore')))
					report += '\n'+str(normalize(tmpStr.encode('ascii','ignore')))		

					tweetText = ''
					try:
						tweetText = tweet['text'].replace("'","\\'")
						tweetText = str(normalize(tweetText.encode('ascii','ignore')))
						print tweetText
					except: 
						continue
					global tweetList				
					#tweetList.append(['https://www.twitter.com/'+str(normalize(tweet['user']['screen_name'])),geoLat, geoLng,'',''])
					#tweetList.append(['https://www.twitter.com/'+str(normalize(tweet['user']['screen_name'])),geoLat, geoLng,'',tweetText])
					tweetList.append(['https://www.twitter.com/'+str(normalize(tweet['user']['screen_name'])),geoLat, geoLng,'',tweetText])

					global globalUserList
					if str(normalize(tweet['user']['screen_name'])) not in globalUserList:
						globalUserList.append(str(normalize(tweet['user']['screen_name'])))
	
					tempList1 = []
					#tempList1.append(['https://www.twitter.com/'+str(normalize(tweet['user']['screen_name'])),repr(zlib.compress(normalize(tweet['text']))),geoLat, geoLng ,lat,lng])	
					tempList1.append(['https://www.twitter.com/'+str(normalize(tweet['user']['screen_name'])),(tweet['text']).encode('ascii','ignore'),geoLat, geoLng ,lat,lng])	
					write2Database('twitter',tempList1)
				except UnicodeDecodeError:
					continue
	except TwitterSearchException as e: 
		print(e)
	except requests.exceptions.ConnectionError:
		cprint('[!] Connection issue. Continuing with next step.','white')
		pass
	print "[*] Writing twitter feed to database: twitter"
	
def retrieve4sqData(lat,lng):
	print "\n[*] Fetching Data from Foursquare"
	global report
	report += "\n[*] Foursquare Search Results"
	count = 20
	client = foursquare.Foursquare(client_id=foursquare_client_id, client_secret=foursquare_client_secret, redirect_uri='http://127.0.0.1/oauth/authorize')
	client.set_access_token(foursquare_access_token)
	list = []
	failedLinks = []
	geolocation = str(lat)+","+str(lng)
	failedLinks.append("https://foursquare.com/img/categories_v2/building/militarybase.png")
	failedLinks.append("https://foursquare.com/img/categories_v2/building/government.png")
	failedLinks.append("https://foursquare.com/img/categories_v2/building/government_monument.png")
	failedLinks.append("https://foursquare.com/img/categories_v2/building/apartment.png")
	failedLinks.append("https://foursquare.com/img/categories_v2/education/classroom.png")
	failedLinks.append("https://foursquare.com/img/categories_v2/building/eventspace.png")
	failedLinks.append("https://foursquare.com/img/categories_v2/building/office_conferenceroom.png")
	failedLinks.append("https://foursquare.com/img/categories_v2/shops/conveniencestore.png")	
	failedLinks.append("https://foursquare.com/img/categories_v2/shops/gym_martialarts.png")
	failedLinks.append("https://foursquare.com/img/categories_v2/parks_outdoors/sceniclookout.png")
	list = []
	data = client.venues.search(params={'ll': geolocation,'limit':count })
	for venue in data['venues']:
		location = client.venues(venue['id'])
		
		html = ''
		try:
			html += location['venue']['location']['address']+'<br>'
		except KeyError:
			continue
		html += '<a href=javascript:window.open("'+location['venue']['canonicalUrl']+'")>'+location['venue']['canonicalUrl']+'</a><br>'
		if len(venue['categories'])>0:
       		 	venueName = venue['name']
        	       	if len(venue['categories'][0]['pluralName'])>0:
       		         	categoryName = venue['categories'][0]['pluralName']
              		else:
                	  	categoryName = ""
                	icon = str(venue['categories'][0]['icon']['prefix'])[:-1]+venue['categories'][0]['icon']['suffix']
              		if icon not in failedLinks:
               			try:
                	        	f = urllib2.urlopen(urllib2.Request(icon))
                	      	except urllib2.HTTPError:
                	            #print icon
								failedLinks.append(icon)
								icon = 'http://foursquare.com/img/categories/none.png'
              		else:
                	  	icon = 'http://foursquare.com/img/categories/none.png'
		else:
					venueName = venue['name']
					icon = 'http://foursquare.com/img/categories/none.png'
		locLat = str(venue['location']['lat'])
		locLng = str(venue['location']['lng'])
       		
		pt1 = geopy.Point(lat, lng)
		pt2 = geopy.Point(locLat, locLng)
		dist = geopy.distance.distance(pt1, pt2).meters
		
		#Get short url for 4sq sites. Use this to search for 4sq checkins in Twitter
		r = requests.get('https://foursquare.com/v/venues/'+str(venue['id']))
		html = r.content
		soup2 = BeautifulSoup(html)
		shortUrl = soup2.find("input", {"class" : "shareLink formStyle"})
		global foursqTwitterSearch
		foursqTwitterSearch.append([shortUrl['value'].strip("http://"),locLat,locLng])
				
			       		
		report += "\nFound "+venueName+"\t"+"("+locLat+","+locLng+")"+"\t"+str(dist)+" meters"
		print "[*] Found "+venueName+"\t"+"("+locLat+","+locLng+")"+"\t"+str(dist)+" meters"
		point = "[\""+venueName+"\","+locLat+","+locLng+",'"+icon+"']"
		#print point
		venueName = venueName.replace("'","\\'")
		venueName = venueName.replace('"','\\"')
		html = html.replace("'","\\'")
		html = html.replace('"','\\"')
		list.append([venueName,locLat,locLng,icon,html])
	print ""
	report += "\n"
	return list			

def write2Database(dbName,dataList):
	try:
		#cprint("[*] Writing "+str(len(dataList))+" record(s) to database table: "+dbName,"white")
		numOfColumns = len(dataList[0])
		c = conn.cursor()
		if numOfColumns==3:
			for i in dataList:
				try:
					c.execute('INSERT INTO '+dbName+' VALUES (?,?,?)', i)
					conn.commit()
				except sqlite3.IntegrityError:
					continue
		if numOfColumns==2:
			for i in dataList:
				try:
					c.execute('INSERT INTO '+dbName+' VALUES (?,?)', i)
					conn.commit()
				except sqlite3.IntegrityError:
					continue
		if numOfColumns==4:
			for i in dataList:
				try:
					c.execute('INSERT INTO '+dbName+' VALUES (?,?,?,?)', i)
					conn.commit()
				except sqlite3.IntegrityError:
					continue
		if numOfColumns==5:
			for i in dataList:
				try:
					c.execute('INSERT INTO '+dbName+' VALUES (?,?,?,?,?)', i)
					conn.commit()
				except sqlite3.IntegrityError:
					continue
		if numOfColumns==6:
			for i in dataList:
				try:
					c.execute('INSERT INTO '+dbName+' VALUES (?,?,?,?,?,?)', i)
					conn.commit()
				except sqlite3.IntegrityError:
					continue
		if numOfColumns==7:
			for i in dataList:
				try:
					c.execute('INSERT INTO '+dbName+' VALUES (?,?,?,?,?,?)', i)
					conn.commit()
				except sqlite3.IntegrityError:
					continue
		if numOfColumns==8:
			for i in dataList:
				try:
					c.execute('INSERT INTO '+dbName+' VALUES (?,?,?,?,?,?,?,?)', i)
					conn.commit()
				except sqlite3.IntegrityError:
					continue
					
		if numOfColumns==9:
			for i in dataList:
				try:
					c.execute('INSERT INTO '+dbName+' VALUES (?,?,?,?,?,?,?,?,?)', i)
					conn.commit()
				except sqlite3.IntegrityError:
					continue
	except TypeError as e:
		print e
		pass
	except IndexError as e:
		print e
		pass

def usernameSearch(username):
	global report
	urlList = []
	urlList.append("https://www.facebook.com/"+username)
	urlList.append("https://www.youtube.com/user/"+username+"/feed")
	urlList.append("http://instagram.com/"+username)
	
	for url in urlList:
		print "\n[*] Searching for valid accounts: "+url
		resp = requests.head(url)
		#print resp.status_code, resp.text, resp.headers
		if resp.status_code==200:
			print "[*] Found: "+url
			report+= "\nFound :"+url
	print "\n[*] Searching for valid accounts on Google+"
	googlePlusSearch(username)
	if len(linkedin_oauth_user_token)>0:	
		print "\n[*] Searching for valid accounts on Linkedin"
		retrieveLinkedinData(username)
	
	print "\n[*] Searching for valid accounts on Google Search"
	retrieveGoogleResults(username)
	
def createMaltegoGeolocation():
	print "\n[*] Create Maltego Mtgx File..."		
	g = Graph()
	totalCount = 50
	start = 0
	nodeList = []
	edgeList = []

	while(start<totalCount):
       		nodeList.append("")	
	        edgeList.append("")
	        start+=1

	nodeList[0] = g.add_node('original')
	nodeList[0]['node'] = createNodeLocation(lat,lng)


	counter1=1
	counter2=0                
	userList=[]

	c = conn.cursor()
	c.execute('select distinct userName from instagram where origLat=? and origLng=?',(lat,lng,))
	dataList = c.fetchall()
	nodeUid = ""
	for i in dataList:
		if i[0] not in userList:
			userList.append(i[0])
			try:
			   	nodeList[counter1] = g.add_node("Instagram_"+str(i[0]))
   				nodeList[counter1]['node'] = createNodeUrl(i[0],str(i[0]))
   				edgeList[counter2] = g.add_edge(nodeList[0], nodeList[counter1])
   				edgeList[counter2]['link'] = createLink('Instagram')
    				nodeList.append("")
 		   		edgeList.append("")
    				counter1+=1
    				counter2+=1
			except IndexError:
				continue
				
	c = conn.cursor()
	c.execute('select distinct URL from flickr where origLat=? and origLng=?',(lat,lng,))
	dataList = c.fetchall()
	nodeUid = ""
	for i in dataList:
		if i[0] not in userList:
			userList.append(i[0])
			try:
			   	nodeList[counter1] = g.add_node("Flickr_"+str(i[0]))
   				nodeList[counter1]['node'] = createNodeUrl(i[0],str(i[0]))
   				edgeList[counter2] = g.add_edge(nodeList[0], nodeList[counter1])
   				edgeList[counter2]['link'] = createLink('Flickr')
    				nodeList.append("")
 		   		edgeList.append("")
    				counter1+=1
    				counter2+=1
			except IndexError:
				continue
				
	c = conn.cursor()
	c.execute('select distinct username from twitter where origLat=? and origLng=?',(lat,lng,))
	dataList = c.fetchall()
	nodeUid = ""
	for i in dataList:
		if i[0] not in userList:
			userList.append(i[0])
			try:
			   	nodeList[counter1] = g.add_node("Twitter1_"+str(i[0]))
   				nodeList[counter1]['node'] = createNodeUrl(i[0],str(i[0]))
   				edgeList[counter2] = g.add_edge(nodeList[0], nodeList[counter1])
   				edgeList[counter2]['link'] = createLink('Twitter_')
    				nodeList.append("")
 		   		edgeList.append("")
    				counter1+=1
    				counter2+=1
			except IndexError:
				continue
	parser = GraphMLParser()
	if not os.path.exists(os.getcwd()+'/Graphs'):
    		os.makedirs(os.getcwd()+'/Graphs')
	filename = 'Graphs/Graph1.graphml'
	parser.write(g, "Graphs/Graph1.graphml")
	cleanUpGraph(filename)
	filename = 'maltego_'+lat+'_'+lng+'.mtgx'
	print 'Creating archive: '+filename
	zf = zipfile.ZipFile(filename, mode='w')
	print 'Adding Graph1.graphml'
	zf.write('Graphs/Graph1.graphml')
	print 'Closing'
	zf.close()

def createMaltegoUsername():
	print "\n[*] Create Maltego Mtgx File..."		
	g = Graph()
	totalCount = 50
	start = 0
	nodeList = []
	edgeList = []

	while(start<totalCount):
       		nodeList.append("")	
	        edgeList.append("")
	        start+=1

	nodeList[0] = g.add_node('original')
	nodeList[0]['node'] = createNodeLocation(lat,lng)

	counter1=1
	counter2=0                
	userList=[]

	nodeUid = ""
	for i in globalUserList:
		i = i.encode('ascii','replace')
		print i
		try:
		   	nodeList[counter1] = g.add_node("Twitter1_"+str(i))
   			nodeList[counter1]['node'] = createNodeUrl(i,str(i))
   			edgeList[counter2] = g.add_edge(nodeList[0], nodeList[counter1])
   			edgeList[counter2]['link'] = createLink('Twitter_')
    			nodeList.append("")
 	   		edgeList.append("")
    			counter1+=1
    			counter2+=1
		except IndexError:
			continue
	parser = GraphMLParser()
	if not os.path.exists(os.getcwd()+'/Graphs'):
    		os.makedirs(os.getcwd()+'/Graphs')
	filename = 'Graphs/Graph1.graphml'
	parser.write(g, "Graphs/Graph1.graphml")
	cleanUpGraph(filename)
	filename = 'maltego1.mtgx'
	print 'Creating archive: '+filename
	zf = zipfile.ZipFile(filename, mode='w')
	print 'Adding Graph1.graphml'
	zf.write('Graphs/Graph1.graphml')
	print 'Closing'
	zf.close()

def usernameSearch(g):
	global report
	counter1=1
	counter2=0                
	userList=[]	
	counter3=0
	secondaryCount = 0

	global globalUserList			
	for username in globalUserList:
		username = str(normalize(username.encode('ascii','replace')))
		username = str(username)
		username = username.replace("(u'","")
		username = username.replace("',)","")

	       	googlePlusSearch(username)
	        if len(linkedin_oauth_user_token)>0:
	               	print "\n[*] Searching for valid accounts on Linkedin"
                	retrieveLinkedinData(username)

	        print "\n[*] Searching for valid accounts on Google Search"
		randNum = randint(10,20)
		print "Sleeping for "+str(randNum)+" seconds to prevent Google bot detection"
		time.sleep(randNum)

        	retrieveGoogleResults(username)


		nodeUid = ""

		url = str(username)
		nodeList[counter1] = g.add_node("Twitter2_"+str(url))
   		nodeList[counter1]['node'] = createNodeUrl(url,str(url))
   		edgeList[counter2] = g.add_edge(nodeList[0], nodeList[counter1])
   		edgeList[counter2]['link'] = createLink('Twitter')	

    		nodeList.append("")
 	   	edgeList.append("")	

		lastCounter = counter1
	    	counter1+=1
    		counter2+=1

		urlList = []
		urlList.append("https://www.facebook.com/"+username)
		urlList.append("https://www.youtube.com/user/"+username+"/feed")
		urlList.append("http://instagram.com/"+username)
		urlList.append("https://twitter.com/"+username)
		

		for url in urlList:
			#print "\n[*] Searching1 for valid accounts: "+url
			try:
				resp = requests.head(url)
				if resp.status_code==200:
					print "[*] Found: "+url
					report+= "\nFound :"+url
				   	nodeList[counter1] = g.add_node("Secondary_"+str(secondaryCount))
   					nodeList[counter1]['node'] = createNodeUrl(url,str(url))
   					edgeList[counter2] = g.add_edge(nodeList[lastCounter], nodeList[counter1])
   					edgeList[counter2]['link'] = createLink('Link_')
		    			nodeList.append("")
		 	   		edgeList.append("")  
 					counter1+=1
    					counter2+=1
					secondaryCount+=1
			except IndexError:
				continue
			except requests.exceptions.ConnectionError:
				continue
	parser = GraphMLParser()
	if not os.path.exists(os.getcwd()+'/Graphs'):
    		os.makedirs(os.getcwd()+'/Graphs')
	filename = 'Graphs/Graph1.graphml'
	parser.write(g, "Graphs/Graph1.graphml")

	cleanUpGraph(filename)
	filename = 'maltego3.mtgx'
	print 'Creating archive: '+filename
	zf = zipfile.ZipFile(filename, mode='w')
	print 'Adding Graph1.graphml'
	zf.write('Graphs/Graph1.graphml')
	print 'Closing'
	zf.close()
	
def geoLocationSearch(lat,lng):
	htmlfile = open("result.html", "w")
	html = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
	html += '<html xmlns="http://www.w3.org/1999/xhtml">'
	html += '<head>'
	html += '<title>Geostalker Tool Google Maps</title>'
	html += "<script src='http://code.jquery.com/jquery.min.js' type='text/javascript'></script>"
	html += '</head>'
	html += '<body>'
	html += '<script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script>'
	htmlfile.write(html)
	htmlfile.write('<br><b>Wireless Access Point Database Lookup from Wigle.net</b><br>')
	
	if len(wigle_username)>0:
		wigle_cookie = loginWigle(wigle_username, wigle_password)
		html1 = downloadWigle(lat,lng,wigle_cookie)    	
		htmlfile.write(html1)

		filename = str(lat)+'_'+str(lng)+'.dat'
		parseWigleDat(filename)
	gpsPoints = []
		
	#Foursquare Start
	if len(foursquare_access_token)>0:
		dataList = retrieve4sqData(lat,lng)
		gpsPoints.extend(dataList)

	#Instagram Start
	if len(instagram_access_token)>0:
		dataList = retrieveInstagramData(lat,lng)
		if dataList:
			gpsPoints.extend(dataList)
			write2Database('instagram',dataList)
	#Flickr Start
	if len(flickr_oauth_secret)>0:
		dataList1 = retrieveFlickrData(lat,lng)
		if len(dataList1)>0:
			write2Database('flickr',dataList1)
			html = ''
			for i in dataList1:
				html = '<a href="'+i[0]+'">'+i[0]+'</a><br>'+i[1]+'<br>'+i[3]+'<br>'+'<br>'
				html = html.encode('ascii','replace')
				gpsPoints.append([('http://www.flickr.com/photos/'+i[2]).encode('ascii','replace'),i[4].encode('ascii','encode'),i[5].encode('ascii','encode'),'',html])		
	#Twitter Start
	if len(twitter_access_secret)>0:
		retrieveTwitterResults(lat,lng)
		gpsPoints.extend(tweetList)
		time.sleep(5)
		tmpList = retrieve4sqOnTwitterResults()
		if tmpList:
			gpsPoints.extend(tmpList)
		
	html = createGoogleMap(gpsPoints,lat,lng)		
	#Twitter End

	print "\n[*] Create Google Map using Flickr/Instagram/Twitter Geolocation Data"		
	htmlfile.write('<br><br>')
	htmlfile.write('<br><b>Google Map based on Flickr/Instagram/Twitter Geolocation Data</b><br>')
	htmlfile.write(html.encode('utf8','replace'))
	htmlfile.write('</body></html>')
	htmlfile.close()

	#new
	print "\n[*] Checking additional social networks for active accounts... "
	g = Graph()
	totalCount = 50
	start = 0
	global nodeList
	global edgeList

	while(start<totalCount):
      		nodeList.append("")	
	        edgeList.append("")
	        start+=1	

	nodeList[0] = g.add_node('original')
	nodeList[0]['node'] = createNodeLocation(lat,lng)	

	global report
	usernameSearch(g)


def showhelp():
	print ""
	print "	MMMMMM$ZMMMMMDIMMMMMMMMNIMMMMMMIDMMMMMMM"
	print "	MMMMMMNINMMMMDINMMMMMMMZIMMMMMZIMMMMMMMM"
	print "	MMMMMMMIIMMMMMI$MMMMMMMIIMMMM8I$MMMMMMMM"
	print "	MMMMMMMMIINMMMIIMMMMMMNIIMMMOIIMMMMMMMMM"
	print "	MMMMMMMMOIIIMM$I$MMMMNII8MNIIINMMMMMMMMM"
	print "	MMMMMMMMMZIIIZMIIIMMMIIIM7IIIDMMMMMMMMMM"
	print "	MMMMMMMMMMDIIIIIIIZMIIIIIII$MMMMMMMMMMMM"
	print "	MMMMMMMMMMMM8IIIIIIZIIIIIIMMMMMMMMMMMMMM"
	print "	MMMMMMMMMMMNIIIIIIIIIIIIIIIMMMMMMMMMMMMM"
	print "	MMMMMMMMM$IIIIIIIIIIIIIIIIIII8MMMMMMMMMM"
	print "	MMMMMMMMIIIIIZIIIIZMIIIIIDIIIIIMMMMMMMMM"
	print "	MMMMMMOIIIDMDIIIIZMMMIIIIIMMOIIINMMMMMMM"
	print "	MMMMMNIIIMMMIIII8MMMMM$IIIZMMDIIIMMMMMMM"
	print "	MMMMIIIZMMM8IIIZMMMMMMMIIIIMMMM7IIZMMMMM"
	print "	MMM$IIMMMMOIIIIMMMMMMMMMIIIIMMMM8IIDMMMM"
	print "	MMDIZMMMMMIIIIMMMMMMMMMMNIII7MMMMNIIMMMM"
	print "	MMIOMMMMMNIII8MMMMMMMMMMM7IIIMMMMMM77MMM"
	print "	MO$MMMMMM7IIIMMMMMMMMMMMMMIII8MMMMMMIMMM"
	print "	MIMMMMMMMIIIDMMMMMMMMMMMMM$II7MMMMMMM7MM"
	print "	MMMMMMMMMIIIMMMMMMMMMMMMMMMIIIMMMMMMMDMM"
	print "	MMMMMMMMMII$MMMMMMMMMMMMMMMIIIMMMMMMMMMM"
	print "	MMMMMMMMNIINMMMMMMMMMMMMMMMOIIMMMMMMMMMM"
	print "	MMMMMMMMNIOMMMMMMMMMMMMMMMMM7IMMMMMMMMMM"
	print "	MMMMMMMMNINMMMMMMMMMMMMMMMMMZIMMMMMMMMMM"
	print "	MMMMMMMMMIMMMMMMMMMMMMMMMMMM8IMMMMMMMMMM"

	print """
	#####################################################
	#                  geoStalker.py                 #
	#               [Trustwave Spiderlabs]              #
	#####################################################
	Usage: python geoStalker.py [OPTIONS]

	[OPTIONS]

	-location   [Physical Address or Geocoordinates]
	-user [Username] - Not enabled yet
	"""

def mainProcess(input):
	#input = "252 North Bridge Road singapore"
	#input = raw_input("Please enter an address or GPS coordinates (e.g. 1.358143,103.944826): ")
	while len(input.strip())<1:
		input = raw_input("Please enter an address or GPS coordinates (e.g. 1.358143,103.944826): ")
	try:	
		if any(c.isalpha() for c in input):
			print "[*] Converting address to GPS coordinates: "+str(lat)+" "+str(lng)
			lat,lng = address2geocoordinate(input)
			lat = lat.strip()
			lng = lng.strip()
		else:
			lat,lng = input.split(',')
			lat = lat.strip()
			lng = lng.strip()
	except:
		pass
		#print "[!] Geocoding error"

	c = conn.cursor()
	c.execute('select distinct username from instagram where origLat=? and origLng=?',(lat,lng,))
	dataList1 = []
	dataList1 = c.fetchall()
	for i in dataList1:
		x = str(normalize(i))
		x = str(x.replace('http://instagram.com/',''))
		if x not in globalUserList:
			globalUserList.append(x)

	c = conn.cursor()
	c.execute('select distinct username from flickr where origLat=? and origLng=?',(lat,lng,))
	dataList1 = []
	dataList1 = c.fetchall()
	for i in dataList1:
		x = str(i)
		x = str(x.replace('http://www.flickr.com/photos/',''))
		if x not in globalUserList:
			globalUserList.append(x)

	c = conn.cursor()
	c.execute('select distinct username from twitter where origLat=? and origLng=?',(lat,lng,))
	dataList1 = []
	dataList1 = c.fetchall()
	for i in dataList1:
		x = str(normalize(i))
		x = str(x.replace('https://www.twitter.com/',''))
		if x not in globalUserList:
			globalUserList.append(x)


	#for x in globalUserList:
	#	print x
	geoLocationSearch(lat,lng)
		
	print "\n[*] Analysis report has been written to 'report.txt'"
	reportFile = open('report.txt', "w")
	reportFile.write('\n[*] Geolocation')
	reportFile.write('\n('+str(lat)+','+str(lng)+')')
	reportFile.write('\n\n[*] Found User IDs in Area')
	for x in globalUserList:
		reportFile.write('\n'+str(normalize(x)).encode('utf8','ignore'))

	reportFile.write(report.encode('utf8','ignore'))
	reportFile.close()
	print "[*] Please refer to 'result.html' for generated Google Maps."		
	filename = 'maltego_'+str(lat)+'_'+str(lng)+'.mtgx'
	altfilename = 'maltego_'+str(lat)+'_'+str(lng)+'_all_searches.mtgx'
	print "[*] Please refer to '"+filename+"' for generated Maltego File containing nearby results from social media sites."
	print "[*] Please refer to '"+altfilename+"' for generated Maltego File containing above plus mapping to other social media accounts (huge map)."
	#createMaltegoGeolocation()
	#createMaltegoUsername()


def options(arguments):
	user = ""
	count = 0
 	for arg in arguments:
  		if arg == "-location":
			count+=1
   			location = arguments[count+1]
  	mainProcess(location)

if __name__ == '__main__':
	if len(sys.argv) <= 1:
		showhelp()
		sys.exit()
 	else:
  		options(sys.argv)
  		sys.exit()
