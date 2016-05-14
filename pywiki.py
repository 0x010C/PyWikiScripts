#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 18 March 2016
#License: GNU GPL v3

import sys
import os
import time
import json
import requests

version = "v1.43"


class Pywiki:

	def __init__(self, config_name):
		user_path = os.path.dirname(os.path.realpath(__file__)) + "/users/"
		if not os.path.exists(user_path):
			os.makedirs(user_path)
		if(os.path.isfile(user_path+config_name+".py") == False):
			print "The user configuration file called '"+config_name+"' seems missing. Don't worry, we will create it yet :\n"
			print "user:"
			print "> ",;user = sys.stdin.readline().split("\n")[0]
			print "password:"
			print "> ",;password = sys.stdin.readline().split("\n")[0]
			print "assertion ('user' or 'bot'):"
			print "> ",;assertion = sys.stdin.readline().split("\n")[0]
			print "api endpoint (ex. 'https://en.wikipedia.org/w/api.php'):"
			print "> ",;api_endpoint = sys.stdin.readline().split("\n")[0]
			file = open("users/"+config_name+".py", "w")
			file.write("# -*- coding: utf-8  -*-\nuser = u'"+user+"'\npassword = u'"+password+"'\nassertion = u'"+assertion+"'\napi_endpoint = u'"+api_endpoint+"'")
			file.close()
		sys.path.append(user_path)
		config = __import__(config_name, globals(), locals(), [], -1)
		
		self.user = config.user
		self.password = config.password
		self.api_endpoint = config.api_endpoint
		self.assertion = config.assertion
		if self.assertion == "bot":
			self.limit = 5000
		else:
			self.limit = 500
		
		self.session = requests.Session()

	"""
	Perform a given request with a simple but usefull error managment
	"""
	def request(self, data):		
		relogin = 3
		while relogin:
			try:
				r = self.session.post(self.api_endpoint, data=data)
				response = json.loads(r.text)
				if response.has_key("error"):
					if response['error']['code'] == 'assertuserfailed':
						self.login()
						relogin -= 1
						continue
					break
				return response
			except requests.exceptions.ConnectionError:
				time.sleep(5)
				self.session = requests.Session()
				self.login()
				relogin -= 1
		raise Exception('API error', response['error'])


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
		r = self.request({
			"action":"query",
			"meta":"tokens",
			"type":"csrf",
			"assert":self.assertion,
			"format":"json"
		})
		return r["query"]["tokens"]["csrftoken"]


	"""
	Revert a given diff, if possible
	"""
	def revert(self, title, rev_id, summary):
		token = self.get_csrf_token()
		if self.assertion == "bot":
			prepare["bot"] = "1"
		r = self.session.post(self.api_endpoint, data={
			"action":"edit",
			"title":title,
			"undo":rev_id,
			"summary":summary,
			"nocreate":"",
			"token":token,
			"assert":self.assertion,
			"format":"json"
		})


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
			"gcmlimit":self.limit,
			"gcmcontinue":gcm_continue,
		})
		response = json.loads(r.text)
		if "continue" in response:
			gcm_continue = response["continue"]["gcmcontinue"]
		else:
			gcm_continue = None
		titles = []
		if "query" in response:
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
			"tilimit":self.limit,
			"ticontinue":ti_continue,
		})
		response = json.loads(r.text)
		if "continue" in response:
			ti_continue = response["continue"]["ticontinue"]
		else:
			ti_continue = None
			
		titles = []
		if "query" in response:
			raw_titles = response["query"]["pages"].itervalues().next()["transcludedin"]
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
	Get the N first redirect pages of the wiki
	"""
	def get_redirects(self, ns=None, gar_continue=""):
		data = {
			"action":"query",
			"format":"json",
			"generator":"allredirects",
			"garlimit":self.limit,
			"assert":self.assertion,
		}
		if ns != None:
			data["garnamespace"] = ns
		if gar_continue != "":
			data["garcontinue"] = gar_continue
		response = self.request(data)
		
		if "continue" in response:
			gar_continue = response["continue"]["garcontinue"]
		else:
			gar_continue = None
		page_list = response["query"]["pages"]
		titles = []
		for id in page_list:
			if page_list[id].has_key("title"):
				titles += [page_list[id]["title"]]
		return (titles,gar_continue)

	"""
	Get all redirect pages of the wiki
	"""
	def get_all_redirects(self, ns=None):
		gar_continue = ""
		all_titles = []
		while gar_continue != None:
			(titles, gar_continue) = self.get_redirects(ns, gar_continue)
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
			"assert":self.assertion,
			"format":"json"
		}
		if self.assertion == "bot":
			prepare["bot"] = 1
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
			"assert":self.assertion,
			"format":"json"
		}
		if self.assertion == "bot":
			prepare["bot"] = 1
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
	def replace(self, titles, text, summary, nocreate=False, createonly=False, use_ids=False):
		if isinstance(titles, (int, basestring)):
			titles = [titles]
		prepare={
			"action":"edit",
			"assert":self.assertion,
			"format":"json",
		}
		if self.assertion == "bot":
			prepare["bot"] = 1
		if nocreate:
			prepare["nocreate"] = ""
		elif createonly:
			prepare["createonly"] = ""
		for title in titles:
			data = prepare
			if use_ids:
				data['pageid'] = title
			else:
				data["title"] = title
			data["text"] = text.replace("$(title)", title)
			data["summary"] = summary.replace("$(title)", title)
			data["token"] = self.get_csrf_token()
			print data
			r = self.request(data)


	"""
	Get the number of notification of the currently-logged user
	"""
	def get_notifications_count(self):
		r = self.session.post(self.api_endpoint, data={
			"action":"query",
			"meta":"notifications",
			"notsections":"alert",
			"notprop":"count",
			"assert":self.assertion,
			"format":"json"
		})
		response = json.loads(r.text)
		return response["query"]["notifications"]["count"]


	def exist(self, titles, invert=False):
		r = self.session.post(self.api_endpoint, data={
			"action":"query",
			"format":"json",
			"titles":"|".join(titles),
			"prop":"info",
			"assert":self.assertion,
		})
	
		response = json.loads(r.text)
		page_list = response["query"]["pages"]
		result = []
		for id in page_list:
			if int(id) > 0 and not invert:
				result += [page_list[id]["title"]]
			elif int(id) < 0 and invert:
				result += [page_list[id]["title"]]
		return result


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


	def get_content(self, title):
		response = self.request({
			"action":"query",
			"format":"json",
			"prop":"revisions",
			"titles":title,
			"rvprop":"content",
			"rvlimit":"1",
			"assert":self.assertion,
		})["query"]["pages"]
		return response[response.keys()[0]]["revisions"][0]["*"]


	def get_content_list(self, titles):
		if isinstance(titles, basestring):
			titles = [titles]
		response = self.request({
			"action":"query",
			"format":"json",
			"prop":"revisions",
			"titles":"|".join(titles),
			"rvprop":"content",
			"assert":self.assertion,
		})["query"]["pages"]
		result = []
		for id in response:
			result += [[id, response[id]["revisions"][0]["*"]]]
		return result


