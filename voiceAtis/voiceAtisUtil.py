#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
#==============================================================================
# voiceAtisUtil - Helper functions for voiceAtis
# Copyright (C) 2018  Oliver Clemens
# 
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# 
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <https://www.gnu.org/licenses/>.
#==============================================================================

import re

# Char table constant (ICAO alphabet)
CHAR_TABLE = {'A' : 'APLHA',    'B' : 'BRAVO',      'C' : 'CHARLIE',
              'D' : 'DELTA',    'E' : 'ECHO',       'F' : 'FOXTROTT',
              'G' : 'GOLF',     'H' : 'HOTEL',      'I' : 'INDIA',
              'J' : 'JULIETT',  'K' : 'KILO',       'L' : 'LIMA',
              'M' : 'MIKE',     'N' : 'NOVEMBER',   'O' : 'OSCAR',
              'P' : 'PAPA',     'Q' : 'QUEBEC',     'R' : 'ROMEO',
              'S' : 'SIERRA',   'T' : 'TANGO',      'U' : 'UNIFORM',
              'V' : 'VICTOR',   'W' : 'WHISKEY',    'X' : 'XRAY',
              'Y' : 'YANKEE',   'Z' : 'ZULU'}

RWY_TABLE = {'R' : 'right',
             'C' : 'center',
             'L' : 'left'}

## Sperates integer Numbers with whitespace
# Needed for voice generation to be pronounced properly.
# Also replaces - by 'minus'
# Example: -250 > minus 2 5 0
def parseVoiceInt(number):
    if isinstance(number, float):
        number = int(number)
    if isinstance(number, int):
        number = str(number)
    
    numberSep = ''
    for k in number:
        if k != '-':
            numberSep = '{}{} '.format(numberSep,k)
        else:
            numberSep = '{}minus '.format(numberSep)
    return numberSep.strip()

## Sperates decimal Numbers with whitespace
# Also replaces . or , by 'decimal'
# Also replaces - by 'minus'
# Example: -118.80 > minus 1 1 8 decimal 8 0
def parseVoiceFloat(number):
    if isinstance(number, float):
        number = str(number)
    
    numberSep = ''
    for k in number:
        if k != '.' and k != ',' and k!= '-':
            numberSep = '{}{} '.format(numberSep,k)
        elif k != '-':
            numberSep = '{}decimal '.format(numberSep)
        else:
            numberSep = '{}minus '.format(numberSep)
    return numberSep.strip()

## Search a string for numbers and seperate with whitespaces.
# Using parseVoiceInt() and parseVoiceFloat().
def parseVoiceString(string):
    pattern = re.compile('\d+[,.]\d+')
    match = pattern.search(string)
    while match is not None:
        replaceStr = parseVoiceFloat(string[match.start():match.end()])
        string = '{}{}{}'.format(string[0:match.start()],replaceStr,string[match.end():])
        match = pattern.search(string)
        
    pattern = re.compile('\d\d+')
    match = pattern.search(string)
    while match is not None:
        replaceStr = parseVoiceInt(string[match.start():match.end()])
        string = '{}{}{}'.format(string[0:match.start()],replaceStr,string[match.end():])
        match = pattern.search(string)
        
    return string

## Splits a string at each char and replaces them with ICAO-alphabet.
def parseVoiceChars(string):
        
    stringSep = ''
    for k in string:
        stringSep = '{}{} '.format(stringSep,CHAR_TABLE[k])
    
    return stringSep.strip()