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


# Main
def main():
    pw = pywiki.Pywiki("commonswiki-0x010C")
    pw.login()

    path = pwutils.arg_parser("-p", value=True, required=True)
    if path[-1] != '/':
        path = path + '/'
    csv_file_path = pwutils.arg_parser("-f", value=True, required=True)
    global_categories = pwutils.arg_parser("-c", value=True).encode("utf-8")
    if global_categories:
        global_categories = global_categories.split(';')
    else:
        global_categories = []

    with open(csv_file_path, 'rb') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='&', quotechar='"')
        for row in csv_reader:
            (file_name, artist, birth, death, title, description_en, description_fr, object_type, art_date, medium, width, height, institution, inscriptions, source, categories_list) = row
            if os.path.isfile(path+file_name):
                
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
                
                if '{{'+medium+'}}':
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
                
            else:
                print "Missing file '"+file_name+"'"

main()

