#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 20 February 2016
#License: GNU GPL v3

import sys
import time
import json
import requests


#Paramètres
version = "1.00"
src_api_endpoint = "https://en.wiktionary.org/w/api.php"
dst_api_endpoint = "https://fr.wiktionary.org/w/api.php"
user = ""
password = ""
src_lang = "en"
dst_lang = "fr"
searched_template = "Template:ja-noun"
page_list = "Utilisateur:0x010C/list/ja-noun"
session = requests.Session()



"""
Login into the wiki
"""
def login(api_endpoint):
	r = session.post(api_endpoint, data={
		"action":"login",
		"lgname":user,
		"lgpassword":password,
		"format":"json"
	})
	token = json.loads(r.text)["login"]["token"];
	r = session.post(src_api_endpoint, data={
		"action":"login",
		"lgname":user,
		"lgpassword":password,
		"lgtoken":token,
		"format":"json"
	})
	if json.loads(r.text)["login"]["result"] != "Success":
		print "\033[1;31munsuccessful wiki login :(\033[0m"
		sys.exit()

"""
Get a crsf token from frwiki to be able to edit a page
"""
def get_csrf_token(api_endpoint):
	r = session.post(api_endpoint, data={
		"action":"query",
		"meta":"tokens",
		"type":"csrf",
		"assert":"user",
		"format":"json"
	})
	return json.loads(r.text)["query"]["tokens"]["csrftoken"]

def get_transcluded_pages(ticontinue):
	r = session.post(src_api_endpoint, data={
		"action":"query",
		"format":"json",
		"prop":"transcludedin",
		"titles":searched_template,
		"tiprop":"title",
		"tinamespace":"0",
		"tilimit":"500",
		"ticontinue":ticontinue,
	})
	response = json.loads(r.text)
	if "continue" in response:
		ticontinue = response["continue"]["ticontinue"]
	else:
		ticontinue = None
	raw_titles = response["query"]["pages"].itervalues().next()["transcludedin"]
	titles = []
	for title in raw_titles:
		titles += [title["title"]]
	return (titles,ticontinue)


def get_missing_lang_links(titles):
	r = session.post(src_api_endpoint, data={
		"action":"query",
		"format":"json",
		"prop":"langlinks",
		"titles":"|".join(titles),
		"lllang":dst_lang,
	})
	pages = json.loads(r.text)["query"]["pages"]
	titles = []
	for key in pages:
		if not("langlinks" in pages[key]):
			titles += [pages[key]["title"]]
	return titles


def save(titles):
	text = "This is a bot-generated list. Contact [[User:0x010C]] for more details.\n\n"
	text += "'''"+str(len(titles))+" pages''' transcluing [[:"+src_lang+":"+searched_template+"]] on en.wikit doesn't exist here.\n\n"
	for title in titles:
		text += "* [[:"+src_lang+":"+title+"|"+title+u"]]  →  [["+title+"]]\n"
	token = get_csrf_token(dst_api_endpoint)
	r = session.post(dst_api_endpoint, data={
		"action":"edit",
		"title":page_list,
		"text":text,
		"summary":"Bot : Update list",
		"nocreate":"",
		"token":token,
		"assert":"user",
		"format":"json"
	})

# Main
def main():
	login(src_api_endpoint)
	ticontinue = ""
	all_titles = []
	i = 0
	while ticontinue != None:
		(titles, ticontinue) = get_transcluded_pages(ticontinue)
		i += 500
		print i
		all_titles += get_missing_lang_links(titles)
	#login(dst_api_endpoint)
	save(all_titles)


main()
