#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 23 March 2016
#License: GNU GPL v3

import sys
import time
import json
import requests
import urllib
import pywiki


def has_backlinks(self, title):
	response = self.request({
		"action":"query",
		"format":"json",
		"titles":title,
		"prop":"linkshere",
		"assert":self.assertion,
	})["query"]["pages"]
	if response[response.keys()[0]].has_key("linkshere"):
		return True
	else:
		return False
pywiki.Pywiki.has_backlinks = has_backlinks


def exist_talk_page(self, titles):
	talk_page_titles_join = "|".join("Discussion:"+title for title in titles)
	response = self.request({
		"action":"query",
		"format":"json",
		"titles":talk_page_titles_join,
		"prop":"info",
		"inprop":"watchers",
		"assert":self.assertion,
	})
	
	page_list = response["query"]["pages"]
	titles_redirect = []
	titles_content = []
	for id in page_list:
		if int(id) > 0:
			if not self.has_backlinks(page_list[id]["title"]):
				if page_list[id].has_key("redirect"):
					new = False
					if page_list[id].has_key("new"):
						new = True
					titles_redirect += [[page_list[id]["title"], new]] #TODO: check, watchers seems not be returned any more
				else:
					titles_content += [page_list[id]["title"]]
	return (titles_redirect,titles_content)
pywiki.Pywiki.exist_talk_page = exist_talk_page




# Main
def main():
	pw = pywiki.Pywiki("frwiki-0x010C")
	pw.login()
	pw.limit = 500
	
	gar_continue = ""
	i=0
	j = 0
	while gar_continue != None:
		#while i < 200000:
		(titles, gar_continue) = pw.get_redirects(0, gar_continue)
		(titles_redirect,titles_content) = pw.exist_talk_page(titles)
		for t in titles_redirect:
			if t[1]: #If the page is tagged with "new" (== if there is only one diff)
				print t
				pw.delete(t[0], "Page de discussion d'une redirection")
				time.sleep(0.3)
				j += 1
		i += pw.limit
		print str(i)+"#"+str(j)
main()

