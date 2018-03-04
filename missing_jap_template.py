#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 20 Mai 2016
#License: GNU GPL v3

import pywiki
import re


#Paramètres
searched_cat = "Catégorie:Portail:Japon/Articles liés"
regex = re.compile(ur"\{\{([Jj]aponais|[Nn]ihongo)")
page = u"User:NeoBot/Modèle japonais manquant"


# Main
def main():
	pw = pywiki.Pywiki("frwiki-NeoBOT")
	pw.login()
	pw.limit = 500
	
	gcm_continue = ""
	all_titles = []
	i = 0
	while gcm_continue != None:
		(titles, gcm_continue) = pw.get_pages_in_cat(searched_cat, 0, gcm_continue)
		contents = pw.get_content_list(titles)
		
		for content in contents:
			if not regex.search(content[1]):
				all_titles += [content[0]]
		i += pw.limit
		print i
	
	
	text = u"{{Mise à jour bot|0x010C}}\n\n"
	for title in all_titles:
		text += u"* [["+title+u"]]\n"
	
	pw.replace(page, text, "Bot : Update list")


main()
