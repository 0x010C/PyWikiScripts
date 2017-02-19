#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 18 February 2017
#License: GNU GPL v3

import pywiki
import pwutils
import csv
import os
from datetime import date


template = """== {{int:filedesc}} ==

{{Artwork
 |artist       = $artist
 |title        = $title
 |description  = $description
 |object type  = $object_type
 |date         = $date
 |medium       = $medium
 |dimensions   = {{Size|cm|$width|$height}}
 |institution  = $institution
 |inscriptions = $inscriptions
 |permission   = $permission
{{CC-zero}}
 |source       = $source - uploaded by [[User:0x010C|]]
}}
$categories
"""

mediums = ['{{Azulejo}}', '{{Bronze}}', '{{Drawing}}', '{{Engraving}}', '{{Etching}}', '{{Fresco}}', '{{Gouache}}', '{{Gouache on paper}}', '{{Hanging scroll}}', '{{Illumination on parchment}}', '{{Ink}}', '{{Landscape}}', '{{Lithography}}', '{{Mosaic}}', '{{Oil on canvas}}', '{{Oil on canvas panel}}', '{{Oil on cardboard}}', '{{Oil on copper}}', '{{Oil on panel}}', '{{Pencil on paper}}', '{{Stained glass}}', '{{Tapestry}}', '{{Tempera on canvas}}', '{{Tempera on panel}}', '{{Watercolor}}', '{{Watercolor on cardboard}}', '{{Watercolor on paper}}', '{{Woodcut}}']


def uploader(file_name, artist, birth, death, title, description_en, description_fr, object_type, art_date, medium, width, height, institution, inscriptions, source, categories_list):
    artist = artist.strip()
    title = title.strip()
    
    raw_artist = artist
    if pw.exist(['Creator:'+artist]):
        artist = '{{Creator:'+artist+'}}'
    elif birth and death:
        artist = artist + ' (' + birth + ' - ' + death + ')'
    
    description = ""
    if description_fr:
        description += '\n{{fr|'+description_fr+'}}'
    if description_en:
        description += '\n{{en|'+description_en+'}}'
    
    if '{{'+medium+'}}' in mediums:
        medium = '{{'+medium+'}}'
    
    if institution:
        if institution[0] == '{':
            pass
        elif pw.exist(['Creator:'+institution]):
            institution = '{{Institution:'+institution+'}}'
    
    if death:
        permission = '{{PD-old-auto-1923|deathyear='+death+'}}'
    else:
        permission = '{{PD-old-auto-1923}}'
        
    categories = ""
    if pw.exist(['Category:'+raw_artist]):
        categories += "\n[[Category:"+raw_artist+"]]"
    if categories_list:
        categories_list = categories_list.split(';')
        for category in categories_list:
            categories += "\n[[Category:"+category+"]]"
        for category in global_categories:
            categories += "\n[[Category:"+category+"]]"
    
    text = template.replace('$artist', artist).replace('$title', title).replace('$description', description).replace('$object_type', object_type).replace('$date', art_date).replace('$medium', medium).replace('$width', width).replace('$height', height).replace('$institution', institution).replace('$inscriptions', inscriptions).replace('$permission', permission).replace('$source', source).replace('$categories', categories)
    
    extension = file_name.split(".")[-1]
    extension = extension.lower()
    if extension == 'jpeg':
        extension = 'jpg'
    
    title = date.today().strftime("%Y-%m") + " " + raw_artist.decode("utf-8") + " - " + title.decode("utf-8") + "." + extension
    
    pw.upload(title, path+file_name, text)
    print "File '"+title+"' uploaded"
    

    def prompt():
        print "artist:\n> ",;artist = sys.stdin.readline().split("\n")[0]
        print "birth:\n> ",;birth = sys.stdin.readline().split("\n")[0]
        print "death:\n> ",;death = sys.stdin.readline().split("\n")[0]
        print "title:\n> ",;title = sys.stdin.readline().split("\n")[0]
        print "description (en):\n> ",;description_en = sys.stdin.readline().split("\n")[0]
        print "description (fr):\n> ",;description_fr = sys.stdin.readline().split("\n")[0]
        print "object type (e.g. 'painting'):\n> ",;object_type = sys.stdin.readline().split("\n")[0]
        print "date:\n> ",;art_date = sys.stdin.readline().split("\n")[0]
        print "medium (e.g. 'Oil on canvas'):\n> ",;medium = sys.stdin.readline().split("\n")[0]
        print "width:\n> ",;width = sys.stdin.readline().split("\n")[0]
        print "height:\n> ",;height = sys.stdin.readline().split("\n")[0]
        print "institution (e.g. 'Louvre':\n> ",;institution = sys.stdin.readline().split("\n")[0]
        print "inscriptions:\n> ",;inscriptions = sys.stdin.readline().split("\n")[0]
        print "source:\n> ",;source = sys.stdin.readline().split("\n")[0]
        print "categories (separated by a ';'):\n> ",;categories_list = sys.stdin.readline().split("\n")[0]
        return (artist, birth, death, title, description_en, description_fr, object_type, art_date, medium, width, height, institution, inscriptions, source, categories_list)



# Main
def main():
    global path, global_categories
    pw = pywiki.Pywiki("commonswiki-0x010C")
    pw.login()

    path = pwutils.arg_parser("-p", value=True)
    if path[-1] != '/':
        path = path + '/'
    csv_file_path = pwutils.arg_parser("-f", value=True)
    global_categories = pwutils.arg_parser("-c", value=True).encode("utf-8")
    if global_categories:
        global_categories = global_categories.split(';')
    else:
        global_categories = []

    if path and csv_file_path:
        with open(csv_file_path, 'rb') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='&', quotechar='"')
            for row in csv_reader:
                (file_name, artist, birth, death, title, description_en, description_fr, object_type, art_date, medium, width, height, institution, inscriptions, source, categories_list) = row
                if os.path.isfile(path+file_name):
                    uploader(file_name, artist, birth, death, title, description_en, description_fr, object_type, art_date, medium, width, height, institution, inscriptions, source, categories_list)
                else:
                    print "Missing file '"+file_name+"'"
    
    url = pwutils.arg_parser("--url", value=True, required=True)
    path = "./"
    image_response = requests.get(url, stream=True)
    with open('./tmp.jpg', 'wb') as out_file:
        shutil.copyfileobj(image_response.raw, out_file)
    del response
    
    (artist, birth, death, title, description_en, description_fr, object_type, art_date, medium, width, height, institution, inscriptions, source, categories_list) = prompt()
    
    uploader("tmp.jpg", artist, birth, death, title, description_en, description_fr, object_type, art_date, medium, width, height, institution, inscriptions, source, categories_list)
    

main()

