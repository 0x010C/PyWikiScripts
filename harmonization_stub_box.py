#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 12 May 2016
#License: GNU GPL v3

import pywiki
import re


harmonization_table = [
	[u"Arabie Saoudite", u"Arabie saoudite"],
	[u"basketball", u"basket-ball"],
	[u"commune d'Algérie", u"commune algérienne"],
	[u"commune de France", u"commune française"],
	[u"Empire Ottoman", u"Empire ottoman"],
	[u"homme politique français", u"personnalité politique française"],
	[u"Jeux Olympiques", u"Jeux olympiques"],
	[u"math", u"mathématiques"],
	[u"Meuble", u"ameublement"],
	[u"personnalité du Brésil", u"personnalité brésilienne"],
	[u"personnalité du Niger", u"personnalité nigérienne"],
	[u"personnalité politique France", u"personnalité politique française"],
	[u"personnalité RDC", u"personnalité congolaise (RDC)"],
	[u"politicien Canada", u"personnalité politique canadienne"],
	[u"politicien Manitoba", u"personnalité politique manitobaine"],
	[u"politicien Ontario", u"personnalité politique ontarienne"],
	[u"politicien Québec", u"personnalité politique québécoise"],
	[u"politique Tunisie", u"politique tunisienne"],
	[u"RDA", u"Allemagne"],
	[u"République Tchèque", u"République tchèque"],
	[u"Réunion", u"La Réunion"],
	[u"Transports en commun", u"transport en commun"],
]

# Main
def main():
	pw = pywiki.Pywiki("frwiki-NeoBOT")
	pw.login()
	pw.limit = 500
	
	for line in harmonization_table:
		line[0] = re.compile(ur'({{ ?[EÉeé]bauche[^}]*\| ?)'+line[0]+ur'( ?[}|])', re.DOTALL | re.IGNORECASE)
	
	regex = re.compile(ur'{{ ?[EÉeé]bauche')
	
	ti_continue = ""
	i=0
	j=0
	while ti_continue != None:
		(titles, ti_continue) = pw.get_transcluded_pages("Modèle:Ébauche", 0, ti_continue)
		contents = pw.get_content_list(titles)
		
		for content in contents:
			tmp = content[1]
			for line in harmonization_table:
				tmp = line[0].sub(ur"\1"+line[1]+ur"\2", tmp)
			if content[1] != tmp:
				tmp = regex.sub(ur"{{Ébauche", tmp)
				print content[0]
				pw.replace(content[0], tmp, u"Bot : Harmonisation des paramètres du bandeau [[Modèle:Ébauche|Ébauche]]", nocreate=True)
				j += 1
		i += pw.limit
		print "###"+str(i)
	print "Nombre de pages modifiés : " + str(j)
main()

