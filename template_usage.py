#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 10 July 2016
#License: GNU GPL v3

import sys
import pywiki


# Main
def main():
	pw = pywiki.Pywiki("frwiki-NeoBOT")
	pw.login()
	
	ti_continue = ""
	title = sys.argv[1]
	count = 0
	while ti_continue != None:
		(titles, ti_continue) = pw.get_transcluded_pages(title, ti_continue=ti_continue)
		count += len(titles)
		print count
	print count

main()

