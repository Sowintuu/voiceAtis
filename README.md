# voiceAtis
Reads an ATIS from IVAO using voice generation.

## Requirements
* XPlane with [XPUIPC](http://fsacars.com/downloads/xpuipc/) **-or-** 
* FSX, P3D with [FSUIPC](http://www.schiratti.com/dowson.html)
    * P3D not tested yet

## Installation
* Get the latest release from the [releases tab](https://github.com/Sowintuu/voiceAtis/releases).
* Unzip the folder.

## Usage
* Start your sim and start a flight.
* Start the voiceAtis.exe file in the unziped folder.
   * **Note that you must start the .exe as admin if you have started your sim as admin!**
* Tune the ATIS frequency of the airport where you are parking.
   * Don't forget to activate receive mode of the radio (COM1 or COM2)
* You should hear the ATIS now, if:
   * There is an ATC station online at this airport (TWR, APP, GND or DEL)
   * The airport has an ATIS frequency at [ourairports.com](http://ourairports.com)
* If there is an frequency, but no station only, voiceAtis will read the current METAR only.

### Custom airport data
Airport data is downloaded from [ourairports.com](http://ourairports.com). You can see these data at `airports.info` file at main directory. It may happen that this data is inaccurate or an airport is missing.

In this case you can add the airport to the `airports_add.info` file. Airports in this file have priority over downloaded data.

You may also inform me about wrong data preferably via the Issues tab. I will then enter the data at [ourairports.com](http://ourairports.com) to distritbute them to all users. Alternatively, after login, you may correct the data on your own.

### Notice for X-Plane users
X-Plane has its own ATIS information broadcasted, often on the same (real) frequency. After tuning in the ATIS frequency you will hear the X-Plane ATIS message first and then the message provided by voiceAtis. Because X-Plane also uses the operation system text-to-speech machine like voiceAtis, the voice messages are queued and read after each other.

To avoid the broadcast of the default ATIS, I added the script `disableXpAtis.lua` which is located in the supportFiles folder. You must have [FlyWithLua](https://forums.x-plane.org/index.php?/files/file/38445-flywithlua-ng-next-generation-edition-for-x-plane-11-win-lin-mac/) installed and add the script to the FlyWithLua Scripts folder.

### Notice for FSX users
FSX also has its own ATIS information broadcasted on the same frequency. It uses its own voice engine thus doesn't interfer with voiceAtis. Nevertheless the spoken messages and the displayed text may be disturbing. To disable them uncheck the following options.
* Options > General > All ATC options
* Options > Sounds > Voice

### Notice for P3D users
I didn't test voiceAtis with P3D as I don't own this simulator, but it should work with the appropriate version of FSUIPC. If you are a P3D user, please tell me if it worked. If it didn't work, open an issue so that I can fix it.

Also instructions to disable the standard ATIS of the simulator are highly appreciated!

## Bugs and issues
* Please report bugs via the github issues tab.
    * It is usefull to attach the logfile from the "logs" folder.
    
### Known limitations
* METAR
    * No trend
    * No visibility directions
    * No runway condition
* IvAc 2 support discontinued
   * Reading ATIS from IvAc 2 works. However there are bugs and this wont be improved.
   * Remarks of ivac 2 stations will not be read.
* X-Plane: Detection of active radio not accurate
* Sometimes airports have more than 1 ATIS frequency (e.g. EDDF or LOWW, for departure and arrival)
    * You might have to try all frequencies to find the one working.
    * Check [ourairports.com](http://ourairports.com) for the (real world) frequencies.

## Build
### Requirements
* Python 3.8 - 32 bit (due to pyuipc incompatibility with 64 bit)
* pywin32

### Installation
* Get the latest python 3.8 ([Python releases](https://www.python.org/downloads/))
* Install the latest pywin32 release (`pip install pywin32`)
* Run `pip install voiceAtis`

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

See the [Credits](http://ourairports.com/about.html#credits) for a list of contributers.

## Changelog

### version 0.3.0 - 16.06.2020
* Complete rework of voice generation logic
    * Change from pyttsx3 to tts
	* Added a radio effect (via AudioLib)
	* Fixed stop of reading when frequency is changed
* Changed station priority logic
    * On ground prio is now DEL > GND > TWR > DEP > APP
	* In the air prio is now APP > TWR > GND > DEL > DEP
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
* Implemented parsing of ATIS created with ivac 2
* Disabled warnings of python-metar

### version 0.0.5 - 13.12.2018
* Runway identifier at metar converted correctly
* Additional ATIS comment parsed for ivac 1

### version 0.0.4 - 12.12.2018
* Getting airport data from web now (http://ourairports.com)
    * Option to add additional data
* Reading airport name now instead of airport code in metar only mode
* Added warning message receiving ivac 2 ATIS

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
* Some Atis feartures missing
* No pyuipc
* Voice not tested

## ROADMAP
* Random start
* GUI for settings and display
