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
		"assert":self.assertion,
	})
	
	page_list = response["query"]["pages"]
	titles_redirect = []
	titles_content = []
	for id in page_list:
		if int(id) > 0:
			if not self.has_backlinks(page_list[id]["title"]):
				if page_list[id].has_key("redirect"):
					titles_redirect += [page_list[id]["title"]]
				else:
					titles_content += [page_list[id]["title"]]
	return (titles_redirect,titles_content)
pywiki.Pywiki.exist_talk_page = exist_talk_page




# Main
def main():
	pw = pywiki.Pywiki("frwiki-0x010C")
	pw.login()
	
	gar_continue = ""
	i=0
	j = 0
	while gar_continue != None:
		#while i < 200000:
		(titles, gar_continue) = pw.get_redirects(0, gar_continue)
		(titles_redirect,titles_content) = pw.exist_talk_page(titles)
		for t in titles_redirect:
			print t
			pw.delete(t, "Page de discussion d'une redirection")
			time.sleep(1)
			j += 1
		i += pw.limit
		print str(i)+"#"+str(j)
	#header_table = '{| class="wikitable"\n|-\n! Titre !! redirect=no !! suppression !! redirect ?'
	#footer_table = '\n|}\n'
	#pw.replace("Utilisateur:NeoBOT/Liste des pages de discussion de redirections", header_table + "\n".join('\n|-\n| [['+t[0]+']] || [https://fr.wikipedia.org/w/index.php?title='+urllib.quote_plus(t[0].encode('utf8'))+'&redirect=no (nr)] || [https://fr.wikipedia.org/w/index.php?title='+urllib.quote_plus(t[0].encode('utf8'))+'&action=delete&wpReason=Page%20de%20discussion%20d\'une%20redirection (suppr)] || '+t[1] for t in sorted_titles) + footer_table, "Mise à jour de la liste")

main()

