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
import pywiki



queues  = [
	{"page":u"Wikipédia:OTRS/backlog-info-fr", "id":u"19"},
	{"page":u"Wikipédia:OTRS/backlog-permissions-commons-fr", "id":u"127"},
	{"page":u"Wikipédia:OTRS/backlog-permissions-fr", "id":u"35"},
	{"page":u"Wikipédia:OTRS/backlog-photosubmissions-fr", "id":u"129"},
]
url_otrs = u"https://ticket.wikimedia.org/otrs/index.pl"
user_otrs = u""
password_otrs = u""
regex_token = re.compile(u"name=\"ChallengeToken\" value=\"([0-9a-zA-Z]+)\"")
regex_age = re.compile(u"<div title=\"([0-9]+ [jhm](?: [0-9]+ [hm])*) *\">")
session_otrs = requests.Session()



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
		"Attribute":"TicketNumber",
		"ResultForm":"Normal",
		"SortBy":"Age",
		"OrderBy":"Up",
	})

	return regex_age.findall(r.text.encode("utf-8"));


"""
Search for users and passwords in the config file
"""
def parse_config_file():
	global user_otrs, password_otrs
	if(os.path.isfile(os.path.dirname(os.path.realpath(__file__))+"/conf/otrs_backlog.conf") == False):
		return;
	fichier = open(os.path.dirname(os.path.realpath(__file__))+"/conf/otrs_backlog.conf", "r");
	contenu = fichier.read();
	fichier.close();
	for line in contenu.split("\n"):
		if re.search("^user_otrs:", line):
			user_otrs = line[10:];
		if re.search("^password_otrs:", line):
			password_otrs = line[14:];


"""
Get all missing parameters (users and passwords)
"""
def get_args():
	global user_otrs, password_otrs
	parse_config_file()
	if user_otrs == "":
		print "user_otrs";
		print "> ",;user_otrs = sys.stdin.readline().split("\n")[0];
	if password_otrs == "":
		print "password_otrs";
		print "> ",;password_otrs = sys.stdin.readline().split("\n")[0];


"""
Main function
"""
def main():
	get_args()
	token = login_otrs()
	pw = pywiki.Pywiki("frwiki-NeoBOT")
	pw.login()
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
		pw.replace(queues[i]['page'], age, u"Mise à jour du backlog des files OTRS francophones", nocreate=True)
		print queues[i]['page'] + " : " + age + " jours"


main()

