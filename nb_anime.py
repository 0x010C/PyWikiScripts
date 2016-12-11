#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Autor: Thibaut120094
#       Antoine "0x010C" Lamielle
#Date: 10 December 2016
#License: GNU GPL v3

import feedparser
import re
import pywiki
import pwutils

supported_anime = {
    #u"title in args": [u"title in rss feed", u"on-wiki title"],
    u"Détective Conan": [u"Case Closed", u"Détective Conan"],
    u"Naruto Shippuden": [u"Naruto Shippuden", u"Naruto Shippuden"],
    u"One Piece": [u"One Piece", u"One Piece"],
}
rss_url = u"http://www.crunchyroll.com/rss/anime?lang=en"
wiki_data_page = u"Module:Nombre d'épisodes d'anime/data"

feed = feedparser.parse(rss_url)

pw = pywiki.Pywiki("frwiki-NeoBOT")
pw.login()

content = pw.get_content(wiki_data_page);

def anime_update(feed_title, wiki_title):
    global content
    
    for post in feed.entries:
        if feed_title in post.title:
            nbepisode = post.title
            break
    else:
        raise Exception("No data found for this anime.")

    match = re.search(ur'Episode (\d+)', nbepisode)
    nbepisode = match.group(1)

    match = re.search(ur'\s*?\["'+wiki_title+'"\]\s*?=\s*?(\d+)\s*?,', content)
    oldnbepisode = match.group(1)

    nbepisode = int(nbepisode)
    oldnbepisode = int(oldnbepisode)
    print(u'[[%s]]' % wiki_title)
    print(u'Crunchyroll: %d' % nbepisode)
    print(u'Wikipedia: %d' % oldnbepisode)
      
    if nbepisode > oldnbepisode:
        content = re.sub(ur'(\s*?\["'+wiki_title+'"\]\s*?=\s*?)\d+(\s*?,)', ur'\g<1>%d\g<2>' % (nbepisode), content)
        print(u'Content updated.\n')
    else :
        print(u'Nothing changed.\n')
        

def main():
    global content
    if pwutils.arg_parser("--all"):
        for title in supported_anime:
            try:
                anime_update(supported_anime[title][0], supported_anime[title][1])
            except:
                print(u'[[%s]]' % supported_anime[title][1])
                print('No data found for this anime.\n')
    else:
        title = pwutils.arg_parser("-t", value=True, required=True)
        if title not in supported_anime:
            raise Exception("This anime is not currently supported.")
        anime_update(supported_anime[title][0], supported_anime[title][1])
    
    pw.replace(wiki_data_page, content, u"Mise à jour depuis Crunchyroll.")
    print('Saved.')

main()
