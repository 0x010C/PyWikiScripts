#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Creation date: 28 October 2015
#Last modification: 10 February 2017
#License: GNU GPL v3

import sys
import time
import pywiki


#Paramètres
version = "2.0"
reply = {
        "section_title":      "Bonjour $1 !",
        "content":            "J'ai bien reçu votre notification, je vous notifie en retour : {{Notif|$1}} {{clin}} ~~~~",
        "summary":            "Notification",
}


def get_notifications_list(self):
	response = self.request( {
		"action": "query",
		"format": "json",
		"meta": "notifications",
		"notfilter": "!read",
		"notprop": "list",
		"notsections": "alert",
		"notformat": "model",
		"notlimit": "50"
	} )

	IDs = []
	names = []
	for notification in response["query"]["notifications"]["list"]:
		IDs.append(notification["id"])
		if notification["type"] == "mention":
			names.append(notification["agent"]["name"])

	return (IDs, names)
pywiki.Pywiki.get_notifications_list = get_notifications_list


def clean_notifications(self, notificationsIDs):
	self.request( {
		"action":"echomarkread",
		"list":"|".join(notificationsIDs),
		"token":self.get_csrf_token(),
		"assert":self.assertion,
		"format":"json"
	} )
pywiki.Pywiki.clean_notifications = clean_notifications


def main():
	reload(sys)
	sys.setdefaultencoding('utf8')

	pw = pywiki.Pywiki("frwiki-NotifBot")
	pw.login()
	while True:
		(IDs, names) = pw.get_notifications_list()
		for name in names:
			print name
			title = "\n== " + name.join(reply["section_title"].split("$1")) + " ==\n"
			text = name.join(reply["content"].split("$1"))
			summary = name.join(reply["summary"].split("$1"))
			pw.append('User_talk:' + pw.user, title + text, summary, nocreate=True)
		pw.clean_notifications(IDs)
		time.sleep(180)

main()
