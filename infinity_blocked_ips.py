#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 3 March 2018
#License: GNU GPL v3

import sys
import time
import json
import requests
import urllib
import pywiki


def get_infinity_blocked_ips(self):
	response = self.request({
		"action": "query",
		"format": "json",
		"list": "blocks",
		"bklimit": "max",
		"bkshow": "ip|!temp"
	})["query"]["blocks"]
	return response
pywiki.Pywiki.get_infinity_blocked_ips = get_infinity_blocked_ips


# Main
def main():
	pw = pywiki.Pywiki("frwiki-NeoBOT")
	pw.login()

	result = pw.get_infinity_blocked_ips()
	if len(result) == 0:
		return;

	ips = []
	for block in result:
		ips += ["* {{ip|"+block["user"]+"}}"]

	wikitext = u"{{subst:Utilisateur:NeoBot/IPs bloquées indéfiniment|nb="+str(len(ips))+"|list="+"\n".join(ips)+"}}"

	pw.append(u"Wikipédia:Requête aux administrateurs", wikitext, u"bot: IPs bloquées indéfiniment")
	print wikitext

main()

