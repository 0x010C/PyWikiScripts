#!/usr/bin/python
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 10 décembre 2015
#License: GNU GPL v3

import re
import requests
import json
import sys
import os



queues  = [
	{"page":u"Wikipédia:OTRS/backlog-info-fr", "id":u"19"},
	{"page":u"Wikipédia:OTRS/backlog-permissions-commons-fr", "id":u"127"},
	{"page":u"Wikipédia:OTRS/backlog-permissions-fr", "id":u"35"},
]
url_otrs = u"https://ticket.wikimedia.org/otrs/index.pl"
url_wiki = u"https://fr.wikipedia.org/w/api.php"
user_otrs = u""
user_wiki = u""
password_otrs = u""
password_wiki = u""
regex_token = re.compile(u"ChallengeToken: '([0-9abcdef]+)',")
regex_age = re.compile(u"<td>[^0-9]*([0-9]* [jhm])(?: [0-9]* [hm])*[^0-9]*</td>")
session_otrs = requests.Session()
session_wiki = requests.Session()



"""
Login into the OTRS website
"""
def login_otrs():
	r = session_otrs.post(url_otrs,data={
		"User":user_otrs,
		"Password":password_otrs,
		"Action":"Login",
		"RequestedURL":"",
		"Lang":"fr",
		"TimeOffset":"-60",
	})
	return regex_token.findall(r.text.encode("utf-8"))[0];



"""
Get the higher age of the current queue
"""
def get_ages(token, queue_id):
	r = session_otrs.post(url_otrs, data={
		"ChallengeToken":token,
		"Action":"AgentTicketSearch",
		"Subaction":"Search",
		"EmptySearch":"1",
		"ShownAttributes":"%3BLabelFulltext%3BLabelStateIDs%3BLabelQueueIDs",
		"StateIDs":"1",
		"QueueIDs":queue_id,
		"AttributeOrig":"TicketNumber",
		"ResultForm":"Normal",
		"SortBy":"Age",
		"OrderBy":"Up",
	})

	return regex_age.findall(r.text.encode("utf-8"));



"""
Login into frwiki
"""
def login_wiki():
	r = session_wiki.post(url_wiki, data={
		"action":"login",
		"lgname":user_wiki,
		"lgpassword":password_wiki,
		"format":"json"
	})
	token = json.loads(r.text)["login"]["token"];
	r = session_wiki.post(url_wiki, data={
		"action":"login",
		"lgname":user_wiki,
		"lgpassword":password_wiki,
		"lgtoken":token,
		"format":"json"
	})
	if json.loads(r.text)["login"]["result"] != "Success":
		print "\033[1;31munsuccessful wiki login :(\033[0m"
		sys.exit()



"""
Get a crsf token from frwiki to be able to edit a page
"""
def get_crsf_token():
	r = session_wiki.post(url_wiki, data={
		"action":"query",
		"meta":"tokens",
		"type":"csrf",
		"assert":"user",
		"format":"json"
	})
	return json.loads(r.text)["query"]["tokens"]["csrftoken"]



"""
set on frwiki the new age on the given page
"""
def update_wiki(page, age):
	token = get_crsf_token()
	r = session_wiki.post(url_wiki, headers={'content-type': 'application/x-www-form-urlencoded'}, data={
		"action":"edit",
		"title":page,
		"text":age,
		"summary":"Mise à jour",
		"nocreate":"",
		"token":token,
		"assert":"bot",
		"format":"json"
	})



"""
Search for users and passwords in the config file
"""
def parse_config_file():
	global user_otrs, user_wiki, password_otrs, password_wiki
	if(os.path.isfile(os.path.dirname(os.path.realpath(__file__))+"/otrs_backlog.conf") == False):
		return;
	fichier = open(os.path.dirname(os.path.realpath(__file__))+"/otrs_backlog.conf", "r");
	contenu = fichier.read();
	fichier.close();
	for line in contenu.split("\n"):
		if re.search("^user_otrs:", line):
			user_otrs = line[10:];
		if re.search("^password_otrs:", line):
			password_otrs = line[14:];
		if re.search("^user_wiki:", line):
			user_wiki = line[10:];
		if re.search("^password_wiki:", line):
			password_wiki = line[14:];



"""
Get all missing parameters (users and passwords)
"""
def get_args():
	global user_otrs, user_wiki, password_otrs, password_wiki
	parse_config_file()
	if user_otrs == "":
		print "user_otrs";
		print "> ",;user_otrs = sys.stdin.readline().split("\n")[0];
	if password_otrs == "":
		print "password_otrs";
		print "> ",;password_otrs = sys.stdin.readline().split("\n")[0];
	if user_wiki == "":
		print "user_wiki";
		print "> ",;user_wiki = sys.stdin.readline().split("\n")[0];
	if password_wiki == "":
		print "password_wiki";
		print "> ",;password_wiki = sys.stdin.readline().split("\n")[0];



"""
Main function
"""
def main():
	get_args()
	token = login_otrs()
	login_wiki()
	for i in range(0,len(queues)):
		ages = get_ages(token, queues[i]['id'])
		if len(ages) > 0:
			age = ages[0].split(" ")
			if age[1] == "j":
				age = age[0]
			else:
				age = "0"
		else:
			age = "0"

		update_wiki(queues[i]['page'], age)
		print queues[i]['page'] + " : " + age + " jours"


main()
