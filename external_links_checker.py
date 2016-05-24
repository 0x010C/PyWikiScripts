#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 22 Mai 2016
#License: GNU GPL v3

import pywiki
import requests
import threading
import time
from collections import deque


lock = threading.Lock()
links = deque()

class LinkChecker (threading.Thread):
	def __init__(self, threadID):
		threading.Thread.__init__(self)
		self.threadID = threadID
	def run(self):
		print "Starting " + str(self.threadID)
		while True:
			with lock:
				try:
					(title, link) = links.popleft()
					print str(self.threadID)+"#"+str(len(links))
				except IndexError:
					print "pause"+str(self.threadID)
					link = None
			if link == None:
				time.sleep(2)
				continue
			
			try:
				r = requests.get(link)
				if r.status_code != 200:
					print title+" --> ("+str(r.status_code)+") "+link
			except requests.exceptions.ConnectionError:
				print title+" --> (DOM) "+link
			except requests.exceptions.TooManyRedirects:
				print title+" --> (RED) "+link
			
		print "Exiting " + str(self.threadID)


# Main
def main():
	global links
	pw = pywiki.Pywiki("frwiki-NeoBOT")
	pw.login()
	pw.limit = 500
	
	threads = []
	for i in range(0,64):
		threads.append(LinkChecker(i))
		threads[i].start()
	
	gap_continue = ""
	le_offset = 0
	while gap_continue != None:
		need_more_links = False
		with lock:
			if len(links) < 200:
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
						#print response["query"]["pages"][id]["title"]
						for extlink in response["query"]["pages"][id]["extlinks"]:
							links.append((response["query"]["pages"][id]["title"], extlink["*"]))
	
			if "continue" in response:
				if response["continue"]["continue"] == "gapcontinue||":
					gap_continue = response["continue"]["gapcontinue"]
					le_offset = 0
				else:
					le_offset = response["continue"]["eloffset"]
			else:
				gap_continue = None
		else:
			time.sleep(10)

main()
