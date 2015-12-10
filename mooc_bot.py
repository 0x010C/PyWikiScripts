#!/usr/bin/python
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 28 October 2015
#License: GNU GPL v3

import sys
import time
import json
import requests


#Paramètres
version = "1.00"
site = "https://test.wikipedia.org"
user = ""
password = ""
cookies = {}

wait = 30
nbLoopRelogin = 30
reply = {
	"title":              "User talk:"+user,
	"section_title":      "Bonjour $1 !",
	"content":            "Je te notifie : [[User:$1|$1]] ;) ~~~~",
	"summary":            "Notification",
	"tag":                "WikiMOOC",
}



def login():
	global cookies
	r = requests.post(site+u"/w/api.php", data={"action":"login", "lgname":user, "lgpassword":password, "format":"json"})
	print r.text
	token = json.loads(r.text)["login"]["token"];
	r = requests.post(site+u"/w/api.php", data={"action":"login", "lgname":user, "lgpassword":password, "lgtoken":token, "format":"json"}, cookies=r.cookies)
	print r.text
	if json.loads(r.text)["login"]["result"] == "Success":
		cookies = r.cookies
		print "\033[1;32msuccessful login :)\033[0m"
	else:
		print "\033[1;31munsuccessful login :(\033[0m"
		sys.exit()


def getNotificationsCount():
	global cookies
	r = requests.post(site+u"/w/api.php", data={"action":"query", "meta":"notifications", "notsections":"alert", "notprop":"count", "assert":"user", "format":"json"}, cookies=cookies)
	response = json.loads(r.text)
	if 'error' in response.keys():
		if response["error"]["code"] == "notlogin-required":
			return -1
		else:
			return -2
	
	print response["query"]["notifications"]["count"]
	return response["query"]["notifications"]["count"]


def getNotificationsList(previousMaxID):
	global cookies
	r = requests.post(site+u"/w/api.php", data={"action":"query", "meta":"notifications", "notprop":"list", "notsections":"alert", "notalertunreadfirst":"", "notmessageunreadfirst":"", "assert":"user", "format":"json"}, cookies=cookies)
	response = json.loads(r.text)
	if 'error' in response.keys():
		if response["error"]["code"] == "notlogin-required":
			return -1
		else:
			return -2

	IDs = []
	names = []
	for item in response["query"]["notifications"]["list"]:
		if int(item) > previousMaxID:
			IDs.append(item)
			names.append(response["query"]["notifications"]["list"][item]["agent"]["name"])

	return (IDs, names)


def getCrsfToken():
	global cookies
	r = requests.post(site+u"/w/api.php", data={"action":"query", "meta":"tokens", "type":"csrf", "assert":"user", "format":"json"}, cookies=cookies)
	cookies.update(r.cookies)
	return json.loads(r.text)["query"]["tokens"]["csrftoken"]


def cleanNotifications(notificationsIDs, token):
	print notificationsIDs
	global cookies
	notificationsIDs = "|".join(notificationsIDs)
	r = requests.post(site+u"/w/api.php", headers={'content-type': 'application/x-www-form-urlencoded'}, data={"action":"echomarkread", "list":notificationsIDs, "token":token, "assert":"user", "format":"json"}, cookies=cookies)
	cookies.update(r.cookies)


def sendMessage(name, token):
	global cookies
	r = requests.post(site+u"/w/api.php", headers={'content-type': 'application/x-www-form-urlencoded'}, data={"action":"edit", "title":reply["title"], "section":"new", "sectiontitle":name.join(reply["section_title"].split("$1")), "text":name.join(reply["content"].split("$1")), "summary":name.join(reply["summary"].split("$1")), "tags":reply["tag"], "nocreate":"", "token":token, "assert":"user", "format":"json"}, cookies=cookies)
	cookies.update(r.cookies)
	print name


# Main
def main():
	global wait
	reload(sys)
	sys.setdefaultencoding('utf8')
	try:
		log = open("maxid.save", "r")
		previousMaxID = int(log.read())
		log.close()
	except:
		previousMaxID = 0
	while True:
		login()
		for i in range(0,nbLoopRelogin):
			if getNotificationsCount() > 0:
				token = getCrsfToken()
				(IDs, names) = getNotificationsList(previousMaxID)
				cleanNotifications(IDs, token)
				for i in IDs:
					if int(i) > previousMaxID:
						previousMaxID = int(i)
				log = open("maxid.save", "w")
				log.write(str(previousMaxID))
				log.close()
				for name in names:
					token = getCrsfToken()
					sendMessage(name, token)
			time.sleep(wait)

main()
