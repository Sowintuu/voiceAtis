#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# =============================================================================
# voiceAtisGUI - A GUI to show information from and control voiceAtis
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
# =============================================================================
import re

from tkinter import Tk, Button, Entry, Label, Radiobutton, StringVar, Text
from voiceAtis import VoiceAtis


class VoiceAtisGUI(object):
    STEP_INTERVAL = 25

    def __init__(self):
        # Init attributes.
        # Gui master.
        self.master = None

        # Gui elements.
        self.source = None
        self.l_connected = None
        self.b_connect = None

        self.v_airport = None
        self.l_airport = None
        self.r_airport = None
        self.e_airport = None

        self.v_frequency = None
        self.l_frequency = None
        self.r_frequency = None
        self.e_frequency = None

        self.r_from_sim = None
        self.l_from_sim = None

        self.t_atis = None

        # Other attributes.
        self.fsuipc_connected = False

        # Init voice ATIS.
        self.voice_atis = VoiceAtis()

        # Init window.
        self.init_window()

    def init_window(self):
        # Init window master.
        self.master = Tk()
        self.master.title('Voice ATIS')
        self.master.resizable(0, 0)

        # Init variables.
        self.source = StringVar()
        self.source.set('Airport')

        # Init gui elements.
        row = 0
        self.l_connected = Label(text='Not connected', bg='red', fg='white')
        self.l_connected.grid(row=row, column=0)
        self.b_connect = Button(text='Connect to simulator', command=self.cb_b_connect)
        self.b_connect.grid(row=row, column=1)

        row += 1
        self.v_airport = StringVar()
        self.v_airport.trace_add('write', self.cb_e_airport)

        self.r_airport = Radiobutton(text='Airport', variable=self.source, value='airport',
                                     command=self.cb_radiobuttons)
        self.r_airport.grid(row=row, column=0, sticky='W')
        self.e_airport = Entry(textvariable=self.v_airport)
        self.e_airport.grid(row=row, column=1)
        # self.e_airport.bind('<Key>', lambda event: self.cb_e_airport())

        row += 1
        self.v_frequency = StringVar()
        self.r_frequency = Radiobutton(text='Frequency', variable=self.source, value='frequency',
                                       command=self.cb_radiobuttons)
        self.r_frequency.grid(row=row, column=0, sticky='W')
        self.e_frequency = Entry(textvariable=self.v_frequency)
        self.e_frequency.grid(row=row, column=1)

        row += 1
        self.r_from_sim = Radiobutton(text='From Sim', variable=self.source, value='sim', state='disabled',
                                      command=self.cb_radiobuttons)
        self.r_from_sim.grid(row=row, column=0, sticky='W')

        row += 1
        self.t_atis = Text(width=30, height=10)
        self.t_atis.grid(row=row, column=0, columnspan=2, sticky='W')

        # Start mainloop.
        self.master.after(self.STEP_INTERVAL, self.step)
        self.master.mainloop()

    def step(self):
        # Check and get airport.
        if self.source.get() == 'airport':
            # Get airport from Entry and send to voice_atis.
            airport_entry = self.v_airport.get()
            if airport_entry in self.voice_atis.airport_infos:
                self.voice_atis.airport = airport_entry
            else:
                self.voice_atis.airport = None

        elif self.source.get() == 'frequency':
            # Get frequency from entry.
            try:
                self.voice_atis.com1frequency = float(self.v_frequency.get())
            except ValueError:
                self.master.after(self.STEP_INTERVAL, self.step)
                return
            # Set com1 in voice_atis (not in sim) to active to read from it.
            self.voice_atis.com1active = True
            # Get airport from frequency.
            self.voice_atis.get_airport()

        elif self.source.get() == 'sim':
            # Check if FSUIPC is still connected and get pyuipc data.
            if self.voice_atis.fsuipc_connection is None:
                self.l_connected.config(text='Connected', bg='red', fg='white')
                self.r_from_sim.config(state='disabled')
                self.source.set('airport')

            # Get airport.
            self.voice_atis.get_fsuipc_data()
            self.voice_atis.get_airport()

        # Check if an airport was found. Otherwise end the step.
        if self.voice_atis.airport is None:
            self.master.after(self.STEP_INTERVAL, self.step)
            return

        # Set entry to airport chosen.
        self.v_airport.set(self.voice_atis.airport)

        # Get atis voice.
        self.voice_atis.get_atis_from_airport()

        # Read the string.
        self.voice_atis.read_voice()

        # Schedule next step execution.
        self.master.after(self.STEP_INTERVAL, self.step)

    def cb_b_connect(self):
        fsuipc_connected = self.voice_atis.connect_fsuipc()

        if fsuipc_connected:
            self.l_connected.config(text='Connected', bg='green', fg='black')
            self.r_from_sim.config(state='normal')

    def cb_radiobuttons(self):
        if self.source.get() == 'airport':
            self.e_airport.config(state='normal')
            self.e_frequency.config(state='disabled')
        elif self.source.get() == 'frequency':
            self.e_airport.config(state='disabled')
            self.e_frequency.config(state='normal')
        elif self.source.get() == 'sim':
            self.e_airport.config(state='disabled')
            self.e_frequency.config(state='disabled')

    def cb_e_airport(self, *args):
        # Get current airport string.
        current_content = self.v_airport.get()

        # Replace wrong chars.
        new_content = re.sub(r'[\WäöüÄÖÜ]', '', current_content).upper()

        # Cut to 4 chars.
        if len(new_content) > 4:
            new_content = new_content[:4]

        # Write adjusted string to entry.
        self.v_airport.set(new_content)
        self.e_airport.update()


if __name__ == '__main__':
    voice_gui = VoiceAtisGUI()
