# -*- coding: utf-8 -*-
from __future__ import division
import httplib2,json
import zlib
import zipfile
import sys
import re
import datetime
import operator
import sqlite3
import os
from datetime import datetime
from datetime import date
import pytz 
from tzlocal import get_localzone
import requests
from termcolor import colored, cprint
from pygraphml.GraphMLParser import *
from pygraphml.Graph import *
from pygraphml.Node import *
from pygraphml.Edge import *

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time,re,sys
from selenium.webdriver.common.keys import Keys
import datetime
from bs4 import BeautifulSoup
from StringIO import StringIO

requests.adapters.DEFAULT_RETRIES = 10

h = httplib2.Http(".cache")


facebook_username = ""
facebook_password = ""

global uid
uid = ""
username = ""
internetAccess = True
cookies = {}
all_cookies = {}
reportFileName = ""

#For consonlidating all likes across Photos Likes+Post Likes
peopleIDList = []
likesCountList = []
timePostList = []
placesVisitedList = []

#Chrome Options
chromeOptions = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images":2}
chromeOptions.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(chrome_options=chromeOptions)



def createDatabase():
	conn = sqlite3.connect('facebook.db')
	c = conn.cursor()
	sql = 'create table if not exists photosLiked (sourceUID TEXT, description TEXT, photoURL TEXT unique, pageURL TEXT, username TEXT)'
	sql1 = 'create table if not exists photosCommented (sourceUID TEXT, description TEXT, photoURL TEXT unique, pageURL TEXT, username TEXT)'
	sql2 = 'create table if not exists friends (sourceUID TEXT, name TEXT, userName TEXT unique, month TEXT, year TEXT)'
	sql3 = 'create table if not exists friendsDetails (sourceUID TEXT, userName TEXT unique, userEduWork TEXT, userLivingCity TEXT, userCurrentCity TEXT, userLiveEvents TEXT, userGender TEXT, userStatus TEXT, userGroups TEXT)'
	sql4 = 'create table if not exists videosBy (sourceUID TEXT, title TEXT unique, url TEXT)'
	sql5 = 'create table if not exists pagesLiked (sourceUID TEXT, name TEXT unique, category TEXT,url TEXT)'
	sql6 = 'create table if not exists photosOf (sourceUID TEXT, description TEXT, photoURL TEXT unique, pageURL TEXT, username TEXT)'
	sql7 = 'create table if not exists photosBy (sourceUID TEXT, description TEXT, photoURL TEXT unique, pageURL TEXT, username TEXT)'
    
	c.execute(sql)
    	c.execute(sql1)
    	c.execute(sql2)
    	c.execute(sql3)
    	c.execute(sql4)
    	c.execute(sql5)
    	c.execute(sql6)
    	c.execute(sql7)
    	conn.commit()

createDatabase()
conn = sqlite3.connect('facebook.db')

def createMaltego(username):
	g = Graph()
	totalCount = 50
	start = 0
	nodeList = []
	edgeList = []

	while(start<totalCount):
       		nodeList.append("")	
	        edgeList.append("")
	        start+=1

	nodeList[0] = g.add_node('Facebook_'+username)
	nodeList[0]['node'] = createNodeFacebook(username,"https://www.facebook.com/"+username,uid)


	counter1=1
	counter2=0                
	userList=[]

	c = conn.cursor()
	c.execute('select userName from friends where sourceUID=?',(uid,))
	dataList = c.fetchall()
	nodeUid = ""
	for i in dataList:
		if i[0] not in userList:
			userList.append(i[0])
			try:
				nodeUid = str(convertUser2ID2(driver,str(i[0])))
				#nodeUid = str(convertUser2ID(str(i[0])))
			   	nodeList[counter1] = g.add_node("Facebook_"+str(i[0]))
   				nodeList[counter1]['node'] = createNodeFacebook(i[0],'https://www.facebook.com/'+str(i[0]),nodeUid)
   				edgeList[counter2] = g.add_edge(nodeList[0], nodeList[counter1])
   				edgeList[counter2]['link'] = createLink('Facebook')
    				nodeList.append("")
 		   		edgeList.append("")
    				counter1+=1
    				counter2+=1
			except IndexError:
				continue
	if len(nodeUid)>0:	
		parser = GraphMLParser()
		if not os.path.exists(os.getcwd()+'/Graphs'):
	    		os.makedirs(os.getcwd()+'/Graphs')
		filename = 'Graphs/Graph1.graphml'
		parser.write(g, "Graphs/Graph1.graphml")
		cleanUpGraph(filename)
		filename = username+'_maltego.mtgx'
		print 'Creating archive: '+filename
		zf = zipfile.ZipFile(filename, mode='w')
		print 'Adding Graph1.graphml'
		zf.write('Graphs/Graph1.graphml')
		print 'Closing'
		zf.close()
 
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
	xmlString += '<mtg:Value>'+str(uid)+'</mtg:Value>'
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

def normalize(s):
	if type(s) == unicode: 
       		return s.encode('utf8', 'ignore')
	else:
        	return str(s)

def findUser(findName):
	stmt = "SELECT uid,current_location,username,name FROM user WHERE contains('"+findName+"')"
	stmt = stmt.replace(" ","+")
	url="https://graph.facebook.com/fql?q="+stmt+"&access_token="+facebook_access_token
	resp, content = h.request(url, "GET")
	results = json.loads(content)
	count=1
	for x in results['data']:
		print str(count)+'\thttp://www.facebook.com/'+x['username']
		count+=1

def convertUser2ID2(driver,username):
	url="http://graph.facebook.com/"+username
	resp, content = h.request(url, "GET")
	if resp.status==200:
		results = json.loads(content)
		if len(results['id'])>0:
			fbid = results['id']
			return fbid

def convertUser2ID(username):
	stmt = "SELECT uid,current_location,username,name FROM user WHERE username=('"+username+"')"
	stmt = stmt.replace(" ","+")
	url="https://graph.facebook.com/fql?q="+stmt+"&access_token="+facebook_access_token
	resp, content = h.request(url, "GET")
	if resp.status==200:
		results = json.loads(content)
		if len(results['data'])>0:
			return results['data'][0]['uid']
		else:
			print "[!] Can't convert username 2 uid. Please check username"
			sys.exit()
			return 0
	else:
		print "[!] Please check your facebook_access_token before continuing"
		sys.exit()
		return 0

def convertID2User(uid):
	stmt = "SELECT uid,current_location,username,name FROM user WHERE uid=('"+uid+"')"
	stmt = stmt.replace(" ","+")
	url="https://graph.facebook.com/fql?q="+stmt+"&access_token="+facebook_access_token
	resp, content = h.request(url, "GET")
	results = json.loads(content)
	return results['data'][0]['uid']


def loginFacebook(driver):
	driver.implicitly_wait(120)
	driver.get("https://www.facebook.com/")
	assert "Welcome to Facebook" in driver.title
	time.sleep(3)
	driver.find_element_by_id('email').send_keys(facebook_username)
	driver.find_element_by_id('pass').send_keys(facebook_password)
	driver.find_element_by_id("loginbutton").click()
	global all_cookies
	all_cookies = driver.get_cookies()
	html = driver.page_source
	if "Incorrect Email/Password Combination" in html:
		print "[!] Incorrect Facebook username (email address) or password"
		sys.exit()
def write2Database(dbName,dataList):
	try:
		cprint("[*] Writing "+str(len(dataList))+" record(s) to database table: "+dbName,"white")
		#print "[*] Writing "+str(len(dataList))+" record(s) to database table: "+dbName
		numOfColumns = len(dataList[0])
		c = conn.cursor()
		if numOfColumns==3:
			for i in dataList:
				try:
					c.execute('INSERT INTO '+dbName+' VALUES (?,?,?)', i)
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

def downloadFile(url):	
	global cookies
	for s_cookie in all_cookies:
			cookies[s_cookie["name"]]=s_cookie["value"]
	r = requests.get(url,cookies=cookies)
	html = r.content
	return html

def parsePost(id,username):
	filename = 'posts__'+str(id)
	if not os.path.lexists(filename):
		print "[*] Caching Facebook Post: "+str(id)
		url = "https://www.facebook.com/"+username+"/posts/"+str(id)
		driver.get(url)	
		if "Sorry, this page isn't available" in driver.page_source:
			print "[!] Cannot access page "+url
			return ""
        	lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        	match=False
        	while(match==False):
        	        time.sleep(1)
        	        lastCount = lenOfPage
               		lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                	if lastCount==lenOfPage:
                	        match=True
		html1 = driver.page_source	
		text_file = open(filename, "w")
		text_file.write(normalize(html1))
		text_file.close()
	else:
		html1 = open(filename, 'r').read()
	soup1 = BeautifulSoup(html1)
	htmlList = soup1.find("h5",{"class" : "_6nl"})
	tlTime = soup1.find("abbr")
	if " at " in str(htmlList):
		soup2 = BeautifulSoup(str(htmlList))
		locationList = soup2.findAll("a",{"class" : "profileLink"})
		locUrl = locationList[len(locationList)-1]['href']
		locDescription = locationList[len(locationList)-1].text
		locTime = tlTime['data-utime']
		placesVisitedList.append([locTime,locDescription,locUrl])


def parseLikesPosts(id):
	peopleID = []
	filename = 'likes_'+str(id)
	if not os.path.lexists(filename):
		print "[*] Caching Post Likes: "+str(id)
		url = "https://www.facebook.com/browse/likes?id="+str(id)
		driver.get(url)	
		if "Sorry, this page isn't available" in driver.page_source:
			print "[!] Cannot access page "+url
			return ""
        	lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        	match=False
        	while(match==False):
        	        time.sleep(1)
        	        lastCount = lenOfPage
               		lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                	if lastCount==lenOfPage:
                	        match=True
		html1 = driver.page_source	
		text_file = open(filename, "w")
		text_file.write(normalize(html1))
		text_file.close()
	else:
		html1 = open(filename, 'r').read()
	soup1 = BeautifulSoup(html1)
	peopleLikeList = soup1.findAll("div",{"class" : "fsl fwb fcb"})

	if len(peopleLikeList)>0:
		print "[*] Extracting Likes from Post: "+str(id)
		for x in peopleLikeList:
			soup2 = BeautifulSoup(str(x))
			peopleLike = soup2.find("a")
			peopleLikeID = peopleLike['href'].split('?')[0].replace('https://www.facebook.com/','')
			if peopleLikeID == 'profile.php':	
				r = re.compile('id=(.*?)&fref')
				m = r.search(str(peopleLike['href']))
				if m:
					peopleLikeID = m.group(1)
			print "[*] Liked Post: "+"\t"+peopleLikeID
			if peopleLikeID not in peopleID:
				peopleID.append(peopleLikeID)
		
		return peopleID	
		


def parseTimeline(html,username):
	soup = BeautifulSoup(html)	
	tlTime = soup.findAll("abbr")
	temp123 = soup.findAll("div",{"role" : "article"})
	placesCheckin = []
	timeOfPostList = []

	counter = 0

	for y in temp123:
		soup1 = BeautifulSoup(str(y))
		tlDateTimeLoc = soup1.findAll("a",{"class" : "uiLinkSubtle"})
		#Universal Time
		try:
			soup2 = BeautifulSoup(str(tlDateTimeLoc[0]))
			tlDateTime = soup2.find("abbr")	
			#Facebook Post Link	
			tlLink = tlDateTimeLoc[0]['href']

			try:
				tz = get_localzone()
				unixTime = str(tlDateTime['data-utime'])
				localTime = (datetime.datetime.fromtimestamp(int(unixTime)).strftime('%Y-%m-%d %H:%M:%S'))
				timePostList.append(localTime)
				timeOfPost = localTime
				timeOfPostList.append(localTime)

				print "[*] Time of Post: "+localTime
			except TypeError:
				continue
			if "posts" in tlLink:
				#print tlLink.strip()
				pageID = tlLink.split("/")

				parsePost(pageID[3],username)
				peopleIDLikes = parseLikesPosts(pageID[3])

				try:
					for id1 in peopleIDLikes:
						global peopleIDList
						global likesCountList
						if id1 in peopleIDList:
							lastCount = 0
							position = peopleIDList.index(id1)
							likesCountList[position] +=1
						else:
							peopleIDList.append(id1)
							likesCountList.append(1)
				except TypeError:
					continue
				
			if len(tlDateTimeLoc)>2:
				try:
					#Device / Location
					if len(tlDateTimeLoc[1].text)>0:
						print "[*] Location of Post: "+unicode(tlDateTimeLoc[1].text)
					if len(tlDateTimeLoc[2].text)>0:
						print "[*] Device: "+str(tlDateTimeLoc[2].text)
				except IndexError:
					continue	

			else:
				try:
					#Device / Location
					if len(tlDateTimeLoc[1].text)>0:
						if "mobile" in tlDateTimeLoc[1].text:
							print "[*] Device: "+str(tlDateTimeLoc[1].text)
						else:
							print "[*] Location of Post: "+unicode(tlDateTimeLoc[1].text)
					
				except IndexError:
					continue	
			#Facebook Posts
			tlPosts = soup1.find("span",{"class" : "userContent"})
			
			try:
				tlPostSec = soup1.findall("span",{"class" : "userContentSecondary fcg"})
				tlPostMsg = ""
			
				#Places Checked In
			except TypeError:
				continue
			soup3 = BeautifulSoup(str(tlPostSec))
			hrefLink = soup3.find("a")

			"""
			if len(str(tlPostSec))>0:
				tlPostMsg = str(tlPostSec)
				#if " at " in str(tlPostMsg) and " with " not in str(tlPostMsg):
				if " at " in str(tlPostMsg):
					print str(tlPostSec)

					print tlPostMsg
					#print hrefLink
					#placeUrl = hrefLink['href'].encode('utf8').split('?')[0]
					#print "[*] Place: "+placeUrl										
					#placesCheckin.append([timeOfPost,placeUrl])
			"""

			try:
				if len(tlPosts)>0:				
					tlPostStr = re.sub('<[^>]*>', '', str(tlPosts))
					if tlPostStr!=None:
						print "[*] Message: "+str(tlPostStr)
			except TypeError as e:
				continue


			tlPosts = soup1.find("div",{"class" : "translationEligibleUserMessage userContent"})
			try:
				if len(tlPosts)>0:
					tlPostStr = re.sub('<[^>]*>', '', str(tlPosts))
					print "[*] Message: "+str(tlPostStr)	
			except TypeError:
				continue
		except IndexError as e:
			continue
		counter+=1
	
	tlDeviceLoc = soup.findAll("a",{"class" : "uiLinkSubtle"})

	print '\n'

	global reportFileName
	if len(reportFileName)<1:
		reportFileName = username+"_report.txt"
	reportFile = open(reportFileName, "w")
	
	reportFile.write("\n********** Places Visited By "+str(username)+" **********\n")
	filename = username+'_placesVisited.htm'
	if not os.path.lexists(filename):
		html = downloadPlacesVisited(driver,uid)
		text_file = open(filename, "w")
		text_file.write(html.encode('utf8'))
		text_file.close()
	else:
		html = open(filename, 'r').read()
	dataList = parsePlacesVisited(html)
	count=1
	for i in dataList:
		reportFile.write(normalize(i[2])+'\t'+normalize(i[1])+'\t'+normalize(i[3])+'\n')
		count+=1
	
	reportFile.write("\n********** Places Liked By "+str(username)+" **********\n")
	filename = username+'_placesLiked.htm'
	if not os.path.lexists(filename):
		html = downloadPlacesLiked(driver,uid)
		text_file = open(filename, "w")
		text_file.write(html.encode('utf8'))
		text_file.close()
	else:
		html = open(filename, 'r').read()
	dataList = parsePlacesLiked(html)
	count=1
	for i in dataList:
		reportFile.write(normalize(i[2])+'\t'+normalize(i[1])+'\t'+normalize(i[3])+'\n')
		count+=1

	reportFile.write("\n********** Places checked in **********\n")
	for places in placesVisitedList:
		unixTime = places[0]
		localTime = (datetime.datetime.fromtimestamp(int(unixTime)).strftime('%Y-%m-%d %H:%M:%S'))
		reportFile.write(localTime+'\t'+normalize(places[1])+'\t'+normalize(places[2])+'\n')

	reportFile.write("\n********** Apps used By "+str(username)+" **********\n")
	filename = username+'_apps.htm'
	if not os.path.lexists(filename):
		html = downloadAppsUsed(driver,uid)
		text_file = open(filename, "w")
		text_file.write(html.encode('utf8'))
		text_file.close()
	else:
		html = open(filename, 'r').read()
	data1 = parseAppsUsed(html)
	result = ""
	for x in data1:
		reportFile.write(normalize(x)+'\n')
		x = x.lower()
		if "blackberry" in x:
			result += "[*] User is using a Blackberry device\n"
		if "android" in x:
			result += "[*] User is using an Android device\n"
		if "ios" in x or "ipad" in x or "iphone" in x:
			result += "[*] User is using an iOS Apple device\n"
		if "samsung" in x:
			result += "[*] User is using a Samsung Android device\n"
	reportFile.write(result)

	reportFile.write("\n********** Videos Posted By "+str(username)+" **********\n")
	filename = username+'_videosBy.htm'
	if not os.path.lexists(filename):
		html = downloadVideosBy(driver,uid)
		text_file = open(filename, "w")
		text_file.write(html.encode('utf8'))
		text_file.close()
	else:
		html = open(filename, 'r').read()
	dataList = parseVideosBy(html)
	count=1
	for i in dataList:
		reportFile.write(normalize(i[2])+'\t'+normalize(i[1])+'\n')
		count+=1

	reportFile.write("\n********** Pages Liked By "+str(username)+" **********\n")
	filename = username+'_pages.htm'
	if not os.path.lexists(filename):
		print "[*] Caching Pages Liked: "+username
		html = downloadPagesLiked(driver,uid)
		text_file = open(filename, "w")
		text_file.write(html.encode('utf8'))
		text_file.close()
	else:
		html = open(filename, 'r').read()
	dataList = parsePagesLiked(html)
	for i in dataList:
		pageName = normalize(i[0])
		tmpStr	= normalize(i[3])+'\t'+normalize(i[2])+'\t'+normalize(i[1])+'\n'
		reportFile.write(tmpStr)
	print "\n"

	c = conn.cursor()
	reportFile.write("\n********** Friendship History of "+str(username)+" **********\n")
	c.execute('select * from friends where sourceUID=?',(uid,))
	dataList = c.fetchall()
	try:
		if len(str(dataList[0][4]))>0:
			for i in dataList:
				#Date First followed by Username
				reportFile.write(normalize(i[4])+'\t'+normalize(i[3])+'\t'+normalize(i[2])+'\t'+normalize(i[1])+'\n')
				#Username followed by Date
				#reportFile.write(normalize(i[4])+'\t'+normalize(i[3])+'\t'+normalize(i[2])+'\t'+normalize(i[1])+'\n')
		print '\n'
	except IndexError:
		pass

	reportFile.write("\n********** Friends of "+str(username)+" **********\n")
	reportFile.write("*** Backtracing from Facebook Likes/Comments/Tags ***\n\n")
	c = conn.cursor()
	c.execute('select userName from friends where sourceUID=?',(uid,))
	dataList = c.fetchall()
	for i in dataList:
		reportFile.write(str(i[0])+'\n')
	print '\n'

	tempList = []
	totalLen = len(timeOfPostList)
	timeSlot1 = 0
	timeSlot2 = 0
	timeSlot3 = 0 
	timeSlot4 = 0
	timeSlot5 = 0 
	timeSlot6 = 0 
	timeSlot7 = 0 
	timeSlot8 = 0 

	count = 0
	if len(peopleIDList)>0:
		likesCountList, peopleIDList  = zip(*sorted(zip(likesCountList,peopleIDList),reverse=True))
	
		reportFile.write("\n********** Analysis of Facebook Post Likes **********\n")
		while count<len(peopleIDList):
			testStr = str(likesCountList[count]).encode('utf8')+'\t'+str(peopleIDList[count]).encode('utf8')
			reportFile.write(testStr+"\n")
			count+=1	

	reportFile.write("\n********** Analysis of Interactions between "+str(username)+" and Friends **********\n")
	c = conn.cursor()
	c.execute('select userName from friends where sourceUID=?',(uid,))
	dataList = c.fetchall()
	photosliked = []
	photoscommented = []
	userID = []
	
	photosLikedUser = []
	photosLikedCount = []
	photosCommentedUser = []
	photosCommentedCount = []
	
	for i in dataList:
		c.execute('select * from photosLiked where sourceUID=? and username=?',(uid,i[0],))
		dataList1 = []
		dataList1 = c.fetchall()
		if len(dataList1)>0:
			photosLikedUser.append(normalize(i[0]))
			photosLikedCount.append(len(dataList1))
	for i in dataList:
		c.execute('select * from photosCommented where sourceUID=? and username=?',(uid,i[0],))
		dataList1 = []
		dataList1 = c.fetchall()
		if len(dataList1)>0:	
			photosCommentedUser.append(normalize(i[0]))
			photosCommentedCount.append(len(dataList1))
	if(len(photosLikedCount)>1):	
		reportFile.write("Photo Likes: "+str(username)+" and Friends\n")
		photosLikedCount, photosLikedUser  = zip(*sorted(zip(photosLikedCount, photosLikedUser),reverse=True))	
		count=0
		while count<len(photosLikedCount):
			tmpStr = str(photosLikedCount[count])+'\t'+normalize(photosLikedUser[count])+'\n'
			count+=1
			reportFile.write(tmpStr)
	if(len(photosCommentedCount)>1):	
		reportFile.write("\n********** Comments on "+str(username)+"'s Photos **********\n")
		photosCommentedCount, photosCommentedUser  = zip(*sorted(zip(photosCommentedCount, photosCommentedUser),reverse=True))	
		count=0
		while count<len(photosCommentedCount):
			tmpStr = str(photosCommentedCount[count])+'\t'+normalize(photosCommentedUser[count])+'\n'
			count+=1
			reportFile.write(tmpStr)


	reportFile.write("\n********** Analysis of Time in Facebook **********\n")
	for timePost in timeOfPostList:
		tempList.append(timePost.split(" ")[1])
		tempTime = (timePost.split(" ")[1]).split(":")[0]
		tempTime = int(tempTime)
		if tempTime >= 21:
			timeSlot8+=1
		if tempTime >= 18 and tempTime < 21:
			timeSlot7+=1
		if tempTime >= 15 and tempTime < 18:
			timeSlot6+=1
		if tempTime >= 12 and tempTime < 15:
			timeSlot5+=1
		if tempTime >= 9 and tempTime < 12:
			timeSlot4+=1
		if tempTime >= 6 and tempTime < 9:
			timeSlot3+=1
		if tempTime >= 3 and tempTime < 6:
			timeSlot2+=1
		if tempTime >= 0 and tempTime < 3:
			timeSlot1+=1
	reportFile.write("Total % (00:00 to 03:00) "+str((timeSlot1/totalLen)*100)+" %\n")
	reportFile.write("Total % (03:00 to 06:00) "+str((timeSlot2/totalLen)*100)+" %\n")
	reportFile.write("Total % (06:00 to 09:00) "+str((timeSlot3/totalLen)*100)+" %\n")
	reportFile.write("Total % (09:00 to 12:00) "+str((timeSlot4/totalLen)*100)+" %\n")
	reportFile.write("Total % (12:00 to 15:00) "+str((timeSlot5/totalLen)*100)+" %\n")
	reportFile.write("Total % (15:00 to 18:00) "+str((timeSlot6/totalLen)*100)+" %\n")
	reportFile.write("Total % (18:00 to 21:00) "+str((timeSlot7/totalLen)*100)+" %\n")
	reportFile.write("Total % (21:00 to 24:00) "+str((timeSlot8/totalLen)*100)+" %\n")

	"""
	reportFile.write("\nDate/Time of Facebook Posts\n")
	for timePost in timeOfPostList:
		reportFile.write(timePost+'\n')	
	"""
	reportFile.close()

def downloadTimeline(username):
	url = 'https://www.facebook.com/'+username.strip()
	driver.get(url)	
	print "[*] Crawling Timeline"
	if "Sorry, this page isn't available" in driver.page_source:
		print "[!] Cannot access page "+url
		return ""
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                lastCount = lenOfPage
                time.sleep(3)
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
			print "[*] Looking for 'Show Older Stories' Link"
			try:
				clickLink = WebDriverWait(driver, 1).until(lambda driver : driver.find_element_by_link_text('Show Older Stories'))
				if clickLink:
					print "[*] Clicked 'Show Older Stories' Link"
					driver.find_element_by_link_text('Show Older Stories').click()
				else:
					print "[*] Indexing Timeline"
					break
		                        match=True
			except TimeoutException:				
				match = True
	return driver.page_source




def downloadPlacesVisited(driver,userid):
	url = 'https://www.facebook.com/search/'+str(userid).strip()+'/places-visited'
	driver.get(url)	
	if "Sorry, this page isn't available" in driver.page_source:
		print "[!] Cannot access page "+url
		return ""
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                time.sleep(3)
                lastCount = lenOfPage
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                        match=True
	return driver.page_source

def downloadPlacesLiked(driver,userid):
	url = 'https://www.facebook.com/search/'+str(userid).strip()+'/places-liked'
	driver.get(url)	
	if "Sorry, this page isn't available" in driver.page_source:
		print "[!] Cannot access page "+url
		return ""
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                time.sleep(3)
                lastCount = lenOfPage
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                        match=True
	return driver.page_source


def downloadVideosBy(driver,userid):
	url = 'https://www.facebook.com/search/'+str(userid).strip()+'/videos-by'
	driver.get(url)	
	if "Sorry, this page isn't available" in driver.page_source:
		print "[!] Cannot access page "+url
		return ""
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                time.sleep(3)
                lastCount = lenOfPage
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                        match=True
	return driver.page_source

def downloadUserInfo(driver,userid):
	url = 'https://www.facebook.com/'+str(userid).strip()+'/info'
	driver.get(url)	
	if "Sorry, this page isn't available" in driver.page_source:
		print "[!] Cannot access page "+url
		return ""
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                time.sleep(3)
                lastCount = lenOfPage
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                        match=True
	return driver.page_source

def downloadPhotosBy(driver,userid):
	driver.get('https://www.facebook.com/search/'+str(userid)+'/photos-by')
	if "Sorry, we couldn't find any results for this search." in driver.page_source:
		print "Photos commented list is hidden"
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                time.sleep(3)
                lastCount = lenOfPage
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                        match=True
	return driver.page_source

def downloadPhotosOf(driver,userid):
	driver.get('https://www.facebook.com/search/'+str(userid)+'/photos-of')
	if "Sorry, we couldn't find any results for this search." in driver.page_source:
		print "Photos commented list is hidden"
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                time.sleep(3)
                lastCount = lenOfPage
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                        match=True
	return driver.page_source

def downloadPhotosCommented(driver,userid):
	driver.get('https://www.facebook.com/search/'+str(userid)+'/photos-commented')
	if "Sorry, we couldn't find any results for this search." in driver.page_source:
		print "Photos commented list is hidden"
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                time.sleep(3)
                lastCount = lenOfPage
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                        match=True
	return driver.page_source
	
def downloadPhotosLiked(driver,userid):
	driver.get('https://www.facebook.com/search/'+str(userid)+'/photos-liked')
	if "Sorry, we couldn't find any results for this search." in driver.page_source:
		print "Pages liked list is hidden"
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                time.sleep(2)
                lastCount = lenOfPage
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                        match=True
	return driver.page_source
	

def downloadPagesLiked(driver,userid):
	driver.get('https://www.facebook.com/search/'+str(userid)+'/pages-liked')
	if "Sorry, we couldn't find any results for this search." in driver.page_source:
		print "Pages liked list is hidden"
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                time.sleep(3)
                lastCount = lenOfPage
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                        match=True
	return driver.page_source

def downloadFriends(driver,userid):
	driver.get('https://www.facebook.com/search/'+str(userid)+'/friends')
	if "Sorry, we couldn't find any results for this search." in driver.page_source:
		print "Friends list is hidden"
		return ""
	else:
		#assert "Friends of " in driver.title
	        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
       		match=False
        	while(match==False):
        	        time.sleep(3)
               		lastCount = lenOfPage
                	lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                	if lastCount==lenOfPage:
                	        match=True
		return driver.page_source

def downloadAppsUsed(driver,userid):
	driver.get('https://www.facebook.com/search/'+str(userid)+'/apps-used')
	if "Sorry, we couldn't find any results for this search." in driver.page_source:
		print "[!] Apps used list is hidden"
		return ""
	else:
	        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
       		match=False
        	while(match==False):
                	time.sleep(3)
                	lastCount = lenOfPage
                	lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                	if lastCount==lenOfPage:
                	        match=True
		return driver.page_source

def parseUserInfo(html):
	userEduWork = []
	userLivingCity = ""
	userCurrentCity = ""
	userLiveEvents = []
	userGender = ""
	userStatus = ""
	userGroups = []

	#try:
	soup = BeautifulSoup(str(html))
	
	pageLeft = soup.findAll("div", {"class" : "_4_g4 lfloat"})
	pageRight = soup.findAll("div", {"class" : "_4_g5 rfloat"})
	tempList = []

	try:
		soup1 = BeautifulSoup(str(pageLeft[0]))
		eduWork = soup.findAll("div", {"class" : "clearfix fbProfileExperience"})
		for i in eduWork:
			soup1 = BeautifulSoup(str(i))
			eduWorkCo = soup1.findAll("div", {"class" : "experienceTitle"},text=True)		
			eduWorkExp = soup1.findAll("div",{"class" : "experienceBody fsm fwn fcg"},text=True)
			try:
				strEduWork = eduWorkExp[0].encode('utf8')+'\t'+ eduWorkExp[1].encode('utf8')
				userEduWork.append(strEduWork)
			except IndexError:
				strEduWork = eduWorkExp[0].encode('utf8')				
				userEduWork.append(strEduWork)
				continue		
	except IndexError:
		pass
	relationships = soup.findAll("div", {"id" : "pagelet_relationships"})
	featured_pages = soup.findAll("div", {"id" : "pagelet_featured_pages"})
	bio = soup.findAll("div", {"id" : "pagelet_bio"})
	quotes = soup.findAll("div", {"id" : "pagelet_quotes"})

	hometown1 = soup.findAll("div", {"id" : "pagelet_hometown"})
	soup1 = BeautifulSoup(str(hometown1))
	hometown2  = soup1.findAll("div", {"id" : "hometown"},text=True)
	counter=0
	for z in hometown2:
		if z=="Current City":
			userCurrentCity = hometown2[counter+1]
			#print "CurrentCity: "+hometown2[counter+1]
		elif z=="Living":
			userLivingCity = hometown2[counter+1]
			#print "Living: "+hometown2[counter+1]
		counter+=1

	try:
		soup1 = BeautifulSoup(str(pageRight[0]))
		liveEvents = soup1.findAll("div",{"class" : "fbTimelineSection mtm fbTimelineCompactSection"},text=True)
		printOn=False
		for i in liveEvents:
			if printOn==True:
				userLiveEvents.append(i.encode('utf8'))
				#print "Life Events: "+i.encode('utf8')
			if i=="Life Events":
				printOn=True	
	except IndexError:
		pass
	basicInfo = soup1.findAll("div",{"class" : "fbTimelineSection mtm _bak fbTimelineCompactSection"},text=True)
	printOn=False
	counter=0
	for i in basicInfo:
		if printOn==True:
			if basicInfo[counter-1]=="Gender":
				#print "userGender: "+i.encode('utf8')
				userGender = i.encode('utf8')
			if basicInfo[counter-1]=="Relationship Status":
				#print "userStatus: "+i.encode('utf8')
				userStatus = i.encode('utf8')
			printOff=False
		if i=="Gender":
			printOn=True
		if i=="Relationship Status":
			printOn=True	
		counter+=1
	soup = BeautifulSoup(html)	
	groups = soup.findAll("div",{"class" : "mbs fwb"})
	r = re.compile('a href="(.*?)\"')
	for g in groups:
		m = r.search(str(g))
		if m:
			userGroups.append(['https://www.facebook.com'+m.group(1),g.text])
	#for x in userGroups:
	#	print x[0].encode('utf8')+'\t'+x[1].encode('utf8')
	tempList.append([userEduWork,userLivingCity,userCurrentCity,userLiveEvents,userGender,userStatus,userGroups])
	return tempList

def parsePlacesVisited(html):
	soup = BeautifulSoup(html)	
	pageName = soup.findAll("div", {"class" : "_zs fwb"})
	pageCategory = soup.findAll("div", {"class" : "_dew _dj_"})
	tempList = []
	count=0
	r = re.compile('a href="(.*?)\?ref=')
	for x in pageName:
		m = r.search(str(x))
		if m:
			pageCategory[count]
			tempList.append([uid,x.text,pageCategory[count].text,m.group(1)])
		count+=1
	return tempList

def parsePlacesLiked(html):
	soup = BeautifulSoup(html)	
	pageName = soup.findAll("div", {"class" : "_zs fwb"})
	pageCategory = soup.findAll("div", {"class" : "_dew _dj_"})
	tempList = []
	count=0
	r = re.compile('a href="(.*?)\?ref=')
	for x in pageName:
		m = r.search(str(x))
		if m:
			pageCategory[count]
			tempList.append([uid,x.text,pageCategory[count].text,m.group(1)])
		count+=1
	return tempList


def parsePagesLiked(html):
	soup = BeautifulSoup(html)	
	pageName = soup.findAll("div", {"class" : "_zs fwb"})
	pageCategory = soup.findAll("div", {"class" : "_dew _dj_"})
	tempList = []
	count=0
	r = re.compile('a href="(.*?)\?ref=')
	for x in pageName:
		m = r.search(str(x))
		if m:
			pageCategory[count]
			tempList.append([uid,x.text,pageCategory[count].text,m.group(1)])
		count+=1
	return tempList

def parsePhotosby(html):
	soup = BeautifulSoup(html)	
	photoPageLink = soup.findAll("a", {"class" : "_23q"})
	tempList = []
	for i in photoPageLink:
		html = str(i)
		soup1 = BeautifulSoup(html)
		pageName = soup1.findAll("img", {"class" : "img"})
		pageName1 = soup1.findAll("img", {"class" : "scaledImageFitWidth img"})
		pageName2 = soup1.findAll("img", {"class" : "_46-i img"})	
		for z in pageName2:
			if z['src'].endswith('.jpg'):
				url1 = i['href']
				r = re.compile('fbid=(.*?)&set=bc')
				m = r.search(url1)
				if m:
					filename = 'fbid_'+ m.group(1)+'.html'
					filename = filename.replace("profile.php?id=","")
					if not os.path.lexists(filename):
						#html1 = downloadPage(url1)
						html1 = downloadFile(url1)
						print "[*] Caching Photo Page: "+m.group(1)
						text_file = open(filename, "w")
						text_file.write(normalize(html1))
						text_file.close()
					else:
						html1 = open(filename, 'r').read()
				soup2 = BeautifulSoup(html1)
				username2 = soup2.find("div", {"class" : "fbPhotoContributorName"})
				r = re.compile('a href="(.*?)"')
				m = r.search(str(username2))
				if m:	
					username3 = m.group(1)
					username3 = username3.replace("https://www.facebook.com/","")
					username3 = username3.replace("profile.php?id=","")
					print "[*] Extracting Data from Photo Page: "+username3
					tempList.append([str(uid),z['alt'],z['src'],i['href'],username3])
		for y in pageName1:
			if y['src'].endswith('.jpg'):
				url1 = i['href']
				r = re.compile('fbid=(.*?)&set=bc')
				m = r.search(url1)
				if m:
					filename = 'fbid_'+ m.group(1)+'.html'
					filename = filename.replace("profile.php?id=","")
					if not os.path.lexists(filename):
						#html1 = downloadPage(url1)
						html1 = downloadFile(url1)
						print "[*] Caching Photo Page: "+m.group(1)
						text_file = open(filename, "w")
						text_file.write(normalize(html1))
						text_file.close()
					else:
						html1 = open(filename, 'r').read()
				soup2 = BeautifulSoup(html1)
				username2 = soup2.find("div", {"class" : "fbPhotoContributorName"})
				r = re.compile('a href="(.*?)"')
				m = r.search(str(username2))
				if m:	
					username3 = m.group(1)
					username3 = username3.replace("https://www.facebook.com/","")
					username3 = username3.replace("profile.php?id=","")
					print "[*] Extracting Data from Photo Page: "+username3
					tempList.append([str(uid),y['alt'],y['src'],i['href'],username3])
		for x in pageName:
			if x['src'].endswith('.jpg'):
				url1 = i['href']
				r = re.compile('fbid=(.*?)&set=bc')
				m = r.search(url1)
				if m:
					filename = 'fbid_'+ m.group(1)+'.html'
					filename = filename.replace("profile.php?id=","")
					if not os.path.lexists(filename):
						#html1 = downloadPage(url1)
						html1 = downloadFile(url1)
						print "[*] Caching Photo Page: "+m.group(1)
						text_file = open(filename, "w")
						text_file.write(normalize(html1))
						text_file.close()
					else:
						html1 = open(filename, 'r').read()
				soup2 = BeautifulSoup(html1)
				username2 = soup2.find("div", {"class" : "fbPhotoContributorName"})
				r = re.compile('a href="(.*?)"')
				m = r.search(str(username2))
				if m:	
					username3 = m.group(1)
					username3 = username3.replace("https://www.facebook.com/","")
					username3 = username3.replace("profile.php?id=","")
					print "[*] Extracting Data from Photo Page: "+username3
					tempList.append([str(uid),x['alt'],x['src'],i['href'],username3])
	return tempList


def parsePhotosOf(html):
	soup = BeautifulSoup(html)	
	photoPageLink = soup.findAll("a", {"class" : "_23q"})
	tempList = []
	for i in photoPageLink:
		html = str(i)
		soup1 = BeautifulSoup(html)
		pageName = soup1.findAll("img", {"class" : "img"})
		pageName1 = soup1.findAll("img", {"class" : "scaledImageFitWidth img"})
		pageName2 = soup1.findAll("img", {"class" : "_46-i img"})	
		for z in pageName2:
			if z['src'].endswith('.jpg'):
				url1 = i['href']
				r = re.compile('fbid=(.*?)&set=bc')
				m = r.search(url1)
				if m:
					filename = 'fbid_'+ m.group(1)+'.html'
					filename = filename.replace("profile.php?id=","")
					if not os.path.lexists(filename):
						#html1 = downloadPage(url1)
						html1 = downloadFile(url1)
						print "[*] Caching Photo Page: "+m.group(1)
						text_file = open(filename, "w")
						text_file.write(normalize(html1))
						text_file.close()
					else:
						html1 = open(filename, 'r').read()
				soup2 = BeautifulSoup(html1)
				username2 = soup2.find("div", {"class" : "fbPhotoContributorName"})
				r = re.compile('a href="(.*?)"')
				m = r.search(str(username2))
				if m:	
					username3 = m.group(1)
					username3 = username3.replace("https://www.facebook.com/","")
					username3 = username3.replace("profile.php?id=","")
					print "[*] Extracting Data from Photo Page: "+username3
					tempList.append([str(uid),z['alt'],z['src'],i['href'],username3])
		for y in pageName1:
			if y['src'].endswith('.jpg'):
				url1 = i['href']
				r = re.compile('fbid=(.*?)&set=bc')
				m = r.search(url1)
				if m:
					filename = 'fbid_'+ m.group(1)+'.html'
					filename = filename.replace("profile.php?id=","")
					if not os.path.lexists(filename):
						#html1 = downloadPage(url1)
						html1 = downloadFile(url1)
						print "[*] Caching Photo Page: "+m.group(1)
						text_file = open(filename, "w")
						text_file.write(normalize(html1))
						text_file.close()
					else:
						html1 = open(filename, 'r').read()
				soup2 = BeautifulSoup(html1)
				username2 = soup2.find("div", {"class" : "fbPhotoContributorName"})
				r = re.compile('a href="(.*?)"')
				m = r.search(str(username2))
				if m:	
					username3 = m.group(1)
					username3 = username3.replace("https://www.facebook.com/","")
					username3 = username3.replace("profile.php?id=","")
					print "[*] Extracting Data from Photo Page: "+username3
					tempList.append([str(uid),y['alt'],y['src'],i['href'],username3])
		for x in pageName:
			if x['src'].endswith('.jpg'):
				url1 = i['href']
				r = re.compile('fbid=(.*?)&set=bc')
				m = r.search(url1)
				if m:
					filename = 'fbid_'+ m.group(1)+'.html'
					filename = filename.replace("profile.php?id=","")
					if not os.path.lexists(filename):
						#html1 = downloadPage(url1)
						html1 = downloadFile(url1)
						print "[*] Caching Photo Page: "+m.group(1)
						text_file = open(filename, "w")
						text_file.write(normalize(html1))
						text_file.close()
					else:
						html1 = open(filename, 'r').read()
				soup2 = BeautifulSoup(html1)
				username2 = soup2.find("div", {"class" : "fbPhotoContributorName"})
				r = re.compile('a href="(.*?)"')
				m = r.search(str(username2))
				if m:	
					username3 = m.group(1)
					username3 = username3.replace("https://www.facebook.com/","")
					username3 = username3.replace("profile.php?id=","")
					print "[*] Extracting Data from Photo Page: "+username3
					tempList.append([str(uid),x['alt'],x['src'],i['href'],username3])
	return tempList


def parsePhotosLiked(html):
	soup = BeautifulSoup(html)	
	photoPageLink = soup.findAll("a", {"class" : "_23q"})
	tempList = []

	for i in photoPageLink:
		html = str(i)
		soup1 = BeautifulSoup(html)
		pageName = soup1.findAll("img", {"class" : "img"})
		pageName1 = soup1.findAll("img", {"class" : "scaledImageFitWidth img"})
		pageName2 = soup1.findAll("img", {"class" : "_46-i img"})	
		for z in pageName2:
			if z['src'].endswith('.jpg'):
				url1 = i['href']
				r = re.compile('fbid=(.*?)&set=bc')
				m = r.search(url1)
				if m:
					filename = 'fbid_'+ m.group(1)+'.html'
					filename = filename.replace("profile.php?id=","")
					if not os.path.lexists(filename):
						#html1 = downloadPage(url1)
						html1 = downloadFile(url1)
						print "[*] Caching Photo Page: "+m.group(1)
						text_file = open(filename, "w")
						text_file.write(normalize(html1))
						text_file.close()
					else:
						html1 = open(filename, 'r').read()
					soup2 = BeautifulSoup(html1)
					username2 = soup2.find("div", {"class" : "fbPhotoContributorName"})
					r = re.compile('a href="(.*?)"')
					m = r.search(str(username2))
					if m:	
						
						username3 = m.group(1)
						username3 = username3.replace("https://www.facebook.com/","")
						username3 = username3.replace("profile.php?id=","")
						if username3.count('/')==2:
							username3 = username3.split('/')[2]
	
						print "[*] Extracting Data from Photo Page: "+username3
						tmpStr = []
						tmpStr.append([str(uid),repr(zlib.compress(normalize(z['alt']))),normalize(z['src']),normalize(i['href']),normalize(username3)])
						write2Database('photosLiked',tmpStr)

		for y in pageName1:
			if y['src'].endswith('.jpg'):
				url1 = i['href']
				r = re.compile('fbid=(.*?)&set=bc')
				m = r.search(url1)
				if m:
					filename = 'fbid_'+ m.group(1)+'.html'
					filename = filename.replace("profile.php?id=","")
					if not os.path.lexists(filename):
						#html1 = downloadPage(url1)
						html1 = downloadFile(url1)
						print "[*] Caching Photo Page: "+m.group(1)
						text_file = open(filename, "w")
						text_file.write(normalize(html1))
						text_file.close()
					else:
						html1 = open(filename, 'r').read()
					soup2 = BeautifulSoup(html1)
					username2 = soup2.find("div", {"class" : "fbPhotoContributorName"})
					r = re.compile('a href="(.*?)"')
					m = r.search(str(username2))
					if m:	
						username3 = m.group(1)
						username3 = username3.replace("https://www.facebook.com/","")
						username3 = username3.replace("profile.php?id=","")
						if username3.count('/')==2:
							username3 = username3.split('/')[2]

						print "[*] Extracting Data from Photo Page: "+username3
						tmpStr = []
						tmpStr.append([str(uid),repr(zlib.compress(normalize(y['alt']))),normalize(y['src']),normalize(i['href']),normalize(username3)])
						write2Database('photosLiked',tmpStr)

		for x in pageName:
			if x['src'].endswith('.jpg'):
				url1 = i['href']
				r = re.compile('fbid=(.*?)&set=bc')
				m = r.search(url1)
				if m:
					filename = 'fbid_'+ m.group(1)+'.html'
					filename = filename.replace("profile.php?id=","")
					if not os.path.lexists(filename):
						#html1 = downloadPage(url1)
						html1 = downloadFile(url1)
						print "[*] Caching Photo Page: "+m.group(1)
						text_file = open(filename, "w")
						text_file.write(normalize(html1))
						text_file.close()
					else:
						html1 = open(filename, 'r').read()
					soup2 = BeautifulSoup(html1)
					username2 = soup2.find("div", {"class" : "fbPhotoContributorName"})
					r = re.compile('a href="(.*?)"')
					m = r.search(str(username2))
					if m:	
						username3 = m.group(1)
						username3 = username3.replace("https://www.facebook.com/","")
						username3 = username3.replace("profile.php?id=","")
						if username3.count('/')==2:
							username3 = username3.split('/')[2]

						print "[*] Extracting Data from Photo Page: "+username3
						tmpStr = []
						tmpStr.append([str(uid),repr(zlib.compress(normalize(x['alt']))),normalize(x['src']),normalize(i['href']),normalize(username3)])
						write2Database('photosLiked',tmpStr)

	return tempList

def downloadPage(url):
	driver.get(url)	
	html = driver.page_source
	return html

def parsePhotosCommented(html):
	soup = BeautifulSoup(html)	
	photoPageLink = soup.findAll("a", {"class" : "_23q"})
	tempList = []

	for i in photoPageLink:
		html = str(i)
		soup1 = BeautifulSoup(html)
		pageName = soup1.findAll("img", {"class" : "img"})
		pageName1 = soup1.findAll("img", {"class" : "scaledImageFitWidth img"})
		pageName2 = soup1.findAll("img", {"class" : "_46-i img"})	
		for z in pageName2:
			if z['src'].endswith('.jpg'):
				url1 = i['href']
				r = re.compile('fbid=(.*?)&set=bc')
				m = r.search(url1)
				if m:
					filename = 'fbid_'+ m.group(1)+'.html'
					if not os.path.lexists(filename):
						html1 = downloadFile(url1)
						#html1 = downloadPage(url1)
						print "[*] Caching Photo Page: "+m.group(1)
						text_file = open(filename, "w")
						text_file.write(normalize(html1))
						text_file.close()
					else:
						html1 = open(filename, 'r').read()
				soup2 = BeautifulSoup(html1)
				username2 = soup2.find("div", {"class" : "fbPhotoContributorName"})
				r = re.compile('a href="(.*?)"')
				m = r.search(str(username2))
				if m:	
					username3 = m.group(1)
					username3 = username3.replace("https://www.facebook.com/","")
					if username3.count('/')==2:
						username3 = username3.split('/')[2]

					print "[*] Extracting Data from Photo Page: "+username3
					tempList.append([str(uid),z['alt'],z['src'],i['href'],username3])
		for y in pageName1:
			if y['src'].endswith('.jpg'):
				url1 = i['href']
				r = re.compile('fbid=(.*?)&set=bc')
				m = r.search(url1)
				if m:
					filename = 'fbid_'+ m.group(1)+'.html'
					if not os.path.lexists(filename):
						html1 = downloadFile(url1)
						print "[*] Caching Photo Page: "+m.group(1)
						text_file = open(filename, "w")
						text_file.write(normalize(html1))
						text_file.close()
					else:
						html1 = open(filename, 'r').read()
				soup2 = BeautifulSoup(html1)
				username2 = soup2.find("div", {"class" : "fbPhotoContributorName"})
				r = re.compile('a href="(.*?)"')
				m = r.search(str(username2))
				if m:	
					username3 = m.group(1)
					username3 = username3.replace("https://www.facebook.com/","")
					if username3.count('/')==2:
						username3 = username3.split('/')[2]

					print "[*] Extracting Data from Photo Page: "+username3
					tempList.append([str(uid),y['alt'],y['src'],i['href'],username3])
		for x in pageName:
			if x['src'].endswith('.jpg'):
				url1 = i['href']
				r = re.compile('fbid=(.*?)&set=bc')
				m = r.search(url1)
				if m:
					filename = 'fbid_'+ m.group(1)+'.html'
					if not os.path.lexists(filename):
						html1 = downloadFile(url1)
						#html1 = downloadPage(url1)
						print "[*] Caching Photo Page: "+m.group(1)
						text_file = open(filename, "w")
						text_file.write(normalize(html1))
						text_file.close()
					else:
						html1 = open(filename, 'r').read()
				soup2 = BeautifulSoup(html1)
				username2 = soup2.find("div", {"class" : "fbPhotoContributorName"})
				r = re.compile('a href="(.*?)"')
				m = r.search(str(username2))
				if m:	
					username3 = m.group(1)
					username3 = username3.replace("https://www.facebook.com/","")
					if username3.count('/')==2:
						username3 = username3.split('/')[2]
					print "[*] Extracting Data from Photo Page: "+username3
					tempList.append([str(uid),x['alt'],x['src'],i['href'],username3])

	return tempList

def parseVideosBy(html):
	soup = BeautifulSoup(html)	
	appsData = soup.findAll("div", {"class" : "_42bw"})
	tempList = []
	for x in appsData:
		r = re.compile('href="(.*?)&amp;')
		m = r.search(str(x))
		if m:
			filename = str(m.group(1)).replace("https://www.facebook.com/photo.php?v=","v_")
			filename = filename+".html"
			url = m.group(1)
			if not os.path.lexists(filename):
				html1 = downloadFile(url)
				#driver.get(url)	
				#html1 = driver.page_source
				text_file = open(filename, "w")
				text_file.write(normalize(html1))
				text_file.close()
			else:
				html1 = open(filename, 'r').read()
			soup1 = BeautifulSoup(html1)	
			titleData = soup1.find("h2", {"class" : "uiHeaderTitle"})
			tempList.append([uid,(titleData.text).strip(),url])
	return tempList
	
def parseAppsUsed(html):
	soup = BeautifulSoup(html)	
	appsData = soup.findAll("div", {"class" : "_zs fwb"})
	tempList = []
	for x in appsData:
		tempList.append(x.text)
	return tempList

def sidechannelFriends(uid):
	userList = []
	c = conn.cursor()
	c.execute('select distinct username from photosLiked where sourceUID=?',(uid,))
	dataList1 = []
	dataList1 = c.fetchall()
	if len(dataList1)>0:
		for i in dataList1:
			if 'pages' not in str(normalize(i[0])):
				userList.append([uid,'',str(normalize(i[0])),'',''])
	c.execute('select distinct username from photosCommented where sourceUID=?',(uid,))
	dataList1 = []
	dataList1 = c.fetchall()
	if len(dataList1)>0:	
		for i in dataList1:
			if 'pages' not in str(normalize(i[0])):
				userList.append([uid,'',str(normalize(i[0])),'',''])
	c.execute('select distinct username from photosOf where sourceUID=?',(uid,))
	dataList1 = []
	dataList1 = c.fetchall()
	if len(dataList1)>0:	
		for i in dataList1:
			if 'pages' not in str(normalize(i[0])):
				userList.append([uid,'',str(normalize(i[0])),'',''])
	return userList

def getFriends(uid):
	userList = []
	c = conn.cursor()
	c.execute('select username from friends where sourceUID=?',(uid,))
	dataList1 = []
	dataList1 = c.fetchall()
	if len(dataList1)>0:
		for i in dataList1:
			userList.append([uid,'',str(normalize(i)),'',''])
	return userList
	
def parseFriends(html):
	mthList = ['january','february','march','april','may','june','july','august','september','october','november','december']
	if len(html)>0:
		soup = BeautifulSoup(html)	

		friendBlockData = soup.findAll("div",{"class" : "_1zf"})
		friendNameData = soup.findAll("div", {"class" : "_zs fwb"})
		knownSinceData = soup.findAll("div", {"class" : "_52eh"})
	
		friendList=[]
		for i in friendBlockData:
			soup1 = BeautifulSoup(str(i))
			friendNameData = soup1.find("div",{"class" : "_zs fwb"})
			lastKnownData = soup1.find("div",{"class" : "_52eh"})
			r = re.compile('a href=(.*?)\?ref')
			m = r.search(str(friendNameData))
			if m:
				try:	
					friendName = friendNameData.text
					friendName = friendName.replace('"https://www.facebook.com/','')
					value = (lastKnownData.text).split("since")[1].strip()
					#Current year - No year listed in page
					if not re.search('\d+', value):					
						value = value+" "+str((datetime.datetime.now()).year)
						month = ((re.sub(" \d+", " ", value)).lower()).strip()
						monthDigit = 0
						count=0
						for s in mthList:
							if s==month:
								monthDigit=count+1
							count+=1	
						year = re.findall("(\d+)",value)[0]
						fbID = m.group(1).replace('"https://www.facebook.com/','')
						friendList.append([str(uid),friendName,fbID,int(monthDigit),int(year)])
					else:
						#Not current year
						month,year = value.split(" ")
						month = month.lower()
						monthDigit = 0
						count=0
						for s in mthList:
							if s==month:
								monthDigit=count+1
							count+=1
						fbID = m.group(1).replace('"https://www.facebook.com/','')
						friendList.append([str(uid),friendName,fbID,int(monthDigit),int(year)])
	

				except IndexError:
					continue
				except AttributeError:
					continue
		i=0
		data = sorted(friendList, key=operator.itemgetter(4,3))
		#print "Friends List"
		#for x in data:
		#	print x
		#	#print x[2]+'\t'+x[1]
		return data

    	
"""
def analyzeFriends(userid):
	c = conn.cursor()
	c.execute('select * from friends where sourceUID=?',(userid,))
	dataList = c.fetchall()
	photosliked = []
	photoscommented = []
	userID = []
	for i in dataList:
		#print i[1]+'\t'+i[2]
		#c.execute('select username from photosLiked')
		c.execute('select * from photosLiked where sourceUID=? and username=?',(userid,i[2],))
		dataList1 = []
		dataList1 = c.fetchall()
		if len(dataList1)>0:
			str1 = ([dataList1[0][4].encode('utf8'),str(len(dataList1))])
			photosliked.append(str1)
		
		c.execute('select * from photosCommented where sourceUID=? and username=?',(userid,i[2],))
		dataList1 = []
		dataList1 = c.fetchall()
		if len(dataList1)>0:
			str1 = ([dataList1[0][4].encode('utf8'),str(len(dataList1))])
			photoscommented.append(str1)
	print "[*] Videos Posted By "+str(username)
	filename = username+'_videosBy.htm'
	if not os.path.lexists(filename):
		html = downloadVideosBy(driver,uid)
		text_file = open(filename, "w")
		text_file.write(html.encode('utf8'))
		text_file.close()
	else:
		html = open(filename, 'r').read()
	dataList = parseVideosBy(html)
	count=1
	for i in dataList:
		print str(count)+') '+i[1]+'\t'+i[2]
		count+=1
	print "\n"

	print "[*] Pages Liked By "+str(uid)
	filename = username+'_pages.htm'
	if not os.path.lexists(filename):
		html = downloadPagesLiked(driver,uid)
		text_file = open(filename, "w")
		text_file.write(html.encode('utf8'))
		text_file.close()
	else:
		html = open(filename, 'r').read()
	dataList = parsePagesLiked(html)
	for i in dataList:
		print "[*] "+normalize(i[1])
		#print "[*] "+normalize(i[2])+"\t"+normalize(i[1])+"\t"+normalize(i[3])
		#print normalize(i[1])+"\t"+normalize(i[2])+"\t"+normalize(i[3])
	print "\n"

"""

	
def mainProcess(username):
	username = username.strip()
	print "[*] Username:\t"+str(username)
	global uid
	
	loginFacebook(driver)
	uid = convertUser2ID2(driver,username)
	if not uid:
		print "[!] Problem converting username to uid"
		sys.exit()
	else:
		print "[*] Uid:\t"+str(uid)

	filename = username+'_apps.htm'
	if not os.path.lexists(filename):
		print "[*] Caching Facebook Apps Used By: "+username
		html = downloadAppsUsed(driver,uid)
		text_file = open(filename, "w")
		text_file.write(html.encode('utf8'))
		text_file.close()
	else:
		html = open(filename, 'r').read()
	data1 = parseAppsUsed(html)
	result = ""
	for x in data1:
		print x	
		x = x.lower()
		if "blackberry" in x:
			result += "[*] User is using a Blackberry device\n"
		if "android" in x:
			result += "[*] User is using an Android device\n"
		if "ios" in x or "ipad" in x or "iphone" in x:
			result += "[*] User is using an iOS Apple device\n"
		if "samsung" in x:
			result += "[*] User is using a Samsung Android device\n"
	print result

	#Caching Pages Liked - Start
	filename = username+'_pages.htm'
	if not os.path.lexists(filename):
		print "[*] Caching Pages Liked By: "+username
		html = downloadPagesLiked(driver,uid)
          	text_file = open(filename, "w")
          	text_file.write(html.encode('utf8'))
          	text_file.close()
       	else:
        	html = open(filename, 'r').read()
        dataList = parsePagesLiked(html)
        if len(dataList)>0:
	        write2Database('pagesLiked',dataList)
	#Caching Pages Liked - End

        filename = username+'_videosBy.htm'
        if not os.path.lexists(filename):
           	print "[*] Caching Videos Liked By: "+username
           	html = downloadVideosBy(driver,uid)
		text_file = open(filename, "w")
		text_file.write(html.encode('utf8'))
            	text_file.close()
        else:
            	html = open(filename, 'r').read()
        dataList = parseVideosBy(html)
        if len(dataList)>0:
	        write2Database('videosBy',dataList)

        filename = username+'_photosOf.htm'
        if not os.path.lexists(filename):
            	print "[*] Caching Photos Of: "+username
            	html = downloadPhotosOf(driver,uid)
            	text_file = open(filename, "w")
            	text_file.write(html.encode('utf8'))
            	text_file.close()
        else:
            	html = open(filename, 'r').read()
        dataList = parsePhotosOf(html)
        write2Database('photosOf',dataList)
        
        filename = username+'_photosBy.htm'
        if not os.path.lexists(filename):
            	print "[*] Caching Photos By: "+username
            	html = downloadPhotosOf(driver,uid)
            	text_file = open(filename, "w")
            	text_file.write(html.encode('utf8'))
            	text_file.close()
        else:
            	html = open(filename, 'r').read()
        dataList = parsePhotosOf(html)
        write2Database('photosBy',dataList)        

	#Disable
   	filename = username+'_photosLiked.htm'
   	print filename
        if not os.path.lexists(filename):
           	print "[*] Caching Photos Liked By: "+username
            	html = downloadPhotosLiked(driver,uid)
            	text_file = open(filename, "w")
            	text_file.write(html.encode('utf8'))
            	text_file.close()
        else:
            	html = open(filename, 'r').read()
        dataList = parsePhotosLiked(html)
        print "[*] Writing "+str(len(dataList))+" records to table: photosLiked"
        #write2Database('photosLiked',dataList)

        filename = username+'_photoscommented.htm'
    	print filename
        if not os.path.lexists(filename):
           	print "[*] Caching Commented On By: "+username
            	html = downloadPhotosCommented(driver,uid)
            	text_file = open(filename,"w")
            	text_file.write(html.encode('utf8'))
            	text_file.close()
        else:
            	html = open(filename, 'r').read()
        dataList = parsePhotosCommented(html)
        write2Database('photosCommented',dataList)

        filename = username+'_friends.htm'
        print filename
        if not os.path.lexists(filename):
           	print "[*] Caching Friends Page of: "+username
            	html = downloadFriends(driver,uid)
            	text_file = open(filename, "w")
            	text_file.write(html.encode('utf8'))
            	text_file.close()
       	else:
            	html = open(filename, 'r').read()
        if len(html.strip())>1:
            	dataList = parseFriends(html)
            	print "[*] Writing Friends List to Database: "+username
            	write2Database('friends',dataList)
	else:
           	print "[*] Extracting Friends from Likes/Comments: "+username
            	write2Database('friends',sidechannelFriends(uid))	
            	
        c = conn.cursor()
        c.execute('select * from friends where sourceUID=?',(uid,))
        dataList = c.fetchall()
        photosliked = []
        photoscommented = []
        userID = []
        for i in dataList:
            #print i[1]+'\t'+i[2]
            #c.execute('select username from photosLiked')
            c.execute('select * from photosLiked where sourceUID=? and username=?',(uid,i[2],))
            dataList1 = []
            dataList1 = c.fetchall()
            if len(dataList1)>0:
                str1 = ([dataList1[0][4].encode('utf8'),str(len(dataList1))])
                photosliked.append(str1)
        
            c.execute('select * from photosCommented where sourceUID=? and username=?',(uid,i[2],))
            dataList1 = []
            dataList1 = c.fetchall()
            if len(dataList1)>0:
                str1 = ([dataList1[0][4].encode('utf8'),str(len(dataList1))])
                photoscommented.append(str1)            	
            	
	

        #analyzeFriends(str(uid))
        filename = username+'.htm'
        if not os.path.lexists(filename):
           	print "[*] Caching Timeline Page of: "+username
            	html = downloadTimeline(username)
            	text_file = open(filename, "w")
            	text_file.write(html.encode('utf8'))
            	text_file.close()
        else:
            	html = open(filename, 'r').read()
        dataList = parseTimeline(html,username)


	print "\n"
	print "[*] Downloading User Information"

	tmpInfoStr = []
	userID =  getFriends(uid)
	for x in userID:
		i = str(normalize(x[2]))
		i = i.replace("(u'","").replace("',","").replace(')','')
		i = i.replace('"https://www.facebook.com/','')
		print "[*] Looking up information on "+i
		filename = i.encode('utf8')+'.html'
		if "/" not in filename:
			if not os.path.lexists(filename):
				print 'Writing to '+filename
				url = 'https://www.facebook.com/'+i.encode('utf8')+'/info'
				html = downloadFile(url)	
				#html = downloadUserInfo(driver,i.encode('utf8'))
				if len(html)>0:
					text_file = open(filename, "w")
					text_file.write(normalize(html))
					#text_file.write(html.encode('utf8'))
					text_file.close()
			else:
				print 'Skipping: '+filename
			print "[*] Parsing User Information: "+i
			html = open(filename, 'r').read()
			userInfoList = parseUserInfo(html)[0]
			tmpStr = []
			tmpStr.append([uid,str(normalize(i)),str(normalize(userInfoList[0])),str(normalize(userInfoList[1])),str(normalize(userInfoList[2])),str(normalize(userInfoList[3])),str(normalize(userInfoList[4])),str(normalize(userInfoList[5])),normalize(str(userInfoList[6]).encode('utf8'))])
			try:
				write2Database('friendsDetails',tmpStr)
			except:
				continue
			#tmpInfoStr.append([uid,str(normalize(i)),str(normalize(userInfoList[0])),str(normalize(userInfoList[1])),str(normalize(userInfoList[2])),str(normalize(userInfoList[3])),str(normalize(userInfoList[4])),str(normalize(userInfoList[5])),str(normalize(userInfoList[6]))])
			#tmpInfoStr.append([i[1],userInfoList[0],userInfoList[1],userInfoList[2],userInfoList[3],userInfoList[4],userInfoList[5],userInfoList[6]])

	#cprint("[*] Writing "+str(len(dataList))+" record(s) to database table: "+dbName,"white")
	cprint("[*] Report has been written to: "+str(reportFileName),"white")
	cprint("[*] Preparing Maltego output...","white")
	createMaltego(username)
	cprint("[*] Maltego file has been created","white")

    	driver.close()
        driver.quit
        conn.close()


def options(arguments):
	user = ""
	count = 0
 	for arg in arguments:
  		if arg == "-user":
			count+=1
   			user = arguments[count+1]
  		if arg == "-report":
			count+=1
			global reportFileName
   			reportFileName = arguments[count+1]
  	mainProcess(user)


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
	#                  fbStalker.py                 #
	#               [Trustwave Spiderlabs]              #
	#####################################################
	Usage: python fbStalker.py [OPTIONS]

	[OPTIONS]

	-user   [Facebook Username]
	-report [Filename]
	"""

if __name__ == '__main__':
	if len(sys.argv) <= 1:
		showhelp()
		driver.close()
		driver.quit
		conn.close()
		sys.exit()
 	else:
		if len(facebook_username)<1 or len(facebook_password)<1:
			print "[*] Please fill in 'facebook_username' and 'facebook_password' before continuing."
			sys.exit()
  		options(sys.argv)
 
