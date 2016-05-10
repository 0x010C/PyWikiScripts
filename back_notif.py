#!/usr/bin/python
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 28 October 2015
#License: GNU GPL v3

import sys
import time
import json
import requests
import pywiki


#Paramètres
version = "1.1"
reply = {
        "title":              "User talk:WikiMOOC",
        "section_title":      "Bonjour $1 !",
        "content":            "J'ai bien reçu votre notification, je vous notifie en retour : [[User:$1|$1]] {{clin}} ~~~~",
        "summary":            "Notification",
}


def get_notifications_list(previousMaxID):
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
pywiki.Pywiki.get_notifications_list = get_notifications_list


def clean_notifications(notificationsIDs):
	r = self.session.post(self.api_endpoint, data={
		"action":"echomarkread",
		"list":"|".join(notificationsIDs),
		"token":self.get_csrf_token(),
		"assert":self.assertion,
		"format":"json"
	})
pywiki.Pywiki.clean_notifications = clean_notifications


# Main
def main():
	reload(sys)
	sys.setdefaultencoding('utf8')
	try:
		log = open("conf/back_notif.conf", "r")
		previousMaxID = int(log.read())
		log.close()
	except:
		previousMaxID = 0

	pw = pywiki.Pywiki("frwiki-NotifBot")
	pw.login()
		if pw.get_notifications_count() > 0
			(IDs, names) = pw.get_notifications_list(previousMaxID)
			pw.clean_notifications(IDs)
			for i in IDs:
				if int(i) > previousMaxID:
					previousMaxID = int(i)
				log = open("conf/back_notif.conf", "w")
				log.write(str(previousMaxID))
				log.close()
				for name in names:
					text = "== "+name.join(reply["section_title"].split("$1"))+" ==\n"+name.join(reply["content"].split("$1"))
					summary = name.join(reply["summary"].split("$1"))
					pw.append(reply["title"], text, summary, nocreate=True):
main()

#headers={'content-type': 'application/x-www-form-urlencoded'}
