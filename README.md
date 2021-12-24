# voiceAtis
Reads an ATIS from IVAO using voice generation.

## Requirements
* XPlane with [XPUIPC](http://fsacars.com/downloads/xpuipc/) **-or-** 
* FSX, P3D with [FSUIPC](http://www.schiratti.com/dowson.html)

## Installation
* Get the latest release from the [releases tab](https://github.com/Sowintuu/voiceAtis/releases).
* Unzip the folder.
* Disable Windows Defender check for voiceAtis. Of course, voiceAtis is no malicious code. But as the "voiceAtis.exe" is from a source unknown to Defender it will issue a warning. You can disable it like this (thanks to Stackoverflow user "kunif"):
    * Go to Start > Settings > Update & Security > Windows Security > Virus & threat protection.
    * Under "Virus & threat protection settings", select "Manage settings" and then under "Exclusions", select "Add or remove exclusions".
    * Select "Add an exclusion". Select the voiceAtis folder.

## Usage
* Start your sim and start a flight.
* Start the voiceAtis.exe file in the unzipped folder.
   * **Note that you must start the .exe as admin if you have started your sim as admin!**
* Tune the ATIS frequency of the airport where you are parking.
   * Don't forget to activate receive mode of the radio (COM1, COM2, NAV1, NAV2)
* You should hear the ATIS now, if:
   * There is an ATC station online at this airport (TWR, APP, GND or DEL)
   * The airport has an ATIS frequency at [ourairports.com](http://ourairports.com)
* If there is a frequency, but no station online, voiceAtis will read the current METAR only.

### Custom airport data
Airport data is downloaded from [ourairports.com](http://ourairports.com). You can see these data at `airports.info` file at main directory. It may happen that this data is inaccurate or an airport is missing.

In this case you can add the airport to the `airports_add.info` file. Airports in this file have priority over downloaded data.

You may also inform me about wrong data preferably via the Issues tab. I will then enter the data at [ourairports.com](http://ourairports.com) to distritbute them to all users. Alternatively, after login, you may correct the data on your own.
Changes are available to voiceAtis at the following day after the change at ourairports.

### Notice for X-Plane users
X-Plane has its own ATIS information broadcast, often on the same (real) frequency. After tuning in the ATIS frequency you will hear the X-Plane ATIS message first and then the message provided by voiceAtis. Because X-Plane also uses the operation system text-to-speech machine like voiceAtis, the voice messages are queued and read after each other.

To avoid the broadcast of the default ATIS, I added the script `disableXpAtis.lua` which is located in the supportFiles folder. You must have [FlyWithLua](https://forums.x-plane.org/index.php?/files/file/38445-flywithlua-ng-next-generation-edition-for-x-plane-11-win-lin-mac/) installed and add the script to the FlyWithLua Scripts folder.

### Notice for FSX users
FSX also has its own ATIS information broadcast on the same frequency. It uses its own voice engine thus doesn't interfer with voiceAtis. Nevertheless the spoken messages and the displayed text may be disturbing. To disable them uncheck the following options.
* Options > General > All ATC options
* Options > Sounds > Voice

### Notice for P3D users
I don't own P3D but voiceAtis was tested up to v0.3.0, and it worked. 

To disable the default ATIS in P3D follow these steps:
* Disable ATIS Voice: Options > General > Sound > Uncheck "Voice"
* Disable ATIS Text: Options > General > Information > Uncheck "Show message log in ATC menu"

## Bugs and issues
* Please report bugs via the GitHub issues tab.
    * It is useful to attach the logfile from the "logs" folder.
    
### Known limitations
* METAR
    * No trend
    * No visibility directions
    * No runway condition
* IvAc 2 support discontinued
    * Reading ATIS from IvAc 2 works. However, there are bugs and this won't be improved in the future.
    * Remarks of IvAc 2 stations will not be read.
* X-Plane: Detection of active COM not accurate
    * To work reliable, activate receive for both COM1 and COM2 
* Frequency used may not match the real world frequency
    * Check [ourairports.com](http://ourairports.com) for the frequencies used.
	* It is a community project, feel free to update the frequencies (or tell me).

## Build
### Requirements
* Python 3.9 (lower versions may work though, not tested)
    * 32 bit for 32 bit simulators (e.g. FSX, old versions of P3D, XP10)
    * 64 bit for 64 bit simulators (e.g. XP11, newer versions of P3D)

### Installation
* **Pip currently not supported, will be updated**
* For the latest version, clone the repository
* Get the latest python 3.9 ([Python releases](https://www.python.org/downloads/))
* Run `pip install voiceAtis`

### Using pyinstaller.
Build an executable using the following command:

`pyinstaller voiceAtis.py`

## Used packages and Copyright
### python-metar
Used to parse the metar contained in the ATIS.

Copyright (c) 2004-2018, Tom Pollard
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

  Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

### pyttsx
Text-to-speech package for python. Used to read the parsed ATIS string.

pyttsx Copyright (c) 2009, 2013 Peter Parente

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


### pyuipc - FSUIPC SDK for Python
Used to get the com frequencies, com status, aircraft coordinates from the simulator.

All Copyright - Peter Dowson and István Váradi.

### [ourairports.com](http://ourairports.com)
OurAirports is a free site where visitors can explore the world's airports, read other people's comments, and leave their own. The help pages have information to get you started.

The site is dedicated to both passengers and pilots. You can create a map of the airports you've visited and share that map with friends. You can find the closest airports to you, and discover the ones that you haven't visited yet.

Behind the fun and features, OurAirports exists primarily as a public good. When Australia forced the US government to shut down public access to its Digital Aeronautical Flight Information File (DAFIF) service in 2006, there was no longer a good source of global aviation data. OurAirports started in 2007 primarily to fill that gap: we encourage members to create and maintain data records for airports around the world, and they manage over 40,000 of them. Many web sites, smartphone apps, and other services rely on OurAirport's data, which is all in the Public Domain (no permission required).

See the [Credits](http://ourairports.com/about.html#credits) for a list of contributors.

## Changelog
### version 0.5.0 - upcoming
* Large code refactor to comply with PEP8
* Usage of fsuipc package instead of pyuipc package
* Adjustment to Whazzup v2
* Corrected typos in Readme

### version 0.4.0 - 17.06.2020
* Support of airports with multiple AITS frequencies
    * Message is read, if one of the frequencies is tuned.
* Support of ATIS broadcast via NAV
* Airport data are now downloaded only once a day. (performance improvement)
* Whazzup data is now only downloaded every 5 minutes or more.
* Removed some debugging code.
* A lot of new information in this document (README.md)

### version 0.3.0 - 16.06.2020
* Complete rework of voice generation logic
    * Change from pyttsx3 to tts
	* Added a radio effect (via AudioLib)
	* Fixed stop of reading when frequency is changed
* Changed station priority logic
    * On ground priority is now DEL > GND > TWR > DEP > APP
	* In the air priority is now APP > TWR > GND > DEL > DEP
* Included legal advice at start of the program

### version 0.2.1 - 12.06.2020
* Small fixes for first standalone release

### version 0.2.0 - 12.06.2020
* Ported to python 3.8
* Added Aurora support
* Complete rework of runway parse logic
* Termination of IvAc 2 support
* Minor fixes

### version 0.1.6 - 24.12.2018
* Fix: Using COM1 frequency
* Tested with FSX

### version 0.1.5 - 21.12.2018
* Changes for improved realism
    * Changed order (metar to the end)
    * Removed "zulu" from time

### version 0.1.4 - 20.12.2018
* Fix: setup.py
* Fix: paths when running from python folder
* Fix: import
* Fix: pip requirements

### version 0.1.0 - 18.12.2018
* Included requirements to `setup.py`

### version 0.0.8 - 18.12.2018
* Created my own custom logger class
* Included `pyuipc.pyd` in the repository
* Small fixes

### version 0.0.7 - 15.12.2018
* Provided the script `xpRemoveAtisFreq`
* First upload to pypi
* Added pyuipc msi to files
* Fix: Bug for multiple runways for departure/arrival
* Fix: Bug reading empty line of airports_add.info

### version 0.0.6 - 14.12.2018
* Implemented parsing of ATIS created with IvAc 2
* Disabled warnings of python-metar

### version 0.0.5 - 13.12.2018
* Runway identifier at metar converted correctly
* Additional ATIS comment parsed for IvAc 1

### version 0.0.4 - 12.12.2018
* Getting airport data from web now (http://ourairports.com)
    * Option to add additional data
* Reading airport name now instead of airport code in metar only mode
* Added warning message receiving IvAc 2 ATIS

### version 0.0.3 - 07.12.2018
* Now using metar if no ATIS available
* pyuipc tested and running
* Changed RADIO_RANGE to a (realistic) value of 180 nm
* Implemented logging

### version 0.0.2 - 05.12.2018
* Implemented wind gusts and variable wind
* Port to python2 (due to pyuipc)
* Added pyuipc (untested)
* Added logic to get airport

### version 0.0.1 - 03.12.2018
* First version for testing purposes
* Some Atis features missing
* No pyuipc
* Voice not tested

## ROADMAP
* Random start
* GUI for settings and display
