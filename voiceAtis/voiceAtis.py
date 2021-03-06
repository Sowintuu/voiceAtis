#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
#==============================================================================
# voiceAtis - Reads an ATIS from IVAO using voice generation
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
# Version - 0.4.0 - Changlog > README.md
#==============================================================================
# Sample ATIS
# 0 - Aurora
#0    eu17.ts.ivao.aero/EDDM_TWR
#1    Muenchen Tower
#2     Information GOLF  recorded at 2101z
#3    EDDM 112050Z 36002KT CAVOK 13/12 Q1009 NOSIG
#4    ARR RWY 26 L/R / DEP RWY 26L/R / TRL FL70 / TA 5000ft
#5    CONFIRM ATIS INFO GOLF  on initial contact
#
#0    eu17.ts.ivao.aero/EDDH_TWR
#1    Hamburg Tower
#2     Information FOXTROT  recorded at 2103z
#3    EDDH 112050Z 04008KT 010V070 9999 BKN007 15/14 Q1013 BECMG BKN004
#4    ARR RWY 15 / DEP RWY 15 / TRL FL070 / TA 5000ft
#5    RMK DEPARTURE FREQUENCY 122.800
#6    CONFIRM ATIS INFO FOXTROT  on initial contact

#------------------------------------------------------------------------------
# 1 - IvAc 1
#0    eu16.ts.ivao.aero/EDDF_A_GND
#1    Frankfurt Apron information DELTA recorded at 2104z
#2     EDDF 112050Z 07003KT 9999 FEW020 15/13 Q1010 NOSIG 
#3    ARR RWY 07R/07L / DEP RWY 07C/18 / TRL FL060 / TA 5000FT
#4    CONFIRM ATIS INFO DELTA on initial contact
#
#0 eu16.ts.ivao.aero/EDDL_TWR
#1    Dusseldorf Tower information HOTEL recorded at 2104z
#2     EDDL 112050Z 07003KT CAVOK 17/13 Q1010 NOSIG 
#3    ARR RWY 05R / DEP RWY 05R / TRL FL070 / TA 5000FT
#4    Departure Frequency 122.800
#5    CONFIRM ATIS INFO HOTEL on initial contact
#------------------------------------------------------------------------------
# 2 - IvAc 2
#0    eu4.ts.ivao.aero/EGSS_GND
#1    EGSS ARR/DEP ATIS H 2103Z
#2    ARR RWY 04
#3    ARR RWY 04
#4    DEP RWY 04
#5    DEP RWY 04
#6    TA 6000 / TRL 75
#7    METAR EGSS 112050Z AUTO 02009KT 9999 OVC006 13/12 Q1010

#==============================================================================

# Declaraion at the beginning.
print('voiceAtis - Reads an ATIS from IVAO using voice generation')
print('Copyright (C) 2018-2020  Oliver Clemens')
print(' ')
print('This program is free software: you can redistribute it and/or modify it under')
print('the terms of the GNU General Public License as published by the Free Software')
print('Foundation, either version 3 of the License, or (at your option) any later')
print('version.')
print(' ')
print('This program is distributed in the hope that it will be useful, but WITHOUT')
print('ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS')
print('FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more')
print('details.')
print(' ')
print('You should have received a copy of the GNU General Public License along with')
print('this program. If not, see <https://www.gnu.org/licenses/>.')
print(' ')
print('This software uses ', end = '')

# Import built-ins
import os
import re
import sys
import time
import shutil
import urllib.request
import gzip
from math import floor
import warnings
from datetime import datetime
import wave
import contextlib

# Import pip packages.
import pyuipc
import tts.sapi
from AudioEffect import AudioEffect
from pygame import mixer
from metar.Metar import Metar
from aviationFormula.aviationFormula import gcDistanceNm

# Import own packages.
from VaLogger import VaLogger
from voiceAtisUtil import parseVoiceInt, parseVoiceString, CHAR_TABLE, RWY_TABLE

# Set encoding type.
ENCODING_TYPE = 'utf-8'


## Main Class of VoiceAtis.
# Run constructor to run the program.
class VoiceAtis(object):
    
    STATION_SUFFIXES_DEP = ['DEL','GND','TWR','DEP','APP']
    STATION_SUFFIXES_ARR = ['APP','TWR','GND','DEL','DEP']
    
    SPEECH_RATE = 150
    
    SLEEP_TIME = 3 # s
    
    RADIO_RANGE = 180 # nm
    
    OFFSETS = [(0x034E,'H'),    # com1freq
               (0x3118,'H'),    # com2freq
               (0x3122,'b'),    # radioActive
               (0x0560,'l'),    # ac Latitude
               (0x0568,'l'),    # ac Longitude
               (0x0350,'H'),    # nav1freq
               (0x0352,'H'),    # nav2freq
               (0x0366,'b'),    # onGroundFlag
              ]
    # Add agl, (ground speed).
    
    WHAZZUP_URL = 'http://api.ivao.aero/getdata/whazzup/whazzup.txt.gz'
    WHAZZUP_METAR_URL = 'http://wx.ivao.aero/metar.php'
    
    OUR_AIRPORTS_URL = 'http://ourairports.com/data/'
    
    
    ## Setup the VoiceAtis object.
    # Inits logger.
    # Downloads airport data.
    def __init__(self,**optional):
        #TODO: Create GUI.
        #TODO: Split 4000 to 4 1000 -> four thousand
        #TODO: Do not recreate voice string, if nothing changed (performance)
        
        # Print newline for spacing.
        print(' ')
        
        # Process optional arguments.
        self.logLvl = optional.get('LogLevel','debug')
        
        # Get file path.
        self.rootDir = os.path.dirname(os.path.abspath(__file__))
        
        # Init logging.
        self.logger = VaLogger(os.path.join(self.rootDir,'logs'))
        self.logger.setLevel(ConcoleLevel=self.logLvl)
        
        # First log message.
        self.logger.info('voiceAtis started')
        
        # Read ini.
        self.readIni()
        
        # Read file with airport frequencies and coordinates.
        self.getAirportData()
        
        # Init tts engine
        self.engine = tts.sapi.Sapi()
        self.engine.set_voice("Zira")   #TODO: handle not available speech engine
        
        # Init pygame.mixer (playing sound files).
        mixer.init()
        
        # Init time of last whazzup download 100 min before call.
        self.lastWhazzupDownload = time.time()-6000
        
    ## Establishs pyuipc connection.
    # Return 'True' on success.
    # Return 'False' on fail.
    def connectPyuipc(self):
        try:
            self.pyuipcConnection = pyuipc.open(0)
            self.pyuipcOffsets = pyuipc.prepare_data(self.OFFSETS)
            self.logger.info('FSUIPC connection established.')
            return True
        except NameError:
            self.pyuipcConnection = None
            self.logger.warning('Error using PYUIPC.')
            return False
        except:
            self.logger.warning('FSUIPC: No simulator detected. Start you simulator first!')
            return False
    
    
    ## Runs an infinite loop.
    # For first implementation without GUI.
    def runLoop(self):
        # Establish pyuipc connection
        result = False
        adminMessageSent = False
        while not result:
            result = self.connectPyuipc()
            if not result:
                self.logger.info('Retrying in 20 seconds.')
                if not adminMessageSent:
                    self.logger.warning('If you run your simulator as admin, also run voiceAtis as admin!')
                    adminMessageSent = True
                time.sleep(20)
        
        # Infinite loop.
        try:
            while True:
                timeSleep = self.loopRun()
                time.sleep(timeSleep)
                
        except KeyboardInterrupt:
            # Actions at Keyboard Interrupt.
            self.logger.info('Loop interrupted by user.')
            self.pyuipc.close()
            
    
    ## One cyle of a loop.
    # Returns the requested sleep time.
    def loopRun(self):
        
        # Get sim data.
        self.getPyuipcData()
        
        # Get best suitable Airport.
        self.getAirport()
        
        # Handle if no airport found.
        if self.airport is None:
            self.logger.info('No airport found, sleeping for {} seconds...'.format(self.SLEEP_TIME))
            return self.SLEEP_TIME
        else:
            self.logger.info('Airport: {}.'.format(self.airport))
        
        # Get whazzup file
        self.getWhazzupText()
        
        # Read whazzup text and get a station.
        self.parseWhazzupText()
        
        # Check if station online.
        if self.atisRaw is not None:
            self.logger.info('Station found, decoding Atis.')
        else:
            # Actions, if no station online.
            self.logger.info('No station online, using metar only.')
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.metar = Metar(self.getAirportMetar(),strict=False)
            
            self.parseVoiceMetar()
            
            # Time
            hours = parseVoiceInt('{:02d}'.format(self.metar._hour))
            minutes = parseVoiceInt('{:02d}'.format(self.metar._min))
            
            # Parse atis voice with metar only.
            self.atisVoice = '{} weather report time {} {}, {}.'.format(self.airportInfos[self.airport][3],hours,minutes,self.metarVoice)
            
            # Read the metar.
            self.readVoice()
            
            return self.SLEEP_TIME
        
        # Parse ATIS.
        # Information.
        self.getInfoIdentifier()
        self.parseVoiceInformation()
        
        # Metar.
        if self.clientType == 0:
            self.parseMetar(self.atisRaw[3].strip())
        if self.clientType == 1:
            self.parseMetar(self.atisRaw[2].strip())
        else:
            for ar in self.atisRaw:
                if ar.startswith('METAR'):
                    self.parseMetar(ar.replace('METAR ','').strip())
                    break
        
        self.parseVoiceMetar()
        
        # Runways / TRL / TA
        self.parseRawRwy()
        self.parseVoiceRwy()
        
        # comment.
        self.parseVoiceComment()
        
        # Compose complete atis voice string.
        self.atisVoice = '{} {} {} {} Information {}, out,'.format(self.informationVoice,self.rwyVoice,self.commentVoice,self.metarVoice,self.informationIdentifier)
        
        # Read the string.
        self.readVoice()
        
        # After successful reading.
        return 0
    
    ## Downloads and reads the whazzup from IVAO 
    def getWhazzupText(self):
        # Check if last download was more than 5 min ago.
        if time.time() - self.lastWhazzupDownload < 300:
            self.logger.info('Last ATIS data download was less than 5 min ago -> no update.')
            return
        
        # Get file from api.
        self.logger.info('Downloading new ATIS data.')
        with urllib.request.urlopen(self.WHAZZUP_URL) as response, open('whazzup.txt.gz', 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        self.lastWhazzupDownload = time.time()

        # Unzip file.
        with gzip.open('whazzup.txt.gz', 'rb') as f:
            self.whazzupText = f.read().decode("ISO-8859-1")
        
        # Remove the source file.
        os.remove('whazzup.txt.gz')
    
    
    ## Reads a whazzup file on disk.
    # For debug purposes.
    def getWhazzupTextDebug(self):
        with open(self.WHAZZUP_TEXT_DEBUG) as whazzupFile:
            self.whazzupText = whazzupFile.read()
        pass
    
    
    ## Find a station of the airport and read the ATIS string.
    def parseWhazzupText(self):
        # Find an open station
        if self.onGround:
            stationSuffixes = self.STATION_SUFFIXES_DEP
        else:
            stationSuffixes = self.STATION_SUFFIXES_ARR
        
        for st in stationSuffixes:
            matchObj = re.search('{}\w*?_{}'.format(self.airport,st),self.whazzupText)
            
            if matchObj is not None:
                break
        
        if matchObj is not None:
            # Extract ATIS.
            lineStart = matchObj.start()
            lineEnd = self.whazzupText.find('\n',matchObj.start())
            
            # Split station text.
            stationInfo = self.whazzupText[lineStart:lineEnd].split(':')
            
            # Get client info (different ATIS text format)
            if stationInfo[38] == 'IvAc':
                self.clientType = int(stationInfo[39][0])
            else:
                self.clientType = 0
                
            # Store raw ATIS text.
            self.atisTextRaw = stationInfo[35]
            self.atisRaw = stationInfo[35].split('^�')
            
            if len(self.atisRaw) < 4:
                self.atisRaw = None
                self.logger.warning('ATIS text is erroneous. Using METAR.')
            
        else:
            self.atisRaw = None
    
    
    def parseMetar(self,metarString):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.metar = Metar(metarString,strict=False)
    
    
    ## Parse runway and transition data.
    # Get active runways for arrival and departure.
    # Get transistion level and altitude.
    def parseRawRwy(self):
        self.rwyInformation = [None,None,None,None]
        # IvAc 1 or Aurora.
        if self.clientType != 2:
            # Select line of rwy information.
            if self.clientType == 0:
                runwayStr = self.atisRaw[4]
            else:
                runwayStr = self.atisRaw[3]
            
            # Get Position of information parts. ARR is always at 0.
            posDep = runwayStr.find('DEP')
            posTrl = runwayStr.find('TRL')
            posTa = runwayStr.find('TA')
            
            # Get strings to parse.
            runwayParts = {'ARR' : runwayStr[7:posDep-2].strip(),
                           'DEP' : runwayStr[posDep+7:posTrl-2].strip(),
                           'TRL' : runwayStr[posTrl+3:posTa-2].strip(),
                           'TA'  : runwayStr[posTa+2:].strip()}
            
            # Parse ARR and DEP.
            for kId, k in enumerate(['ARR','DEP']):
                runways = []
                partStr = runwayParts[k]
                
                # Find rwy numbers.
                rwyPos = []
                for rw in re.finditer('\d{2}',partStr):
                    rwyPos.append(rw.start())
                rwyPos.append(len(partStr))
                
                rwCount = 0
                while rwCount < len(rwyPos)-1:
                    dirStr = partStr[rwyPos[rwCount]:rwyPos[rwCount+1]]
                    runwayNum = partStr[rwyPos[rwCount]:rwyPos[rwCount]+2]
                    contDir = False
                    for m in ['R','C','L']:
                        if m in dirStr:
                            runways.append(runwayNum + m)
                            contDir = True
                    if not contDir:
                        runways.append(runwayNum)
                    
                    rwCount += 1
                
                # Add runways to list.
                self.rwyInformation[kId] = runways
            
            # Parse TRL and TA.
            self.rwyInformation[3] = runwayParts['TRL'][2:]
            self.rwyInformation[2] = runwayParts['TA'][:-2] #TODO: Check unit meter (russia, china).
        
        # Ivac 2
        else:
            for ar in self.atisRaw:
                if ar.startswith('TA'):
                    trlTaSplit = ar.split(' / ')
                    self.rwyInformation[3] = trlTaSplit[0].replace('TA ','')
                    self.rwyInformation[2] = trlTaSplit[1].replace('TRL','')
                    
                elif ar.startswith('ARR'):
                    curRwy = [ar[8:10],None,None,None]
                    if 'L' in ar[8:]:
                        curRwy[1] = 'Left'
                    if 'C' in ar[8:]:
                        curRwy[2] = 'Center'
                    if 'R' in ar[8:]:
                        curRwy[3] = 'Right'
                    if self.rwyInformation[0] is None:
                        self.rwyInformation[0] = [curRwy]
                    else:
                        self.rwyInformation[0].append(curRwy)
                        
                elif ar.startswith('DEP'):
                    curRwy = [ar[8:10],None,None,None]
                    if 'L' in ar[8:]:
                        curRwy[1] = 'Left'
                    if 'C' in ar[8:]:
                        curRwy[2] = 'Center'
                    if 'R' in ar[8:]:
                        curRwy[3] = 'Right'
                    if self.rwyInformation[1] is None:
                        self.rwyInformation[1] = [curRwy]
                    else:
                        self.rwyInformation[1].append(curRwy)
    
    
    ## Generate a string of the metar for voice generation.
    def parseVoiceMetar(self):
        self.metarVoice = ''
        
        # Wind
        if self.metar.wind_speed._value != 0:
            if self.metar.wind_dir is not None:
                self.metarVoice = '{}, wind {}, {}'.format(self.metarVoice,parseVoiceString(self.metar.wind_dir.string()),parseVoiceString(self.metar.wind_speed.string()))
            else:
                self.metarVoice = '{}, wind variable, {}'.format(self.metarVoice,parseVoiceString(self.metar.wind_speed.string()))
        else:
            self.metarVoice = '{}, wind calm'.format(self.metarVoice,self.metar.wind_dir.string(),self.metar.wind_speed.string())
        
        if self.metar.wind_gust is not None:
            self.metarVoice = '{}, maximum {}'.format(self.metarVoice,parseVoiceString(self.metar.wind_gust.string()))
        
        if self.metar.wind_dir_from is not None:
            self.metarVoice = '{}, variable between {} and {}'.format(self.metarVoice,parseVoiceString(self.metar.wind_dir_from.string()),parseVoiceString(self.metar.wind_dir_to.string()))
            
        
        # Visibility.
        #TODO: implement directions
        self.metarVoice = '{}, visibility {}'.format(self.metarVoice,self.metar.vis.string())
        
        # runway visual range
        rvr = self.metar.runway_visual_range().replace(';', ',')
        if rvr:
            rvrNew = ''
            lastEnd = 0
            rvrPattern = re.compile('[0123]\d[LCR]?(?=,)')
            for ma in rvrPattern.finditer(rvr):
                rwyRaw = rvr[ma.start():ma.end()]
                rwyStr = parseVoiceInt(rwyRaw[0:2])
                if len(rwyRaw) > 2:
                    if rwyRaw[2] == 'L':
                        rwyStr = '{} left'.format(rwyStr)
                    elif rwyRaw[2] == 'C':
                        rwyStr = '{} center'.format(rwyStr)
                    elif rwyRaw[2] == 'R':
                        rwyStr = '{} right'.format(rwyStr)
                rvrNew = '{}{}{}'.format(rvrNew,rvr[lastEnd:ma.start()],rwyStr)
                lastEnd = ma.end()
            
            rvrNew = '{}{}'.format(rvrNew,rvr[lastEnd:])
            
            self.metarVoice = '{}, visual range {}'.format(self.metarVoice,rvrNew)
        
        # weather phenomena
        if self.metar.weather:
            self.metarVoice = '{}, {}'.format(self.metarVoice,self.metar.present_weather().replace(';',','))
        
        # clouds
        if self.metar.sky:
            self.metarVoice = '{}, {}'.format(self.metarVoice,self.metar.sky_conditions(',').replace(',',', ').replace('a few','few'))
        elif 'CAVOK' in self.metar.code:
            self.metarVoice = '{}, clouds and visibility ok'.format(self.metarVoice)
        
        
        # runway condition
        #TODO: Implement runway conditions
        # Not implemented in python-metar
        
        # temperature
        tempValue = parseVoiceInt(str(int(self.metar.temp._value)))
        if self.metar.temp._units == 'C':
            tempUnit = 'degree Celsius'
        else:
            tempUnit = 'degree Fahrenheit'
            
        self.metarVoice = '{}, temperature {} {}'.format(self.metarVoice,tempValue,tempUnit)
        
        # dew point
        dewptValue = parseVoiceInt(str(int(self.metar.dewpt._value)))
        if self.metar.dewpt._units == 'C':
            dewptUnit = 'degree Celsius'
        else:
            dewptUnit = 'degree Fahrenheit'
            
        self.metarVoice = '{}, dew point {} {}'.format(self.metarVoice,dewptValue,dewptUnit)
        
        # QNH
        if self.metar.press._units == 'MB':
            pressValue = parseVoiceInt(str(int(self.metar.press._value)))
            self.metarVoice = '{}, Q N H {} hectopascal'.format(self.metarVoice,pressValue)
        else:
            self.metarVoice = '{}, Altimeter {}'.format(self.metarVoice,parseVoiceString(self.metar.press.string()))
        
        #TODO: implement trend
        
        self.metarVoice = '{},'.format(self.metarVoice)
    
    ## Generate a string of the information identifier for voice generation.
    def parseVoiceInformation(self):
        # Aurora or IvAc 1
        if self.clientType != 2:
            if self.clientType == 0:
                infoLine = self.atisRaw[1] + self.atisRaw [2]
            else:
                infoLine = self.atisRaw[1]
            
            # Get report time.
            timeMatch = re.search(r'\d{4}z',infoLine)
            startInd = timeMatch.start()
            endInd = timeMatch.end()- 1
            timeStr = parseVoiceInt(infoLine[startInd:endInd])
            
            # Get Airport name.
            wordsList = infoLine.lower().split(' ')
            informationIndex = wordsList.index('information')
            airportName = ' '.join(wordsList[:informationIndex-1])
            
            self.informationVoice = '{} information {}, met report time {}.'.format(airportName,self.informationIdentifier,timeStr)
        
        # IvAc 2
        else:
            information = self.atisRaw[1].split(' ')
            airport = information[0]
            airport = self.airportInfos[airport][3]
            time = parseVoiceInt(information[4][0:4])
            
            self.informationVoice = '{} Information {} recorded at {}.'.format(airport,self.informationIdentifier,time)
    
    
    ## Generate a string of the runway information for voice generation.
    def parseVoiceRwy(self):
        self.rwyVoice = ''
        arrDep = ['Arrival','Departure']
        
        # ARR, DEP
        for k in [0,1]:
            if self.rwyInformation[k] is not None:
                self.rwyVoice = '{}{} runway '.format(self.rwyVoice,arrDep[k])
                for m in self.rwyInformation[k]:
                    if len(m) > 2:
                        self.rwyVoice = '{}{} {}, and '.format(self.rwyVoice,parseVoiceInt(m[0:2]),RWY_TABLE[m[2]])
                    else:
                        self.rwyVoice = '{}{}, and '.format(self.rwyVoice,parseVoiceInt(m))
                
                self.rwyVoice = self.rwyVoice[:-6] + ', '
        
        # TRL
        if self.rwyInformation[2] is not None:
            self.rwyVoice = '{}Transition altitude {} feet, '.format(self.rwyVoice,self.rwyInformation[2])
        
        # TA
        if self.rwyInformation[3] is not None:
            self.rwyVoice = '{}Transition level {},'.format(self.rwyVoice,parseVoiceInt(self.rwyInformation[3]))
            
    ## Generate a string of ATIS comment for voice generation.
    def parseVoiceComment(self):
        if self.clientType == 0 and len(self.atisRaw) > 6:
            self.commentVoice = '{},'.format(parseVoiceString(self.atisRaw[5].replace('RMK ','')))
        elif self.clientType == 1 and len(self.atisRaw) > 5:
            self.commentVoice = '{},'.format(parseVoiceString(self.atisRaw[4]))
        else:
            self.commentVoice = ''
    
    
    def readVoice(self):
        #TODO: Start first reading at random place in string.
    
        # Set properties currently reading
        self.currentlyReading = self.airport
        
        # Log ATIS text.
        try:
            self.logger.info('ATIS Text is: {}'.format(self.atisVoice))
        except:
            self.logger.info('ATIS Text cannot be displayed: unexpected characters.')
        
        # Create tmp folder.
        if not os.path.isdir('tmp'):
            os.mkdir('tmp')
        
        # Get tmp name.
        fileCount = 0
        fileTmp = 'tmp/atis_0.wav'
        while os.path.isfile(fileTmp):
            fileCount += 1
            fileTmp = 'tmp/atis_{}.wav'.format(fileCount)
        
        # Create tmp wav file.
        self.logger.info('Generating ATIS sound.')
        self.engine.create_recording(fileTmp, self.atisVoice)
        
        # Apply radio effect.
        self.logger.info('Generating radio effects.')
        AudioEffect.radio(fileTmp, fileTmp)
        
        # Get wav duration.
        with contextlib.closing(wave.open(fileTmp,'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            self.wavDuration = frames / float(rate)
        
        # Start reading.
        mixer.music.load(fileTmp)
        self.logger.info('Start reading.')
        mixer.music.play()
        
        while mixer.music.get_busy():
            self.onWord()
            tmpfiles = os.listdir('tmp')
            for k in tmpfiles:
                fullPath = 'tmp/' + k
                if fullPath != fileTmp:
                    try:
                        os.remove(fullPath)
                    except:
                        pass
            time.sleep(0.5)
        
        self.logger.info('Reading finished.')
        
    
    ## Callback for stop of reading.
    # Stops reading if frequency change/com deactivation/out of range.
    def onWord(self):
        self.getPyuipcData()
        self.getAirport()
        
        if self.airport != self.currentlyReading:
            mixer.music.stop()
            self.currentlyReading = None
            self.logger.info('Reading interrupted.')
    
    
    ## Reads current frequency and COM status.
    def getPyuipcData(self):
        
        results = pyuipc.read(self.pyuipcOffsets)
        
        # frequency
        #TODO: Check 8.33 kHz. (125.205 = 125.200)
        hexCode = hex(results[0])[2:]
        self.com1frequency = float('1{}.{}'.format(hexCode[0:2],hexCode[2:]))
        hexCode = hex(results[1])[2:]
        self.com2frequency = float('1{}.{}'.format(hexCode[0:2],hexCode[2:]))
        hexCode = hex(results[5])[2:]
        self.nav1frequency = float('1{}.{}'.format(hexCode[0:2],hexCode[2:]))
        hexCode = hex(results[6])[2:]
        self.nav2frequency = float('1{}.{}'.format(hexCode[0:2],hexCode[2:]))
        
        # radio active
        #TODO: Test accuracy of this data (with various planes and sims)
        radioActiveBits = list(map(int, '{0:08b}'.format(results[2])))
        if radioActiveBits[2]:
            self.com1active = True
            self.com2active = True
        elif radioActiveBits[0]:
            self.com1active = True
            self.com2active = False
        elif radioActiveBits[1]:
            self.com1active = False
            self.com2active = True
        else:
            self.com1active = False
            self.com2active = False
        
        if radioActiveBits[3]:
            self.nav1active = True
        else:
            self.nav1active = False
        if radioActiveBits[4]:
            self.nav2active = True
        else:
            self.nav2active = False
        
        # lat lon
        self.lat = results[3] * (90.0/(10001750.0 * 65536.0 * 65536.0))
        self.lon = results[4] * (360.0/(65536.0 * 65536.0 * 65536.0 * 65536.0))
        
        # on ground.
        self.onGround = results[7]
            
        
        # Logging.
        if self.com1active:
            com1activeStr = 'active'
        else:
            com1activeStr = 'inactive'
        if self.com2active:
            com2activeStr = 'active'
        else:
            com2activeStr = 'inactive'
        if self.nav1active:
            nav1activeStr = 'active'
        else:
            nav1activeStr = 'inactive'
        if self.nav2active:
            nav2activeStr = 'active'
        else:
            nav2activeStr = 'inactive'
            
        if mixer.music.get_busy():
            self.logger.debug('COM 1: {} ({}), COM 2: {} ({})'.format(self.com1frequency,com1activeStr,self.com2frequency,com2activeStr))
            self.logger.debug('NAV 1: {} ({}), NAV 2: {} ({})'.format(self.nav1frequency,nav1activeStr,self.nav2frequency,nav2activeStr))
        else:
            self.logger.info('COM 1: {} ({}), COM 2: {} ({})'.format(self.com1frequency,com1activeStr,self.com2frequency,com2activeStr))
            self.logger.info('NAV 1: {} ({}), NAV 2: {} ({})'.format(self.nav1frequency,nav1activeStr,self.nav2frequency,nav2activeStr))
    
    ## Determine if there is an airport aplicable for ATIS reading.
    def getAirport(self):
        self.airport = None
        frequencies = []
        if self.com1active:
            frequencies.append(self.com1frequency)
        if self.com2active:
            frequencies.append(self.com2frequency)
        if self.nav1active:
            frequencies.append(self.nav1frequency)
        if self.nav2active:
            frequencies.append(self.nav2frequency)
        
        if frequencies:
            distanceMin = self.RADIO_RANGE + 1
            for ap in self.airportInfos:
                distance = gcDistanceNm(self.lat, self.lon, self.airportInfos[ap][1], self.airportInfos[ap][2])
                if distance < self.RADIO_RANGE and distance < distanceMin:
                    for fr in self.airportInfos[ap][0]:
                        if (floor(fr*100)/100) in frequencies:
                            distanceMin = distance
                            self.airport = ap
                            break
    
    
    ## Read data of airports from a given file.
    def getAirportDataFile(self,apFile):
        # Check if file exists.
        if not os.path.isfile(apFile):
            self.logger.warning('No such file: {}'.format(apFile))
            return
        
        # Read the file.
        with open(apFile, encoding="utf8") as aptInfoFile:
            for li in aptInfoFile:
                lineSplit = re.split('[,;]',li)
                if not li.startswith('#') and len(lineSplit) == 5:
                    freqStr = lineSplit[1].split('^')
                    freqList = []
                    for fr in freqStr:
                        freqList.append(float(fr))
                    self.airportInfos[lineSplit[0].strip()] = (freqList,float(lineSplit[2]),float(lineSplit[3]),lineSplit[4].replace('\n',''))
    
    ## Read data of airports from http://ourairports.com.
    def getAirportDataWeb(self):
        
        airportFreqs = {}
        
        # Read the file with frequency.
        response = urllib.request.urlopen(self.OUR_AIRPORTS_URL + 'airport-frequencies.csv')
        data = response.read()
        apFreqText = data.decode(ENCODING_TYPE)
        
        # Get the frequencies from the file.
        for li in apFreqText.split('\n'):
            lineSplit = li.split(',')
            if len(lineSplit) > 3 and lineSplit[3] == '"ATIS"':
                airportCode = lineSplit[2].replace('"','')
                if airportCode not in airportFreqs:
                    airportFreqs[airportCode] = [float(lineSplit[-1].replace('\n',''))]
                else:
                    airportFreqs[airportCode].append(float(lineSplit[-1].replace('\n','')))
        
        # Read the file with other aiport data.
        response = urllib.request.urlopen(self.OUR_AIRPORTS_URL + 'airports.csv')
        data = response.read()
        apText = data.decode(ENCODING_TYPE)
        
        # Add frequency and write them to self. airportInfos.
        for li in apText.split('\n'):
            lineSplit = re.split((",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)"),li)
            
            if len(lineSplit) > 1:
                apCode = lineSplit[1].replace('"','')
                if apCode in airportFreqs and len(apCode) <= 4:
                    self.airportInfos[apCode] = [airportFreqs[apCode],float(lineSplit[4]),float(lineSplit[5]),lineSplit[3].replace('"','')]
        
        
    ## Reads airportData from two sources.
    def getAirportData(self):
        self.airportInfos = {}
        
        # Check update date of airport data.
        # Airport data only have to be downloaded once a day.
        if 'lastAirportDownload' in self.iniOptions:
            if self.iniOptions['lastAirportDownload'] == datetime.today().strftime('%d%m%y'):
                self.logger.info('Airport data up to date.')
                self.getAirportDataFile(os.path.join(self.rootDir,'supportFiles','airports.info'))
                return
        
        try:
            # Try to read airport data from web.
            self.logger.info('Downloading airport data. This may take some time.')
            self.getAirportDataWeb()
            self.getAirportDataFile(os.path.join(self.rootDir,'supportFiles','airports_add.info'))
            collectedFromWeb = True
            self.logger.info('Finished downloading airport data.')
            
        except:
            # If this fails, use the airports from airports.info.
            self.logger.warning('Unable to get airport data from web. Using airports.info. Error: {}'.format(sys.exc_info()[0]))
            self.airportInfos = {}
            collectedFromWeb = False
            try:
                self.getAirportDataFile(os.path.join(self.rootDir,'supportFiles','airports.info'))
            except:
                self.logger.error('Unable to read airport data from airports.info!')
        
        # Sort airportInfos and write them to a file for future use if collected from web.
        if collectedFromWeb:
            apInfoPath = os.path.join(self.rootDir,'supportFiles','airports.info')
            apList = list(self.airportInfos.keys())
            apList.sort()
            with open(apInfoPath,'w',encoding=ENCODING_TYPE) as apDataFile:
                for ap in apList:
                    freqStr = ''
                    for fr in self.airportInfos[ap][0]:
                        freqStr = '{}{}^'.format(freqStr,fr)
                    apDataFile.write('{:>4}; {:20}; {:11.6f}; {:11.6f}; {}\n'.format(ap,freqStr.strip('^'),self.airportInfos[ap][1],self.airportInfos[ap][2],self.airportInfos[ap][3]))
            
            self.iniOptions['lastAirportDownload'] = datetime.today().strftime('%d%m%y')
            self.writeIni()
    
    ## Determines the info identifier of the loaded ATIS.
    def getInfoIdentifier(self):
        if self.clientType == 1:
            informationPos = re.search('information ',self.atisRaw[1].lower()).end()
            informationSplit = self.atisRaw[1][informationPos:].split(' ')
            self.informationIdentifier = informationSplit[0]
        elif self.clientType == 0:
            informationPos = re.search('information ',self.atisRaw[2].lower()).end()
            informationSplit = self.atisRaw[2][informationPos:].split(' ')
            self.informationIdentifier = informationSplit[0]
        else:
            self.informationIdentifier = CHAR_TABLE[re.findall(r'(?<=ATIS )[A-Z](?= \d{4})',self.atisRaw[1])[0]]
        
    
    ## Retrieves the metar of an airport independet of an ATIS.
    def getAirportMetar(self):
        
        # Get the text of the file.
        response = urllib.request.urlopen(self.WHAZZUP_METAR_URL)
        data = response.read()
        metarText = data.decode(ENCODING_TYPE)
        
        # Find the metar of the current airport.
        metarStart = metarText.find(self.airport)
        metarEnd = metarText.find('\n',metarStart)
        
        return metarText[metarStart:metarEnd]
    
    
    ## Get information from voiceAtis.ini file.
    # File is created if it doesn't exist.
    def readIni(self):
        self.iniOptions = {}
        if os.path.isfile('voiceAtis.ini'):
            with open('voiceAtis.ini') as iniFile:
                iniContent = iniFile.readlines()
            for k in iniContent:
                line = k.split('=')
                self.iniOptions[line[0].strip()] = line[1].strip()
        else:
            self.writeIni()
    
    
    ## Write information to voiceAtis.ini
    def writeIni(self):
        with open('voiceAtis.ini','w') as iniFile:
            for k in self.iniOptions:
                iniFile.write('{}={}\n'.format(k,self.iniOptions[k]))
    
    
if __name__ == '__main__':
    voiceAtis = VoiceAtis()
#     voiceAtis = VoiceAtis(Debug=True)
    voiceAtis.runLoop()
    pass
