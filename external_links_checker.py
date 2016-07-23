#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 22 Mai 2016
#License: GNU GPL v3

import pywiki
import requests
import threading
import time
import re
from collections import deque


lock = threading.Lock()
links = deque()
nb_article_crawled = 0
nb_links_found = 0
nb_links_found_lock = threading.Lock()

blacklist = [
	"wikimedia.org",
	"wikipedia.org",
	"www.minorplanetcenter.net",
]

headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
}


class LinkChecker (threading.Thread):
	def __init__(self, threadID):
		threading.Thread.__init__(self)
		self.threadID = threadID
	def run(self):
		global nb_links_found
		print "Starting " + str(self.threadID)
		while True:
			with lock:
				try:
					(title, link) = links.popleft()
					print str(nb_links_found)+"#"+str(nb_article_crawled)+"#\t"+str(len(links))
				except IndexError:
					print "pause"+str(self.threadID)
					link = None
			if link == None:
				time.sleep(2)
				continue
			
			found = False
			try:
				r = requests.get(link, headers=headers)
				if r.status_code != 200:
					print title+" --> ("+str(r.status_code)+") "+link
					found = True
			except requests.exceptions.ConnectionError:
				print title+" --> (DOM) "+link
				found = True
			except requests.exceptions.TooManyRedirects:
				print title+" --> (RED) "+link
				found = True
			
			if found:
				with nb_links_found_lock:
					nb_links_found += 1
			
		print "Exiting " + str(self.threadID)


# Main
def main():
	global links, nb_article_crawled
	pw = pywiki.Pywiki("frwiki-NeoBOT")
	pw.login()
	pw.limit = 500
	
	blacklist_r = "("
	for site in blacklist:
		blacklist_r += site + "|"
	blacklist_r = re.compile(blacklist_r[:-1]+")")

	threads = []
	for i in range(0,392):
		threads.append(LinkChecker(i))
		threads[i].start()
	
	gap_continue = ""
	le_offset = 0
	while gap_continue != None:
		need_more_links = False
		with lock:
			if len(links) < 700:
				need_more_links = True
		
		if need_more_links:
			print "Get more links"
			response = pw.request({
				"action":"query",
				"format":"json",
				"prop":"extlinks",
				"generator":"allpages",
				"elexpandurl":"1",
				"ellimit":pw.limit,
				"gaplimit":pw.limit,
				"eloffset":le_offset,
				"gapcontinue":gap_continue,
				"assert":pw.assertion,
			})

			with lock:
				for id in response["query"]["pages"]:
					if "extlinks" in response["query"]["pages"][id]:
						for extlink in response["query"]["pages"][id]["extlinks"]:
							if not blacklist_r.search(extlink["*"]):
								links.append((response["query"]["pages"][id]["title"], extlink["*"]))
	
			if "continue" in response:
				if response["continue"]["continue"] == "gapcontinue||":
					gap_continue = response["continue"]["gapcontinue"]
					le_offset = 0
					nb_article_crawled += pw.limit
				else:
					le_offset = response["continue"]["eloffset"]
			else:
				gap_continue = None
		else:
			time.sleep(10)

main()
