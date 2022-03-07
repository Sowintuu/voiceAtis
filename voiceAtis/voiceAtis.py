#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# ==============================================================================
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
# ==============================================================================
# Version - 0.4.0 - Changlog > README.md
# ==============================================================================
# Sample ATIS
# 0 - Aurora
# 0    eu17.ts.ivao.aero/EDDM_TWR
# 1    Muenchen Tower
# 2     Information GOLF  recorded at 2101z
# 3    EDDM 112050Z 36002KT CAVOK 13/12 Q1009 NOSIG
# 4    ARR RWY 26 L/R / DEP RWY 26L/R / TRL FL70 / TA 5000ft
# 5    CONFIRM ATIS INFO GOLF  on initial contact
#
# 0    eu17.ts.ivao.aero/EDDH_TWR
# 1    Hamburg Tower
# 2     Information FOXTROT  recorded at 2103z
# 3    EDDH 112050Z 04008KT 010V070 9999 BKN007 15/14 Q1013 BECMG BKN004
# 4    ARR RWY 15 / DEP RWY 15 / TRL FL070 / TA 5000ft
# 5    RMK DEPARTURE FREQUENCY 122.800
# 6    CONFIRM ATIS INFO FOXTROT  on initial contact

# ------------------------------------------------------------------------------
# 1 - IvAc 1
# 0    eu16.ts.ivao.aero/EDDF_A_GND
# 1    Frankfurt Apron information DELTA recorded at 2104z
# 2     EDDF 112050Z 07003KT 9999 FEW020 15/13 Q1010 NOSIG
# 3    ARR RWY 07R/07L / DEP RWY 07C/18 / TRL FL060 / TA 5000FT
# 4    CONFIRM ATIS INFO DELTA on initial contact
#
# 0 eu16.ts.ivao.aero/EDDL_TWR
# 1    Dusseldorf Tower information HOTEL recorded at 2104z
# 2     EDDL 112050Z 07003KT CAVOK 17/13 Q1010 NOSIG
# 3    ARR RWY 05R / DEP RWY 05R / TRL FL070 / TA 5000FT
# 4    Departure Frequency 122.800
# 5    CONFIRM ATIS INFO HOTEL on initial contact
# ------------------------------------------------------------------------------
# 2 - IvAc 2
# 0    eu4.ts.ivao.aero/EGSS_GND
# 1    EGSS ARR/DEP ATIS H 2103Z
# 2    ARR RWY 04
# 3    ARR RWY 04
# 4    DEP RWY 04
# 5    DEP RWY 04
# 6    TA 6000 / TRL 75
# 7    METAR EGSS 112050Z AUTO 02009KT 9999 OVC006 13/12 Q1010

# ==============================================================================

# Import built-ins
import os
import re
import sys
import time
import json
import urllib.request
from math import floor
import warnings
from datetime import datetime
import wave
import contextlib

# Import pip packages.
import tts.sapi
from fsuipc import FSUIPC, FSUIPCException
from AudioEffect import AudioEffect
from pygame import mixer
from metar.Metar import Metar
from aviationFormula.aviationFormula import gcDistanceNm

# Import own packages.
from VaLogger import VaLogger
from voiceAtisUtil import parseVoiceInt, parseVoiceString, CHAR_TABLE, RWY_TABLE

# Declaration at the beginning.
print(' ')
print('voiceAtis - Reads an ATIS from IVAO using voice generation')
# print('Copyright (C) 2018-2022  Oliver Clemens')
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

# Set encoding type.
ENCODING_TYPE = 'utf-8'


# Main Class of VoiceAtis.
# Run constructor to run the program.
class VoiceAtis(object):
    STATION_SUFFIXES_DEP = ['DEL', 'GND', 'TWR', 'DEP', 'APP']
    STATION_SUFFIXES_ARR = ['APP', 'TWR', 'GND', 'DEL', 'DEP']

    SPEECH_RATE = 150

    SLEEP_TIME = 3  # s

    RADIO_RANGE = 180  # nm

    OFFSETS = [(0x034E, 'H'),  # com1freq
               (0x3118, 'H'),  # com2freq
               (0x3122, 'b'),  # radioActive
               (0x0560, 'l'),  # ac Latitude
               (0x0568, 'l'),  # ac Longitude
               (0x0350, 'H'),  # nav1freq
               (0x0352, 'H'),  # nav2freq
               (0x0366, 'b'),  # onGroundFlag
               ]
    # TODO: Add agl, (ground speed).

    WHAZZUP_URL = 'https://api.ivao.aero/v2/tracker/whazzup'
    WHAZZUP_METAR_URL = 'http://wx.ivao.aero/metar.php'
    WHAZZUP_INTERVAL = 30  # seconds

    NOAA_METAR_URL = 'http://tgftp.nws.noaa.gov/data/observations/metar/stations/<station>.TXT'

    OUR_AIRPORTS_URL = 'http://ourairports.com/data/'

    # Setup the VoiceAtis object.
    # Initialise logger.
    # Downloads airport data.
    def __init__(self, **optional):
        # TODO: Create GUI.
        # TODO: Split 4000 to 4 1000 -> four thousand (more immersive speaking)
        # TODO: Do not recreate voice string, if nothing changed (performance)

        # Print newline for spacing.
        print(' ')

        # Init attributes for later use.
        self.fsuipc_connection = None
        self.fsuipc_offsets = None
        self.metar = None
        self.atis_voice = ''
        self.whazzup_text = ''

        self.com1frequency = None
        self.com2frequency = None
        self.nav1frequency = None
        self.nav2frequency = None
        self.com1active = False
        self.com2active = False
        self.nav1active = False
        self.nav2active = False
        self.lat = 0.0
        self.lon = 0.0
        self.on_ground = True

        self.airport = None
        self.airport_infos = {}
        self.atc = []
        self.atis_raw = None
        self.client_type = ''
        self.information_voice = ''
        self.information_identifier = ''
        self.rwy_information = [None, None, None, None]
        self.metar_voice = ''
        self.rwy_voice = ''
        self.comment_voice = ''
        self.currently_reading = ''
        self.wav_duration = None
        self.ini_options = {}

        # Process optional arguments.
        self.logLvl = optional.get('LogLevel', 'debug')

        # Get file path.
        self.rootDir = os.path.dirname(os.path.abspath(__file__))

        # Init logging.
        self.logger = VaLogger(os.path.join(self.rootDir, 'logs'))
        self.logger.setLevel(ConcoleLevel=self.logLvl)

        # First log message.
        self.logger.info('voiceAtis started')

        # Read ini.
        self.read_ini()

        # Read file with airport frequencies and coordinates.
        self.get_airport_data()

        # Init tts engine
        self.engine = tts.sapi.Sapi()
        self.engine.set_voice("Zira")  # TODO: handle not available speech engine

        # Init pygame.mixer (playing sound files).
        mixer.init()

        # Init time of last whazzup download 100 min before call.
        self.last_whazzup_download_time = time.time() - 6000

    # Establishes pyuipc connection.
    # Return 'True' on success.
    # Return 'False' on fail.
    def connect_fsuipc(self):
        try:
            self.fsuipc_connection = FSUIPC()
            self.fsuipc_offsets = self.fsuipc_connection.prepare_data(self.OFFSETS, True)
            self.logger.info('FSUIPC connection established.')
            return True
        except NameError:
            self.fsuipc_connection = None
            self.logger.warning('Error using PYUIPC.')
            return False
        except FSUIPCException:
            self.logger.warning('FSUIPC: No simulator detected. Start you simulator first!')
            return False

    # Runs an infinite loop.
    # For first implementation without GUI.
    def start_loop(self):
        # Establish pyuipc connection
        result = False
        admin_message_sent = False
        while not result:
            result = self.connect_fsuipc()
            if not result:
                self.logger.info('Retrying in 20 seconds.')
                if not admin_message_sent:
                    self.logger.warning('If you run your simulator as admin, also run voiceAtis as admin!')
                    admin_message_sent = True
                time.sleep(20)

        # Infinite loop.
        try:
            while True:
                time_sleep = self.loop_run()
                time.sleep(time_sleep)

        except KeyboardInterrupt:
            # Actions at Keyboard Interrupt.
            self.logger.info('Loop interrupted by user.')
            self.fsuipc_connection.close()

    # One cycle of a loop.
    # Returns the requested sleep time.
    def loop_run(self):
        # Try to reestablish if no fsuipc connection is detected.
        if self.fsuipc_connection is None:
            self.connect_fsuipc()
            return self.SLEEP_TIME

        # Get sim data.
        try:
            self.get_fsuipc_data()
        except FSUIPCException:
            # If connection was lost in the meantime, reset to None and return.
            self.fsuipc_connection = None
            return self.SLEEP_TIME

        # Get best suitable Airport.
        self.get_airport()

        # Handle if no airport found.
        if self.airport is None:
            self.logger.info('No airport found, sleeping for {} seconds...'.format(self.SLEEP_TIME))
            return self.SLEEP_TIME
        else:
            self.logger.info('Airport: {}.'.format(self.airport))

        # Get atis voice.
        self.get_atis_from_airport()

        # Read the string.
        self.read_voice()

        # After successful reading.
        return 0

        # # Get whazzup file
        # self.get_whazzup_json()
        #
        # # Read whazzup text and get a station.
        # self.parse_whazzup_text()
        #
        # # Check if station online.
        # if self.atis_raw is not None:
        #     self.logger.info('Station found, decoding Atis.')
        #
        #     # Parse ATIS.
        #     # Information.
        #     self.get_info_identifier()
        #     self.parse_voice_information()
        #
        #     # Metar.
        #     if self.client_type == 'aurora':
        #         self.parse_metar(self.atis_raw[3].strip())
        #     if self.client_type == 'ivAc1':
        #         self.parse_metar(self.atis_raw[2].strip())
        #     else:
        #         for ar in self.atis_raw:
        #             if ar.startswith('METAR'):
        #                 self.parse_metar(ar.replace('METAR ', '').strip())
        #                 break
        #
        #     self.parse_voice_metar()
        #
        #     # Runways / TRL / TA
        #     self.parse_raw_rwy()
        #     self.parse_voice_rwy()
        #
        #     # comment.
        #     self.parse_voice_comment()
        #
        #     # Compose complete atis voice string.
        #     self.atis_voice = '{} {} {} {} Information {}, out,'.format(self.information_voice, self.rwy_voice,
        #                                                                 self.comment_voice, self.metar_voice,
        #                                                                 self.information_identifier)
        #
        # else:
        #     # Actions, if no station online.
        #     self.logger.info('No station online, using metar only.')
        #     with warnings.catch_warnings():
        #         warnings.simplefilter("ignore")
        #         # TODO: Get metar from a different source. (not API v1)
        #         self.metar = Metar(self.get_airport_metar(), strict=False)
        #
        #     self.parse_voice_metar()
        #
        #     # Time
        #     hours = parseVoiceInt('{:02d}'.format(self.metar._hour))
        #     minutes = parseVoiceInt('{:02d}'.format(self.metar._min))
        #
        #     # Parse atis voice with metar only.
        #     self.atis_voice = '{} weather report time {} {}, {}.'.format(self.airport_infos[self.airport][3], hours,
        #                                                                  minutes, self.metar_voice)
        #
        # # Read the string.
        # self.read_voice()
        #
        # # After successful reading.
        # return 0

    # With a determined airport, get atis_voice from whazzup data.
    def get_atis_from_airport(self):
        # Get whazzup file
        self.get_whazzup_json()

        # Read whazzup text and get a station.
        self.parse_whazzup_text()

        # Check if station online.
        if self.atis_raw is not None:
            self.logger.info('Station found, decoding Atis.')

            # Parse ATIS.
            # Information.
            self.get_info_identifier()
            self.parse_voice_information()

            # Metar.
            if self.client_type == 'aurora':
                self.parse_metar(self.atis_raw[3].strip())
            if self.client_type == 'ivAc1':
                self.parse_metar(self.atis_raw[2].strip())
            else:
                for ar in self.atis_raw:
                    if ar.startswith('METAR'):
                        self.parse_metar(ar.replace('METAR ', '').strip())
                        break

            self.parse_voice_metar()

            # Runways / TRL / TA
            self.parse_raw_rwy()
            self.parse_voice_rwy()

            # comment.
            self.parse_voice_comment()

            # Compose complete atis voice string.
            self.atis_voice = '{} {} {} {} Information {}, out,'.format(self.information_voice, self.rwy_voice,
                                                                        self.comment_voice, self.metar_voice,
                                                                        self.information_identifier)

        else:
            # Actions, if no station online.
            self.logger.info('No station online, using metar only.')
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                # TODO: Get metar from a different source. (not API v1)
                self.metar = Metar(self.get_airport_metar(), strict=False)

            self.parse_voice_metar()

            # Time
            hours = parseVoiceInt('{:02d}'.format(self.metar._hour))
            minutes = parseVoiceInt('{:02d}'.format(self.metar._min))

            # Parse atis voice with metar only.
            self.atis_voice = '{} weather report time {} {}, {}.'.format(self.airport_infos[self.airport][3], hours,
                                                                         minutes, self.metar_voice)

    # Downloads and reads the whazzup from IVAO
    def get_whazzup_json(self):
        # Check if last download was more than 5 min ago.
        if time.time() - self.last_whazzup_download_time < self.WHAZZUP_INTERVAL:
            self.logger.info(f'Last ATIS data download was less than {self.WHAZZUP_INTERVAL} seconds ago -> no update.')
            return

        # Get file from api.
        self.logger.info('Downloading new ATIS data.')
        with urllib.request.urlopen(self.WHAZZUP_URL) as response:  # , open('whazzup.txt.gz', 'wb') as out_file:
            self.whazzup_text = response.read().decode("ISO-8859-1")

        # Parse json and get atc data.
        json_loads = json.loads(self.whazzup_text)
        self.atc = json_loads['clients']['atcs']

        # shutil.copyfileobj(response, out_file)
        self.last_whazzup_download_time = time.time()

    # Find a station of the airport and read the ATIS string.
    def parse_whazzup_text(self):
        # Check if data is available.
        if not self.atc:
            self.logger.warning('No atc data available for parsing.')
            return

        # Find an open station.
        # Get preferred station order.
        if self.on_ground:
            station_suffixes = self.STATION_SUFFIXES_DEP
        else:
            station_suffixes = self.STATION_SUFFIXES_ARR

        # Search for fitting stations.
        stations_avail = []
        for st in self.atc:
            if st['callsign'].startswith(self.airport):
                stations_avail.append(st)
                if st['callsign'].endswith(station_suffixes[0]):
                    # Finish the search, if the preferred station was found.
                    break

        # Get the preferred station from available stations.
        station_chosen = None
        for su in station_suffixes:
            for st in stations_avail:
                if st['callsign'].endswith(su):
                    station_chosen = st
                    break
            # Exit loop if a station was chosen.
            if station_chosen is not None:
                break

        # Get atis from chosen station.
        if station_chosen is not None:
            self.atis_raw = station_chosen['atis']['lines']
            if station_chosen['softwareTypeId'] == 'aurora':
                self.client_type = 'aurora'
            elif station_chosen['softwareTypeId'] == 'ivAc' and station_chosen['softwareVersion'].startswith('1'):
                self.client_type = 'ivac1'
            elif station_chosen['softwareTypeId'] == 'ivAc' and station_chosen['softwareVersion'].startswith('2'):
                self.client_type = 'ivac2'
            else:
                self.client_type = 'other'

        else:
            self.atis_raw = None

    def parse_metar(self, metar_string):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.metar = Metar(metar_string, strict=False)

    # Parse runway and transition data.
    # Get active runways for arrival and departure.
    # Get transition level and altitude.
    def parse_raw_rwy(self):
        self.rwy_information = [None, None, None, None]
        # IvAc 1 or Aurora.
        if self.client_type in ['aurora', 'ivac1']:
            # Select line of rwy information.
            if self.client_type == 'aurora':
                runway_str = self.atis_raw[4]
            else:
                runway_str = self.atis_raw[3]

            # Get Position of information parts. ARR is always at 0.
            pos_dep = runway_str.find('DEP')
            pos_trl = runway_str.find('TRL')
            pos_ta = runway_str.find('TA')

            # Get strings to parse.
            runway_parts = {'ARR': runway_str[7:pos_dep - 2].strip(),
                            'DEP': runway_str[pos_dep + 7:pos_trl - 2].strip(),
                            'TRL': runway_str[pos_trl + 3:pos_ta - 2].strip(),
                            'TA': runway_str[pos_ta + 2:].strip()}

            # Parse ARR and DEP.
            for kId, k in enumerate(['ARR', 'DEP']):
                runways = []
                part_str = runway_parts[k]

                # Find rwy numbers.
                rwy_pos = []
                for rw in re.finditer(r'\d{2}', part_str):
                    rwy_pos.append(rw.start())
                rwy_pos.append(len(part_str))

                rw_count = 0
                while rw_count < len(rwy_pos) - 1:
                    dir_str = part_str[rwy_pos[rw_count]:rwy_pos[rw_count + 1]]
                    runway_num = part_str[rwy_pos[rw_count]:rwy_pos[rw_count] + 2]
                    cont_dir = False
                    for m in ['R', 'C', 'L']:
                        if m in dir_str:
                            runways.append(runway_num + m)
                            cont_dir = True
                    if not cont_dir:
                        runways.append(runway_num)

                    rw_count += 1

                # Add runways to list.
                self.rwy_information[kId] = runways

            # Parse TRL and TA.
            self.rwy_information[3] = runway_parts['TRL'][2:]
            self.rwy_information[2] = runway_parts['TA'][:-2]  # TODO: Check unit meter (russia, china).

        # Ivac 2
        else:
            for ar in self.atis_raw:
                if ar.startswith('TA'):
                    trl_ta_split = ar.split(' / ')
                    self.rwy_information[3] = trl_ta_split[0].replace('TA ', '')
                    self.rwy_information[2] = trl_ta_split[1].replace('TRL', '')

                elif ar.startswith('ARR'):
                    cur_rwy = [ar[8:10], None, None, None]
                    if 'L' in ar[8:]:
                        cur_rwy[1] = 'Left'
                    if 'C' in ar[8:]:
                        cur_rwy[2] = 'Center'
                    if 'R' in ar[8:]:
                        cur_rwy[3] = 'Right'
                    if self.rwy_information[0] is None:
                        self.rwy_information[0] = [cur_rwy]
                    else:
                        self.rwy_information[0].append(cur_rwy)

                elif ar.startswith('DEP'):
                    cur_rwy = [ar[8:10], None, None, None]
                    if 'L' in ar[8:]:
                        cur_rwy[1] = 'Left'
                    if 'C' in ar[8:]:
                        cur_rwy[2] = 'Center'
                    if 'R' in ar[8:]:
                        cur_rwy[3] = 'Right'
                    if self.rwy_information[1] is None:
                        self.rwy_information[1] = [cur_rwy]
                    else:
                        self.rwy_information[1].append(cur_rwy)

    # Generate a string of the metar for voice generation.
    def parse_voice_metar(self):
        self.metar_voice = ''

        # Wind
        if self.metar.wind_speed._value != 0:
            if self.metar.wind_dir is not None:
                self.metar_voice = '{}, wind {}, {}'.format(self.metar_voice,
                                                            parseVoiceString(self.metar.wind_dir.string()),
                                                            parseVoiceString(self.metar.wind_speed.string()))
            else:
                self.metar_voice = '{}, wind variable, {}'.format(self.metar_voice,
                                                                  parseVoiceString(self.metar.wind_speed.string()))
        else:
            self.metar_voice = '{}, wind calm'.format(self.metar_voice, self.metar.wind_dir.string(),
                                                      self.metar.wind_speed.string())

        if self.metar.wind_gust is not None:
            self.metar_voice = '{}, maximum {}'.format(self.metar_voice,
                                                       parseVoiceString(self.metar.wind_gust.string()))

        if self.metar.wind_dir_from is not None:
            self.metar_voice = '{}, variable between {} and {}'.format(self.metar_voice, parseVoiceString(
                self.metar.wind_dir_from.string()), parseVoiceString(self.metar.wind_dir_to.string()))

        # Visibility.
        # TODO: implement directions
        self.metar_voice = '{}, visibility {}'.format(self.metar_voice, self.metar.vis.string())

        # runway visual range
        rvr = self.metar.runway_visual_range().replace(';', ',')
        if rvr:
            rvr_new = ''
            last_end = 0
            rvr_pattern = re.compile(r'[0123]\d[LCR]?(?=,)')
            for ma in rvr_pattern.finditer(rvr):
                rwy_raw = rvr[ma.start():ma.end()]
                rwy_str = parseVoiceInt(rwy_raw[0:2])
                if len(rwy_raw) > 2:
                    if rwy_raw[2] == 'L':
                        rwy_str = '{} left'.format(rwy_str)
                    elif rwy_raw[2] == 'C':
                        rwy_str = '{} center'.format(rwy_str)
                    elif rwy_raw[2] == 'R':
                        rwy_str = '{} right'.format(rwy_str)
                rvr_new = '{}{}{}'.format(rvr_new, rvr[last_end:ma.start()], rwy_str)
                last_end = ma.end()

            rvr_new = '{}{}'.format(rvr_new, rvr[last_end:])

            self.metar_voice = '{}, visual range {}'.format(self.metar_voice, rvr_new)

        # weather phenomena
        if self.metar.weather:
            self.metar_voice = '{}, {}'.format(self.metar_voice, self.metar.present_weather().replace(';', ','))

        # clouds
        if self.metar.sky:
            self.metar_voice = '{}, {}'.format(self.metar_voice,
                                               self.metar.sky_conditions(',').replace(',', ', ').replace('a few',
                                                                                                         'few'))
        elif 'CAVOK' in self.metar.code:
            self.metar_voice = '{}, clouds and visibility ok'.format(self.metar_voice)

        # runway condition
        # TODO: Implement runway conditions
        # Not implemented in python-metar

        # temperature
        temp_value = parseVoiceInt(str(int(self.metar.temp._value)))
        if self.metar.temp._units == 'C':
            temp_unit = 'degree Celsius'
        else:
            temp_unit = 'degree Fahrenheit'

        self.metar_voice = '{}, temperature {} {}'.format(self.metar_voice, temp_value, temp_unit)

        # dew point
        dewpt_value = parseVoiceInt(str(int(self.metar.dewpt._value)))
        if self.metar.dewpt._units == 'C':
            dewpt_unit = 'degree Celsius'
        else:
            dewpt_unit = 'degree Fahrenheit'

        self.metar_voice = '{}, dew point {} {}'.format(self.metar_voice, dewpt_value, dewpt_unit)

        # QNH
        if self.metar.press._units == 'MB':
            press_value = parseVoiceInt(str(int(self.metar.press._value)))
            self.metar_voice = '{}, Q N H {} hectopascal'.format(self.metar_voice, press_value)
        else:
            self.metar_voice = '{}, Altimeter {}'.format(self.metar_voice, parseVoiceString(self.metar.press.string()))

        # TODO: implement trend
        self.metar_voice = f'{self.metar_voice},'

    # Generate a string of the information identifier for voice generation.
    def parse_voice_information(self):
        # Aurora or IvAc 1
        if self.client_type in ['aurora', 'ivAc1']:
            if self.client_type == 'aurora':
                info_line = self.atis_raw[1] + ' ' + self.atis_raw[2]
            else:
                info_line = self.atis_raw[1]

            # Get report time.
            time_match = re.search(r'\d{4}z', info_line)
            if time_match is not None:
                start_ind = time_match.start()
                end_ind = time_match.end() - 1
                time_str = parseVoiceInt(info_line[start_ind:end_ind])
            else:
                time_str = parseVoiceInt(datetime.utcnow().strftime('%H%M'))

            # Get Airport name.
            airport_name = self.airport_infos[self.airport][3]
            # TODO: Remove if no longer needed or set option.
            # words_list = info_line.lower().split(' ')
            # information_index = words_list.index('information')
            # airport_name = ' '.join(words_list[:information_index - 1])

            self.information_voice = f'{airport_name} information {self.information_identifier}'
            self.information_voice += f', met report time {time_str},'

        # IvAc 2
        else:
            information = self.atis_raw[1].split(' ')
            airport_name = information[0]
            airport_name = self.airport_infos[airport_name][3]
            time_str = parseVoiceInt(information[4][0:4])

            # TODO: Unify with Aurora/ivAc format.
            self.information_voice = f'{airport_name} Information {self.information_identifier} recorded at {time_str}.'

    # Generate a string of the runway information for voice generation.
    def parse_voice_rwy(self):
        self.rwy_voice = ''
        arr_dep = ['Arrival', 'Departure']

        # ARR, DEP
        for k in [0, 1]:
            if self.rwy_information[k] is not None:
                self.rwy_voice = '{}{} runway '.format(self.rwy_voice, arr_dep[k])
                for m in self.rwy_information[k]:
                    if len(m) > 2:
                        self.rwy_voice = '{}{} {}, and '.format(self.rwy_voice, parseVoiceInt(m[0:2]), RWY_TABLE[m[2]])
                    else:
                        self.rwy_voice = '{}{}, and '.format(self.rwy_voice, parseVoiceInt(m))

                self.rwy_voice = self.rwy_voice[:-6] + ', '

        # TRL
        if self.rwy_information[2] is not None:
            self.rwy_voice = '{}Transition altitude {} feet, '.format(self.rwy_voice, self.rwy_information[2])

        # TA
        if self.rwy_information[3] is not None:
            self.rwy_voice = f'{self.rwy_voice}Transition level {parseVoiceInt(self.rwy_information[3])},'

    # Generate a string of ATIS comment for voice generation.
    def parse_voice_comment(self):
        if self.client_type == 'aurora' and len(self.atis_raw) > 6:
            self.comment_voice = '{},'.format(parseVoiceString(self.atis_raw[5].replace('RMK ', '')))
        elif self.client_type == 'ivac1' and len(self.atis_raw) > 5:
            self.comment_voice = '{},'.format(parseVoiceString(self.atis_raw[4]))
        else:
            self.comment_voice = ''

    def read_voice(self):
        # TODO: Start first reading at random place in string.

        # Set properties currently reading
        self.currently_reading = self.airport

        # Log ATIS text.
        try:
            self.logger.info('ATIS Text is: {}'.format(self.atis_voice))
        except:
            # TODO: Fix too broad except.
            self.logger.info('ATIS Text cannot be displayed: unexpected characters.')

        # Create tmp folder.
        if not os.path.isdir('tmp'):
            os.mkdir('tmp')

        # Get tmp name.
        file_count = 0
        file_tmp = 'tmp/atis_0.wav'
        while os.path.isfile(file_tmp):
            file_count += 1
            file_tmp = 'tmp/atis_{}.wav'.format(file_count)

        # Create tmp wav file.
        self.logger.info('Generating ATIS sound.')
        self.engine.create_recording(file_tmp, self.atis_voice)

        # Apply radio effect.
        self.logger.info('Generating radio effects.')
        AudioEffect.radio(file_tmp, file_tmp)

        # Get wav duration.
        with contextlib.closing(wave.open(file_tmp, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            self.wav_duration = frames / float(rate)

        # Start reading.
        mixer.music.load(file_tmp)
        self.logger.info('Start reading.')
        mixer.music.play()

        while mixer.music.get_busy():
            self.onWord()
            tmpfiles = os.listdir('tmp')
            for k in tmpfiles:
                full_path = 'tmp/' + k
                if full_path != file_tmp:
                    try:
                        os.remove(full_path)
                    except:
                        pass
            time.sleep(0.5)

        self.logger.info('Reading finished.')

    # Callback for stop of reading.
    # Stops reading if frequency change/com deactivation/out of range.
    def onWord(self):
        if self.fsuipc_connection is not None:
            self.get_fsuipc_data()
            self.get_airport()

        if self.airport != self.currently_reading:
            mixer.music.stop()
            self.currently_reading = None
            self.logger.info('Reading interrupted.')

    # Reads current frequency and COM status.
    def get_fsuipc_data(self):
        # Get results from FSUIPC connection.
        try:
            results = self.fsuipc_offsets.read()
        except FSUIPCException:
            # Return if connection lost in the meantime.
            self.fsuipc_connection = None
            self.logger.warning('FSUIPC connection lost!')
            return

        # frequency
        # TODO: Check 8.33 kHz. (125.205 = 125.200)
        hex_code = hex(results[0])[2:]
        self.com1frequency = float('1{}.{}'.format(hex_code[0:2], hex_code[2:]))
        hex_code = hex(results[1])[2:]
        self.com2frequency = float('1{}.{}'.format(hex_code[0:2], hex_code[2:]))
        hex_code = hex(results[5])[2:]
        self.nav1frequency = float('1{}.{}'.format(hex_code[0:2], hex_code[2:]))
        hex_code = hex(results[6])[2:]
        self.nav2frequency = float('1{}.{}'.format(hex_code[0:2], hex_code[2:]))

        # radio active
        # TODO: Test accuracy of this data (with various planes and sims)
        radio_active_bits = list(map(int, '{0:08b}'.format(results[2])))
        if radio_active_bits[2]:
            self.com1active = True
            self.com2active = True
        elif radio_active_bits[0]:
            self.com1active = True
            self.com2active = False
        elif radio_active_bits[1]:
            self.com1active = False
            self.com2active = True
        else:
            self.com1active = False
            self.com2active = False

        if radio_active_bits[3]:
            self.nav1active = True
        else:
            self.nav1active = False
        if radio_active_bits[4]:
            self.nav2active = True
        else:
            self.nav2active = False

        # lat lon
        self.lat = results[3] * (90.0 / (10001750.0 * 65536.0 * 65536.0))
        self.lon = results[4] * (360.0 / (65536.0 * 65536.0 * 65536.0 * 65536.0))

        # on ground.
        self.on_ground = results[7]

        # Logging.
        if self.com1active:
            com1active_str = 'active'
        else:
            com1active_str = 'inactive'
        if self.com2active:
            com2active_str = 'active'
        else:
            com2active_str = 'inactive'
        if self.nav1active:
            nav1active_str = 'active'
        else:
            nav1active_str = 'inactive'
        if self.nav2active:
            nav2active_str = 'active'
        else:
            nav2active_str = 'inactive'

        if mixer.music.get_busy():
            self.logger.debug(
                'COM 1: {} ({}), COM 2: {} ({})'.format(self.com1frequency, com1active_str, self.com2frequency,
                                                        com2active_str))
            self.logger.debug(
                'NAV 1: {} ({}), NAV 2: {} ({})'.format(self.nav1frequency, nav1active_str, self.nav2frequency,
                                                        nav2active_str))
        else:
            self.logger.info(
                'COM 1: {} ({}), COM 2: {} ({})'.format(self.com1frequency, com1active_str, self.com2frequency,
                                                        com2active_str))
            self.logger.info(
                'NAV 1: {} ({}), NAV 2: {} ({})'.format(self.nav1frequency, nav1active_str, self.nav2frequency,
                                                        nav2active_str))

    # Determine if there is an airport applicable for ATIS reading.
    def get_airport(self):
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
            distance_min = self.RADIO_RANGE + 1
            for ap in self.airport_infos:
                distance = gcDistanceNm(self.lat, self.lon, self.airport_infos[ap][1], self.airport_infos[ap][2])
                if distance < self.RADIO_RANGE and distance < distance_min:
                    for fr in self.airport_infos[ap][0]:
                        if (floor(fr * 100) / 100) in frequencies:
                            distance_min = distance
                            self.airport = ap
                            break

    # Read data of airports from a given file.
    def get_airport_data_file(self, ap_file):
        # Check if file exists.
        if not os.path.isfile(ap_file):
            self.logger.warning('No such file: {}'.format(ap_file))
            return

        # Read the file.
        with open(ap_file, encoding="utf8") as aptInfoFile:
            for li in aptInfoFile:
                line_split = re.split('[,;]', li)
                if not li.startswith('#') and len(line_split) == 5:
                    freq_str = line_split[1].split('^')
                    freq_list = []
                    for fr in freq_str:
                        freq_list.append(float(fr))
                    self.airport_infos[line_split[0].strip()] = (
                        freq_list, float(line_split[2]), float(line_split[3]), line_split[4].replace('\n', ''))

    # Read data of airports from http://ourairports.com.
    def get_airport_data_web(self):
        airport_freqs = {}

        # Read the file with frequency.
        response = urllib.request.urlopen(self.OUR_AIRPORTS_URL + 'airport-frequencies.csv')
        data = response.read()
        ap_freq_text = data.decode(ENCODING_TYPE)

        # Get the frequencies from the file.
        for li in ap_freq_text.split('\n'):
            line_split = li.split(',')
            if len(line_split) > 3 and line_split[3] == '"ATIS"':
                airport_code = line_split[2].replace('"', '')
                if airport_code not in airport_freqs:
                    airport_freqs[airport_code] = [float(line_split[-1].replace('\n', ''))]
                else:
                    airport_freqs[airport_code].append(float(line_split[-1].replace('\n', '')))

        # Read the file with other airport data.
        response = urllib.request.urlopen(self.OUR_AIRPORTS_URL + 'airports.csv')
        data = response.read()
        ap_text = data.decode(ENCODING_TYPE)

        # Add frequency and write them to self. airportInfos.
        for li in ap_text.split('\n'):
            line_split = re.split(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", li)

            if len(line_split) > 1:
                ap_code = line_split[1].replace('"', '')
                if ap_code in airport_freqs and len(ap_code) <= 4:
                    self.airport_infos[ap_code] = [airport_freqs[ap_code], float(line_split[4]), float(line_split[5]),
                                                   line_split[3].replace('"', '')]

    # Reads airportData from two sources.
    def get_airport_data(self):
        self.airport_infos = {}

        # Check update date of airport data.
        # Airport data only have to be downloaded once a day.
        if 'lastAirportDownload' in self.ini_options:
            if self.ini_options['lastAirportDownload'] == datetime.today().strftime('%d%m%y'):
                self.logger.info('Airport data up to date.')
                self.get_airport_data_file(os.path.join(self.rootDir, 'supportFiles', 'airports.info'))
                return

        try:
            # Try to read airport data from web.
            self.logger.info('Downloading airport data. This may take some time.')
            self.get_airport_data_web()
            self.get_airport_data_file(os.path.join(self.rootDir, 'supportFiles', 'airports_add.info'))
            collected_from_web = True
            self.logger.info('Finished downloading airport data.')

        except:
            # If this fails, use the airports from airports.info.
            self.logger.warning(
                'Unable to get airport data from web. Using airports.info. Error: {}'.format(sys.exc_info()[0]))
            self.airport_infos = {}
            collected_from_web = False
            try:
                self.get_airport_data_file(os.path.join(self.rootDir, 'supportFiles', 'airports.info'))
            except:
                self.logger.error('Unable to read airport data from airports.info!')

        # Sort airportInfos and write them to a file for future use if collected from web.
        if collected_from_web:
            ap_info_path = os.path.join(self.rootDir, 'supportFiles', 'airports.info')
            ap_list = list(self.airport_infos.keys())
            ap_list.sort()
            with open(ap_info_path, 'w', encoding=ENCODING_TYPE) as apDataFile:
                for ap in ap_list:
                    freq_str = ''
                    for fr in self.airport_infos[ap][0]:
                        freq_str = '{}{}^'.format(freq_str, fr)
                    apDataFile.write('{:>4}; {:20}; {:11.6f}; {:11.6f}; {}\n'.format(ap, freq_str.strip('^'),
                                                                                     self.airport_infos[ap][1],
                                                                                     self.airport_infos[ap][2],
                                                                                     self.airport_infos[ap][3]))

            self.ini_options['lastAirportDownload'] = datetime.today().strftime('%d%m%y')
            self.write_ini()

    # Determines the info identifier of the loaded ATIS.
    def get_info_identifier(self):
        if self.client_type == 'ivac1':
            information_pos = re.search('information ', self.atis_raw[1].lower()).end()
            information_split = self.atis_raw[1][information_pos:].split(' ')
            self.information_identifier = information_split[0]
        elif self.client_type == 'aurora':
            information_pos = re.search('information ', self.atis_raw[2].lower()).end()
            information_split = self.atis_raw[2][information_pos:].split(' ')
            self.information_identifier = information_split[0]
        else:
            self.information_identifier = CHAR_TABLE[re.findall(r'(?<=ATIS )[A-Z](?= \d{4})', self.atis_raw[1])[0]]

    # Retrieves the metar of an airport independent of an ATIS.
    def get_airport_metar(self):
        response = urllib.request.urlopen(self.NOAA_METAR_URL.replace('<station>', self.airport))
        data = response.read()
        metar_text = data.decode(ENCODING_TYPE)

        # Split at newline.
        metar_text_split = metar_text.split('\n')

        return metar_text_split[1]

    # Get information from voiceAtis.ini file.
    # File is created if it doesn't exist.
    def read_ini(self):
        self.ini_options = {}
        if os.path.isfile('voiceAtis.ini'):
            with open('voiceAtis.ini') as iniFile:
                ini_content = iniFile.readlines()
            for k in ini_content:
                line = k.split('=')
                self.ini_options[line[0].strip()] = line[1].strip()
        else:
            self.write_ini()

    # Write information to voiceAtis.ini
    def write_ini(self):
        with open('voiceAtis.ini', 'w') as iniFile:
            for k in self.ini_options:
                iniFile.write('{}={}\n'.format(k, self.ini_options[k]))


if __name__ == '__main__':
    voiceAtis = VoiceAtis()
    #     voiceAtis = VoiceAtis(Debug=True)
    voiceAtis.start_loop()
