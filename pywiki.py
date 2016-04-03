#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 18 March 2016
#License: GNU GPL v3

import sys
import time
import json
import requests

version = "v1.00"


class Pywiki:

	def __init__(self, api_endpoint, user, password, mw_assert="bot"):
		self.api_endpoint = api_endpoint
		self.user = user
		self.password = password
		self.mw_assert = mw_assert
		self.session = requests.Session()
	
	"""
	Login into the wiki
	"""
	def login(self):
		r = self.session.post(self.api_endpoint, data={
			"action":"login",
			"lgname":self.user,
			"lgpassword":self.password,
			"format":"json"
		})
		token = json.loads(r.text)["login"]["token"];
		r = self.session.post(self.api_endpoint, data={
			"action":"login",
			"lgname":self.user,
			"lgpassword":self.password,
			"lgtoken":token,
			"format":"json"
		})
		if json.loads(r.text)["login"]["result"] != "Success":
			return -1
		return 0


	"""
	Get a crsf token from frwiki to be able to edit a page
	"""
	def get_csrf_token(self):
		r = self.session.post(self.api_endpoint, data={
			"action":"query",
			"meta":"tokens",
			"type":"csrf",
			"assert":self.mw_assert,
			"format":"json"
		})
		return json.loads(r.text)["query"]["tokens"]["csrftoken"]


	"""
	Revert a given diff, if possible
	"""
	def revert(self, title, rev_id, summary):
		token = self.get_csrf_token()
		r = self.session.post(self.api_endpoint, data={
			"action":"edit",
			"title":title,
			"undo":rev_id,
			"summary":summary,
			"nocreate":"",
			"token":token,
			"assert":self.mw_assert,
			"format":"json"
		})
		print r.text


	"""
	Get N pages of a category, starting at offset gcm_continue if given
	"""
	def get_pages_in_cat(self, category, ns=None, gcm_continue=""):
		if ns == None:
			ns = ""
		elif isinstance(ns, list):
			ns = "|".join(str(i) for i in ns)

		r = self.session.post(self.api_endpoint, data={
			"action":"query",
			"format":"json",
			"generator":"categorymembers",
			"gcmtitle":category,
			"gcmnamespace":ns,
			"gcmlimit":"500",
			"gcmcontinue":gcm_continue,
		})
		response = json.loads(r.text)
		if "continue" in response:
			gcm_continue = response["continue"]["gcmcontinue"]
		else:
			gcm_continue = None
		titles = []
		for i in response["query"]["pages"]:
			titles += response["query"]["pages"][i]["title"].split(":")[1:]
		return (titles,gcm_continue)


	"""
	Get all pages of a category
	@param string category : The category name, including the prefixed namespace (ex: "Category:Python")
	@param list ns : A list of the numeric value of the namespaces to work on, will ignore all the others (ex: [0,1,4]) ; if None is given, it will include all the namespaces
	"""
	def get_all_pages_in_cat(self, category, ns=None):
		gcm_continue = ""
		all_titles = []
		while gcm_continue != None:
			(titles, gcm_continue) = self.get_pages_in_cat(category, ns, gcm_continue)
			all_titles += titles
		return all_titles


	"""
	Get N pages that transclude a template
	"""
	def get_transcluded_pages(self, title, ns=None, ti_continue=""):
		if ns == None:
			ns = ""
		elif isinstance(ns, list):
			ns = "|".join(str(i) for i in ns)
	
		r = self.session.post(self.api_endpoint, data={
			"action":"query",
			"format":"json",
			"prop":"transcludedin",
			"titles":title,
			"tiprop":"title",
			"tinamespace":ns,
			"tilimit":"500",
			"ticontinue":ti_continue,
		})
		response = json.loads(r.text)
		if "continue" in response:
			ti_continue = response["continue"]["ticontinue"]
		else:
			ti_continue = None
		raw_titles = response["query"]["pages"].itervalues().next()["transcludedin"]
		titles = []
		for title in raw_titles:
			titles += [title["title"]]
		return (titles,ti_continue)


	"""
	Get all pages that transclude a template
	"""
	def get_all_transcluded_pages(self, title, ns=None):
		ti_continue = ""
		all_titles = []
		while ti_continue != None:
			(titles, ti_continue) = self.get_transcluded_pages(title, ns, ti_continue)
			all_titles += titles
		return all_titles


	"""
	Append the given text to a page, or a list of pages
	@param list/string titles : A list of pages to append the text (if only a page has to be processed, it could be passed as a string)
	@param string text : The text to append ; all the "$(title)" will be replaced by the title of the page.
	@param string summary : the summary of the edit; all the "$(title)" will be replaced by the title of the page.
	@param bool nocreate : if it's set to True, the edit will fail when the page doesn't exist
	@param bool createonly : if it's set to True, the edit will fail when the page already exists
	"""
	def append(self, titles, text, summary, nocreate=False, createonly=False):
		if isinstance(titles, basestring):
			titles = [titles]
		data={
			"action":"edit",
			"assert":self.mw_assert,
			"format":"json"
		}
		if nocreate:
			data["nocreate"] = ""
		elif createonly:
			data["createonly"] = ""
		for title in titles:
			data["title"] = title
			data["appendtext"] = text.replace("$(title)", title)
			data["summary"] = summary.replace("$(title)", title)
			data["token"] = self.get_csrf_token()
			r = self.session.post(self.api_endpoint, data=data)


	"""
	Prepend the given text to a page, or a list of pages
	@param list/string titles : A list of pages onto the text should be prepend (if only a page has to be processed, it could be passed as a string)
	@param string text : The text to prepend ; all the "$(title)" will be replaced by the title of the page.
	@param string summary : the summary of the edit; all the "$(title)" will be replaced by the title of the page.
	@param bool nocreate : if it's set to True, the edit will fail when the page doesn't exist
	@param bool createonly : if it's set to True, the edit will fail when the page already exists
	"""
	def prepend(self, titles, text, summary, nocreate=False, createonly=False):
		if isinstance(titles, basestring):
			titles = [titles]
		data={
			"action":"edit",
			"assert":self.mw_assert,
			"format":"json"
		}
		if nocreate:
			data["nocreate"] = ""
		elif createonly:
			data["createonly"] = ""
		for title in titles:
			data["title"] = title
			data["prependtext"] = text.replace("$(title)", title)
			data["summary"] = summary.replace("$(title)", title)
			data["token"] = self.get_csrf_token()
			r = self.session.post(self.api_endpoint, data=data)


	"""
	Replace the content of a page (or a list of pages) with the given text
	@param list/string titles : A list of pages to append the text (if only a page has to be processed, it could be passed as a string)
	@param string text : The text to append ; all the "$(title)" will be replaced by the title of the page.
	@param string summary : the summary of the edit; all the "$(title)" will be replaced by the title of the page.
	@param bool nocreate : if it's set to True, the edit will fail when the page doesn't exist
	@param bool createonly : if it's set to True, the edit will fail when the page already exists
	"""
	def replace(self, titles, text, summary, nocreate=False, createonly=False):
		if isinstance(titles, basestring):
			titles = [titles]
		data={
			"action":"edit",
			"assert":self.mw_assert,
			"format":"json"
		}
		if nocreate:
			data["nocreate"] = ""
		elif createonly:
			data["createonly"] = ""
		for title in titles:
			data["title"] = title
			data["text"] = text.replace("$(title)", title)
			data["summary"] = summary.replace("$(title)", title)
			data["token"] = self.get_csrf_token()
			r = self.session.post(self.api_endpoint, data=data)


	"""
	Get the number of notification of the currently-logged user
	"""
	def getNotificationsCount(self):
		r = self.session.post(self.api_endpoint, data={
			"action":"query",
			"meta":"notifications",
			"notsections":"alert",
			"notprop":"count",
			"assert":self.mw_assert,
			"format":"json"
		})
		response = json.loads(r.text)
		return response["query"]["notifications"]["count"]


	"""
	Delete some pages
	"""
	def delete(self, titles, reason):
		if isinstance(titles, basestring):
			titles = [titles]
	
		data = {
			"action":"delete",
			"format":"json",
			"reason":reason,
		}
		for title in titles:
			data["title"] = title
			data["token"] = self.get_csrf_token()
			r = self.session.post(self.api_endpoint, data=data)



