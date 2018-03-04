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
import datetime
import re


def get_blocked_ips(self, bkcontinue=""):
	data = {
		"action": "query",
		"format": "json",
		"list": "blocks",
		"formatversion": "2",
		"bkdir": "newer",
		"bklimit": "max",
		"bkprop": "id|user|by|timestamp|expiry|reason|flags",
		"bkshow": "temp|!account"
	}
	if bkcontinue != "":
		data["bkcontinue"] = bkcontinue

	response = self.request(data)

	bkcontinue = None
	if "continue" in response:
		bkcontinue = response["continue"]["bkcontinue"]

	return (response["query"]["blocks"], bkcontinue)

pywiki.Pywiki.get_blocked_ips = get_blocked_ips


def get_all_blocked_ips(self):
	bkcontinue = ""
	all_blocks = []
	while bkcontinue != None:
		(blocks, bkcontinue) = self.get_blocked_ips(bkcontinue)
		all_blocks += blocks
	return all_blocks
pywiki.Pywiki.get_all_blocked_ips = get_all_blocked_ips


def parse_date(date):
	return datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")


# Main
def main():
	pw = pywiki.Pywiki("frwiki-NeoBOT")
	pw.login()

	proxy_regex = re.compile(r'(proxy|vpn|tor)', re.UNICODE | re.IGNORECASE)

	blocks = pw.get_all_blocked_ips()

	now = datetime.datetime.today()

	ips = []
	for block in blocks:
		expiry = parse_date(block["expiry"])
		if (expiry - now).days <= 7 and not block["automatic"] and proxy_regex.search(block["reason"]):
			timestamp = parse_date(block["timestamp"])
			print block
			ips += [
				u"{{subst:Utilisateur:NeoBot/Proxy ouvert/expiration des blocages/ligne"
				+ u"|ip=" + block["user"]
				+ u"|par=" + block["by"]
				+ u"|bloqué le=" + timestamp.strftime("%Y-%m-%d")
				+ u"|expire le=" + expiry.strftime("%Y-%m-%d")
				+ u"|raison=" + block["reason"]
				+ u"}}"
			]


	wikitext = u"{{subst:Utilisateur:NeoBot/Proxy ouvert/expiration des blocages|nb="+str(len(ips))+"|list="+"\n".join(ips)+"}}"

	pw.replace(u"Wikipédia:Proxy ouvert/expiration des blocages", wikitext, u"bot: Mise à jour de la liste des proxy ouverts dont le blocage expire dans moins d'une semaine.", nocreate=True)
	print wikitext

main()

