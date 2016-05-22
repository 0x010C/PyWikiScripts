#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 22 Mai 2016
#License: GNU GPL v3

import pywiki
import requests


# Main
def main():
	pw = pywiki.Pywiki("frwiki-NeoBOT")
	pw.login()
	pw.limit = 500
	
	gap_continue = ""
	le_offset = 0
	while gap_continue != None:
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

		for id in response["query"]["pages"]:
			if "extlinks" in response["query"]["pages"][id]:
				#print response["query"]["pages"][id]["title"]
				for extlink in response["query"]["pages"][id]["extlinks"]:
					r = requests.get(extlink["*"])
					if r.status_code != 200:
						print response["query"]["pages"][id]["title"]+" --> ("+str(r.status_code)+") "+extlink["*"]
	
		if "continue" in response:
			if response["continue"]["continue"] == "gapcontinue||":
				gap_continue = response["continue"]["gapcontinue"]
				le_offset = 0
			else:
				le_offset = response["continue"]["eloffset"]
		else:
			gap_continue = None


main()
