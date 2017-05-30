#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: SunGyo Kim
# Email: Kimsg1984@gmail.com
# irc.freenode #ubuntu-ko Sungyo

keywords = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'pcx']

def getKeywords():
	wildcard= ['', '', []]
	for k in keywords:
		k1 = k.lower()
		k2 = k.upper()
		k3 = k[0].upper() + k[1:].lower()

		wildcard[0] = ('%s*.%s;*.%s;*.%s;' %(wildcard[0], k1, k2, k3))[:-1]
		wildcard[1] = ('%s|%s|%s|%s|' %(wildcard[1], k1, k2, k3))[:-1]
		wildcard[2].append('.%s' %k1); wildcard[2].append('.%s' %k2); wildcard[2].append('.%s' %k3)
	wildcard[1] = wildcard[1][1:] # remove first '|'
	return wildcard

