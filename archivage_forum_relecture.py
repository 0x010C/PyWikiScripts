#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 2 April 2016
#License: GNU GPL v3

import sys
import time
import json
from datetime import date, timedelta
import requests
import urllib
import pywiki

user = ""
password = ""
DAYS = 10

def json_findall(v, k):
	r = []
	if type(v) == type({}):
		for k1 in v:
			if k1 == k:
				r += [int(v[k1])]
			r += json_findall(v[k1], k)
	return r

def get_last_edition_time_flow_thread(self, thread):
	r = self.session.post(self.api_endpoint, data={
		"action":"flow",
		"submodule":"view-topic",
		"page":thread,
		"vtformat":"wikitext",
		"format":"json"
	})
	response = json.loads(r.text)
	return max(json_findall(response, "timestamp"))
pywiki.Pywiki.get_last_edition_time_flow_thread = get_last_edition_time_flow_thread



def update_flow_topic_summary(self, thread):
	r = self.session.post(self.api_endpoint, data={
		"action":"flow",
		"submodule":"view-topic-summary",
		"page":thread,
		"vtsformat":"wikitext",
		"format":"json"
	})
	response = json.loads(r.text)
	prev_revision = ""
	if "revisionId" in response["flow"]["view-topic-summary"]["result"]["topicsummary"]["revision"]:
		prev_revision = response["flow"]["view-topic-summary"]["result"]["topicsummary"]["revision"]["revisionId"]
	
	r = self.session.post(self.api_endpoint, data={
		"action":"flow",
		"submodule":"edit-topic-summary",
		"page":thread,
		"etsprev_revision":prev_revision,
		"etssummary":"{{Réponse ff|obsolète}}",
		"etsformat":"wikitext",
		"token":self.get_csrf_token(),
		"format":"json"
	})
pywiki.Pywiki.update_flow_topic_summary = update_flow_topic_summary


def close_flow_topic(self, thread):
	r = self.session.post(self.api_endpoint, data={
		"action":"flow",
		"submodule":"close-open-topic",
		"page":thread,
		"cotmoderationState":"close",
		"cotreason":"Discussion inactive depuis plus de "+str(DAYS)+" jours",
		"token":self.get_csrf_token(),
		"format":"json"
	})
pywiki.Pywiki.close_flow_topic = close_flow_topic

# Main
def main():
	pw = pywiki.Pywiki("https://fr.wikipedia.org/w/api.php", user, password, "user")
	pw.login()
	
	threads_in_cat = pw.get_all_pages_in_cat("Catégorie:Requête en attente d'une réponse", "2600")
	date_threshold = int((date.today() - timedelta(days=DAYS)).strftime("%Y%m%d%H%M%S"))
	i = 0
	for thread in threads_in_cat:
		if pw.get_last_edition_time_flow_thread("Sujet:"+thread) < date_threshold:
			pw.update_flow_topic_summary("Sujet:"+thread)
			pw.close_flow_topic("Sujet:"+thread)
		i += 1
		print i


main()


