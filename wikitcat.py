#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 20 February 2016
#License: GNU GPL v3

import sys
import time
import json
import requests
import pywiki


#Paramètres
version = "1.02"
src_lang = "en"
dst_lang = "fr"
searched_template = "Template:ja-noun"
editintro_template = "Utilisateur:Thibaut120094/template_ja"


# Main
def main():
	pw_src = pywiki.Pywiki(src_lang+"wikit-NeoBOT")
	pw_dst = pywiki.Pywiki(dst_lang+"wikit-NeoBOT")
	pw_src.login()
	pw_dst.login()
	
	ti_continue = ""
	all_titles = []
	i = 0
	while ti_continue != None:
		(titles, ti_continue) = pw_src.get_transcluded_pages(searched_template, 0, ti_continue)
		i += pw_src.limit
		print i
		all_titles += pw_dst.exist(titles, invert=True)
	
	
	text = "This is a bot-generated list. Contact [[User:0x010C]] for more details.\n\n"
	text += "'''"+str(len(all_titles))+" pages''' transcluing [[:"+src_lang+":"+searched_template+"]] on "+src_lang+".wikit doesn't exist here.\n\n"
	for title in all_titles:
		text += "* [[:"+src_lang+":"+title+"|"+title+u"]]  →  [["+title+"]] <small>[https://"+dst_lang+".wiktionary.org/w/index.php?action=edit&editintro="+editintro_template+"&title="+title+" (create)]</small>\n"
	
	pw_dst.replace("User:NeoBOT/list/"+searched_template, text, "Bot : Update list")


main()
