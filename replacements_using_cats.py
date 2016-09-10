#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 12 May 2016
#License: GNU GPL v3
#Usage example: python replacements_using_cats.py -c "Portail:Castille-et-León/Articles liés" -o "({{ ?[EÉeé]bauche[^}]*\| ?)commune d'Espagne( ?[}|])" -n "\1commune d'Aragon\2" -s "Bot : Remplacement de '{{ébauche|commune d'Espagne}}' par '{{ébauche|commune de Castille-et-León}}'" --regex --dotall --ignorecase

import pywiki
import re
import sys


harmonization_table = [
    #category   text to find    text to put instead
    [u"Portail:Aragon/Articles liés", u"{{ébauche|commune d'Espagne}}", u"{{ébauche|commune d'Aragon}}"],
]

# Main
def main():
    category = ""
    old_text = ""
    new_text = ""
    summary = ""
    use_regex = False
    regex_flags = 0
    
    if "--regex" in sys.argv:
        use_regex = True
        if "--dotall" in sys.argv:
            regex_flags = re.DOTALL
        if "--ignorecase" in sys.argv:
            regex_flags = regex_flags | re.IGNORECASE
    
    if "-o" in sys.argv:
        index = sys.argv.index("-o")
        if len(sys.argv) >= index:
            old_text = sys.argv[index+1].decode("utf-8")
            if use_regex:
                old_text = re.compile(old_text, regex_flags);
        else:
            print "Missing value after parameter -o"
            sys.exit()
    else:
        print "Missing parameter -o"
        sys.exit()
    
    if "-n" in sys.argv:
        index = sys.argv.index("-n")
        if len(sys.argv) >= index:
            new_text = sys.argv[index+1].decode("utf-8")
        else:
            print "Missing value after parameter -n"
            sys.exit()
    else:
        print "Missing parameter -n"
        sys.exit()
    
    if "-c" in sys.argv:
        index = sys.argv.index("-c")
        if len(sys.argv) >= index:
            category = sys.argv[index+1].decode("utf-8")
        else:
            print "Missing category name after parameter -c"
            sys.exit()
    else:
        print "Missing parameter -c"
        sys.exit()
    
    if "-s" in sys.argv:
        index = sys.argv.index("-s")
        if len(sys.argv) >= index:
            summary = sys.argv[index+1].decode("utf-8")
        else:
            print "Missing value after parameter -s"
            sys.exit()
    else:
        summary = u"Bot : Remplacement de '"+old_text+u"' par '"+new_text+u"' dans la catégorie [[Category:"+category+u"|"+category+u"]]"
    
    
    pw = pywiki.Pywiki("frwiki-NeoBOT")
    pw.login()
    pw.limit = 500
    
    gcm_continue = ""
    i=0
    j=0
    while gcm_continue != None:
        (titles, gcm_continue) = pw.get_pages_in_cat("Category:"+category, gcm_continue=gcm_continue)
        contents = pw.get_content_list(titles)
        
        for content in contents:
            if use_regex:
                tmp = re.sub(old_text, new_text, content[1])
            else:
                tmp = content[1].replace(old_text, new_text)
            if content[1] != tmp:
                print content[0]
                pw.replace(content[0], tmp, summary, nocreate=True)
                j += 1
            i += 1
    print "Nombre de pages parcourues : " + str(i)
    print "Nombre de pages modifiés : " + str(j)
main()

