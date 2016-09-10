#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 30 June 2016
#License: GNU GPL v3
#Usage: python move_category.py -o "Old category name" -n "New category name" --move --delete

import sys
import re
import pywiki


# Main
def main():
    old_cat = ""
    new_cat = ""
    
    if "-o" in sys.argv:
        index = sys.argv.index("-o")
        if len(sys.argv) >= index:
            old_cat = sys.argv[index+1].decode("utf-8")
        else:
            print "Missing category name after parameter -o"
            sys.exit()
    else:
        print "Missing parameter -o"
        sys.exit()
    
    if "-n" in sys.argv:
        index = sys.argv.index("-n")
        if len(sys.argv) >= index:
            new_cat = sys.argv[index+1].decode("utf-8")
        else:
            print "Missing category name after parameter -n"
            sys.exit()
    else:
        print "Missing parameter -n"
        sys.exit()

    regex = re.compile(ur'(\n?\[\[ *(?:Category|Catégorie) *: ?)'+old_cat+ur'( *(?:| *[^\]]+ *)?\]\])', re.DOTALL | re.IGNORECASE)
    
    pw = pywiki.Pywiki("frwiki-NeoBOT")
    pw.login()
    pw.limit = 500
    titles = pw.get_all_pages_in_cat("Category:"+old_cat)

    while titles:
        contents = pw.get_content_list(titles[:500])
        for (title,content) in contents:
            if new_cat == "":
                new_content = regex.sub(ur"", content)
            else:
                new_content = regex.sub(ur"\1"+new_cat+ur"\2", content)
            
            if new_content != content:
                print title
                pw.replace(title, new_content, u"Bot : Remplacement de [[Catégorie:"+old_cat+u"]] par [[Catégorie:"+new_cat+u"]]", nocreate=True)
        titles = titles[500:]
    
    pw = pywiki.Pywiki("frwiki-0x010C")
    pw.login()
    if "--move" in sys.argv:
        if "--delete" in sys.argv:
            no_redirect = True
        else:
            no_redirect = False
        pw.move(u"Category:"+old_cat, u"Category:"+new_cat, u"Renommage de catégorie", no_redirect=no_redirect, move_talk=True, ignore_warnings=True)
    elif "--delete" in sys.argv:
        pw.delete(u"Category:"+old_cat, u"Categorie déplacé vers [[Catégorie:"+new_cat+"]]")


main()
