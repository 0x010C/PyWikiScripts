#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 12 May 2016
#License: GNU GPL v3
#Usage example: python replacements_using_cats.py -c "Portail:Castille-et-León/Articles liés" -o "({{ ?[EÉeé]bauche[^}]*\| ?)commune d'Espagne( ?[}|])" -n "\1commune d'Aragon\2" -s "Bot : Remplacement de '{{ébauche|commune d'Espagne}}' par '{{ébauche|commune de Castille-et-León}}'" --regex --dotall --ignorecase

import pywiki
import pwutils
import re
import sys


pw = None


# Main
def cat_replace(category, old_text, new_text, summary, recursive=False, use_regex=False, regex_flags=0, namespace=pywiki.NS_MAIN):
    i=0
    j=0
    
    
    all_cats = set(["Category:"+category])
    if recursive:
        to_search = set(["Category:"+category])
        while to_search:
            gcm_continue = ""
            current_cat = to_search.pop()
            while gcm_continue != None:
                (cats, gcm_continue) = pw.get_pages_in_cat(current_cat, gcm_type="subcat", gcm_continue=gcm_continue)
                for cat in cats:
                    if cat not in all_cats:
                        to_search.add(cat)
                        all_cats.add(cat)

    for cat in all_cats:
        gcm_continue = ""
        while gcm_continue != None:
            (titles, gcm_continue) = pw.get_pages_in_cat(cat, gcm_type="page", gcm_continue=gcm_continue)
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
    print "Nombre de pages modifiées :  " + str(j)

def main():
    global pw
    
    pw = pywiki.Pywiki("frwiki-NeoBOT")
    pw.login()
    pw.limit = 500
    
    mass = pwutils.arg_parser("--mass", value=True, required=False, default=False)
    if mass:
        sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/conf/")
        mass_replacement = __import__(mass, globals(), locals(), [], -1).mass_replacement
        for request in mass_replacement:
            cat_replace(request[0], request[1], request[2], request[3], request[4], request[5], request[6], request[7])
        
    else:
        category = pwutils.arg_parser("-c", value=True, required=True)
        old_text = pwutils.arg_parser("-o", value=True, required=True)
        new_text = pwutils.arg_parser("-n", value=True, required=True)
        summary = pwutils.arg_parser("-s", value=True, default=u"Bot : Remplacement de '"+old_text+u"' par '"+new_text+u"' dans la catégorie [[Category:"+category+u"|"+category+u"]]")
        recursive = pwutils.arg_parser("--recursive")
        namespace = pwutils.arg_parser("--namespace", value=True, default=pywiki.NS_MAIN)
        use_regex = pwutils.arg_parser("--regex")
        regex_flags = ""
        if use_regex:
            if pwutils.arg_parser("--dotall"):
                regex_flags = re.DOTALL
            if pwutils.arg_parser("--ignorecase"):
                regex_flags = regex_flags | re.IGNORECASE
            old_text = re.compile(old_text, regex_flags);
        
        cat_replace(category, old_text, new_text, summary, recursive, use_regex, regex_flags, namespace)




main()

