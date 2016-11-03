#!/usr/bin/python
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 2 November 2016
#License: GNU GPL v3
import requests
import re
import os
import sys


base_path = "/home/www/wmdumps/"
wiki_list = ["frwiki", "alswiki", "frwikinews", "frwikiquote", "cawiki", "dewiki"]


def download_dump(url, filename):
    print str(i)+".\t\033[93m[STARTING]\033[0m "+url+"\r",
    sys.stdout.flush()
    r = requests.get(url, stream=True)
    total_length = int(r.headers.get('content-length'))*2
    dl_length = 0
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=65536):
            if chunk:
                dl_length += len(chunk)
                f.write(chunk)
                dl_length += len(chunk)
                print str(i)+".\t\033[93m["+str(int(100*dl_length/total_length))+"% ("+str(dl_length)+"/"+str(total_length)+")]\033[0m "+url+"\r",
                sys.stdout.flush()


base_path = ""
wiki_list = []

if len(sys.argv) > 1:
    if os.path.isfile(sys.argv[1]):
        path = os.path.dirname(sys.argv[1])
        if path[0] != '/':
            path = os.path.abspath(path)
        sys.path.append(path)
        conf = __import__(os.path.basename(sys.argv[1][:-3]), globals(), locals(), [], -1)
        base_path = conf.base_path
        wiki_list = conf.wiki_list

if wiki_list == []:
    print "Enter all the wiki-aliases (e.g. enwiki, frwikinews,...) you want to get the dump, separated by semicolons"
    print "> ",;wiki_list = sys.stdin.readline().split("\n")[0].split(";")
if base_path == "":
    print "Directory in whitch the script should store the dumps:"
    print "> ",;base_path = sys.stdin.readline().split("\n")[0]
    if base_path[-1] != '/':
        base_path += '/'


for wiki in wiki_list:
    print "\033[94m"+wiki+"\033[0m"
    latest = requests.get("https://dumps.wikimedia.org/"+wiki+"/latest/")
    rss_filenames = re.findall("<a href=\"("+wiki+"-latest-pages-meta-history[0-9]*\.xml(?:-p[0-9]+p[0-9]+)?\.bz2-rss\.xml)", latest.text)
    i=1
    if not os.path.exists(base_path+wiki):
        os.makedirs(base_path+wiki)
    for rss_filename in rss_filenames:
        rss_data = requests.get("https://dumps.wikimedia.org/"+wiki+"/latest/"+rss_filename)
        (url, date) = re.findall("href=\"http://(download.wikimedia.org/"+wiki+"/([0-9]+)/"+wiki+"-[0-9]+-pages-meta-history[0-9]*.xml(?:-p[0-9]+p[0-9]+)?.bz2)\"", rss_data.text)[0]
        filename = base_path+wiki+"/"+date+"/"+url.split('/')[-1]
        if not os.path.exists(base_path+wiki+"/"+date):
            os.makedirs(base_path+wiki+"/"+date)
        if(os.path.isfile(filename) == False):
            download_dump("https://"+url, filename)
            print str(i)+".\t\033[92m[DONE]\033[0m "+url
        else:
            print str(i)+".\t\033[92m[CACHED]\033[0m "+url
        i+=1



