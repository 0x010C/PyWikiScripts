#!/usr/bin/python
# -*- coding: utf-8  -*-

#PROGRAMME :
#	cinema.py
#DEVELOPER :
#	Antoine "0x010C" Lamielle <antoine.lamielle@0x010C.fr>
#PROJECT START DATE :
#	March, 21th 2015
#LICENCE :
#	This program is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; either version 3 of the License, or
#	(at your option) any later version.
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#	GNU General Public License for more details.
#	You should have received a copy of the GNU General Public License along
#	with this program; if not, write to the Free Software Foundation, Inc.,
#	51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import pywikibot
from pywikibot import pagegenerators
from pywikibot.data import api
import re
import sys


site = pywikibot.getSite()
if not site.logged_in():
	site.login()


pdd = pywikibot.Page(site, u"User talk:RobokoBot")
pddD = pywikibot.Page(site, u"User talk:Thibaut120094")
rpdd = re.compile(ur"^\{\{\/Stop\}\}$")
def coupe_circuit_pdd():
	pdd.get()
	if not rpdd.search(pdd.text):
		print u"Arrêt du bot.\n********************\n"
		print pdd.text
		pddD.get()
		pddD.text = pddD.text+u"\n== Un utilisateur a demandé l'arrêt de RobokoBot ==\n*[[Discussion utilisateur:RobokoBot]]\n*[[Spécial:Contributions/RobokoBot]]"
		pddD.save(u"Arrêt de RobokoBot")
		sys.exit()


m1 = pywikibot.Page(site, u"Modèle:Infobox Cinéma (film)")
m2 = pywikibot.Page(site, u"Modèle:Titre en italique")

r1 = re.compile(ur"\{\{[tT]itre en italique\|[^\}]*")
r2 = re.compile(ur"\{\{[tT]itre en italique\|([^\}]*)")
r3 = re.compile(ur"\{\{[iI]nfobox Cinéma \(film\)(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{[^\}]*\}\})*\}\})*\}\})*langue du titre *= *[a-zA-Z]+")
r4 = re.compile(ur"\{\{[iI]nfobox Cinéma \(film\)(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{[^\}]*\}\})*\}\})*\}\})*langue du titre *=")
r5 = re.compile(ur"(\{\{[iI]nfobox Cinéma \(film\)(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{[^\}]*\}\})*\}\})*\}\})*langue du titre *=)")
r6 = re.compile(ur"\{\{[iI]nfobox Cinéma \(film\)(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{[^\}]*\}\})*\}\})*\}\})*titre *=")
r7 = re.compile(ur"(\{\{[iI]nfobox Cinéma \(film\)[^\}]*titre *=(?:[^\|\n\}\{]|\{\{(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{[^\}]*\}\})*\}\})*\}\})*)")
r8 = re.compile(ur"(\{\{[iI]nfobox Cinéma \(film\))")
r9 = re.compile(ur"(\{\{[tT]itre en italique\|[^\}]*\}\} *\n)")

i=0
j=0

exceptions = []
exceptions.append(u"Modèle:Infobox Cinéma (film)")

generator1 = pagegenerators.ReferringPageGenerator(m1, onlyTemplateInclusion=True)
generator2 = pagegenerators.NamespaceFilterPageGenerator(generator1, [0])
generator3 = pagegenerators.RegexFilter.contentfilter(generator1, r1, quantifier='any')

for page in generator3:
	j=j+1
	print str(j)+" : "+page.title().encode("utf8")

	l=r2.findall(page.text)[0]
	# Si l'article fait parti des exceptions à ne pas traiter
	if page.title() in exceptions:
		continue
	# Si la langue est déjà dans l'infobox
	if r3.search(page.text):
		print ""
	# Si le paramètre est présent mais pas renseigné
	elif r4.search(page.text):
		page.text = r5.sub(r'\1 '+l+' ', page.text)
	# Si le paramètre n'est pas présent, mais que le paramètre titre l'est
	elif r6.search(page.text):
		page.text = r7.sub(r'\1\n| langue du titre = '+l+' ', page.text)
	# Si le paramètre n'est pas présent, et titre non plus
	else:
		page.text = r8.sub(r'\1\n| langue du titre = '+l+' ', page.text)
	page.text = r9.sub(r'', page.text)
	page.save(u"Maintenance infobox Cinéma (film)")
	print "########################################################"
	coupe_circuit_pdd()

