#!/usr/bin/python3

import struct
import time
import serial
import curses

def readData():
    if ser.isOpen():
        data = bytes([0xf0])
        ser.write( data )
        ser.flush()

        time.sleep( 0.5 )

        data = bytes()

        while ser.inWaiting():
            data += ser.read()

        if len(data) > 0:

            line = ""

            stdscr.move(1,0)

            for byte in data:
                line = line + "{:02x} ".format(byte)
                if len(line) > 80:
                    stdscr.addstr( "{}\n".format(line) )
                    line = ""

            stdscr.addstr( "{}\n".format(line) )

            global brightness
            global timeout
            global recCurrent

            voltage = int.from_bytes( data[2:4], byteorder="big" ) / 100.0
            current = int.from_bytes( data[4:6], byteorder="big" ) / 1000.0
            temp = int.from_bytes( data[10:12], byteorder="big" )
            power = int.from_bytes( data[8:10], byteorder="big" ) / 1000.0
            energyW = int.from_bytes( data[22:24], byteorder="big" )
            energyA = int.from_bytes( data[18:20], byteorder="big" )
            group = int.from_bytes( data[14:16], byteorder="big" )
            voltagePos = int.from_bytes( data[96:98], byteorder="big" ) / 100.0
            voltageNeg = int.from_bytes( data[98:100], byteorder="big" ) / 100.0
            resistance = int.from_bytes( data[124:126], byteorder="big" ) / 10.0
            recCurrent = int.from_bytes( data[110:112], byteorder="big" )
            recTime = int.from_bytes( data[114:116], byteorder="big" )
            timeout = int.from_bytes( data[118:120], byteorder="big" )
            brightness = int.from_bytes( data[120:122], byteorder="big" )
            screen = int.from_bytes( data[126:128], byteorder="big" )

            realRecCurrent = recCurrent / 100.0

            line = ""

            stdscr.move(8,0)

            for counter in range(0,len(data),2):
                line = line + "({:03}): {:5}   ".format(counter,int.from_bytes( data[counter:counter+2], byteorder="big" ))
                if len(line) > 80:
                    stdscr.addstr( "{}\n".format(line) )
                    line = ""

            stdscr.addstr( "{}\n".format(line) )

            stdscr.move(21,0)

            stdscr.addstr( "Spannung: {:04.2f}V\n".format(voltage) )
            stdscr.addstr( "Strom: {:04.3f}A\n".format(current) )
            stdscr.addstr( "Temperatur: {}°C\n".format(temp) )
            stdscr.addstr( "\n" )
            stdscr.addstr( "Datengruppe: {}\n".format(group) )
            stdscr.addstr( "Leistung: {:05.3f}W\n".format(power) )
            stdscr.addstr( "Energie: {}mAh\n".format(energyA) )
            stdscr.addstr( "Energie: {}mWh\n".format(energyW) )
            stdscr.addstr( "Widerstand: {}Ω\n".format(resistance) )
            stdscr.addstr( "\n" )
            stdscr.addstr( "+: {}V\n".format(voltagePos) )
            stdscr.addstr( "-: {}V\n".format(voltageNeg) )
            stdscr.addstr( "\n" )
            stdscr.addstr( "Trigger Strom: {}A\n".format(realRecCurrent) )

            hours = int(recTime/60/60)
            minutes = int(recTime%3600/60)
            seconds = recTime % 60
            stdscr.addstr( "Aufnahmezeit: {:02}:{:02}:{:02}\n".format(hours,minutes,seconds) )
            stdscr.addstr( "\n" )

            stdscr.addstr( "Timeout: {}\n".format(timeout) )
            stdscr.addstr( "Helligkeit: {}\n".format(brightness) )
            stdscr.addstr( "\n" )
            stdscr.addstr( "aktives Interface: {}\n".format(screen) )

            stdscr.addstr( "\n" )

            # Menüeinträge mit den aktuellen Werten aktualisieren
            menuEntries = menuEntriesTemplate.copy()
            menuEntries[4] = menuEntries[4].format(brightness)
            menuEntries[5] = menuEntries[5].format(timeout)
            menuEntries[6] = menuEntries[6].format(recCurrent / 100.0)

            # Menü zeichnen
            pos = 0
            for entry in range( 0, len(menuEntries) ):
                if entry != activeEntry:
                    stdscr.addstr( 42, pos, " " + menuEntries[entry] + " ", curses.color_pair(1) )
                else:
                    stdscr.addstr( 42, pos, " " + menuEntries[entry] + " ", curses.color_pair(2) )
                pos = pos + len( menuEntries[entry] ) + 2

            stdscr.refresh()
        else:
            stdscr.erase()

def executeMenuCommand( entry, key = 0 ):

    global brightness
    global timeout
    global recCurrent

    if entry == 0:
        # next Page
        ser.write( [0xf1] )
        ser.flush()

    elif entry == 1:
        # next Group
        ser.write( [0xf3] )
        ser.flush()

    elif entry == 2:
        # rotate Screen
        ser.write( [0xf2] )
        ser.flush()

    elif entry == 3:
        # reset Data
        ser.write( [0xf4] )
        ser.flush()

    elif entry == 4:
        newBrightness = brightness + key
        if newBrightness > 5:
            newBrightness = 0
        if newBrightness < 0:
            newBrightness = 5
        ser.write( [0xd0+newBrightness] )
        ser.flush()

    elif entry == 5:
        newTimeout = timeout + key
        if newTimeout > 9:
            newTimeout = 0
        if newTimeout < 0:
            newTimeout = 9
        ser.write( [0xe0+newTimeout] )
        ser.flush()

    elif entry == 6:
        newCurrent = recCurrent + key
        if newCurrent > 29:
            newCurrent = 0
        if newCurrent < 0:
            newCurrent = 29
        ser.write( [0xb0+newCurrent] )
        ser.flush()

    elif entry == 7:
        stdscr.keypad(0)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        exit(0)

menuEntriesTemplate = [ "nächste Seite", "nächste Gruppe", "Display rotieren", "reset Data", "Display Helligkeit [{}]", "Display Timeout [{}]", "Min Strom [{:03.2f}]", "beenden" ]
activeEntry = 0

brightness = 0
timeout = 0
recCurrent = 0

ser = serial.Serial( '/dev/rfcomm0', 9600 )
ser.flushInput()
ser.flushOutput()

while True:
    stdscr = curses.initscr() #init curses
    curses.cbreak() #react on keys instantly without Enter
    curses.noecho() #turn off echoing of keys to the screen
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

    stdscr.keypad(1) #returning a special value such as curses.KEY_LEFT
    stdscr.nodelay(1)

    input = stdscr.getch()

    if input == 27 or input == ord('q'):
        stdscr.keypad(0)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        exit(0)

    elif input == 10:
        executeMenuCommand( activeEntry )

    elif input == 261:
        activeEntry = activeEntry + 1

    elif input == 260:
        activeEntry = activeEntry - 1

    elif input == 258:
        executeMenuCommand( activeEntry, -1 )

    elif input == 259:
        executeMenuCommand( activeEntry, 1 )

    elif input != -1:
        stdscr.addstr( "\n" )
        stdscr.addstr( "Unknown Key: {:04}".format(input) )

    if activeEntry > len(menuEntriesTemplate)-1:
        activeEntry = 0
    if activeEntry < 0:
        activeEntry = len(menuEntriesTemplate)-1
        
    stdscr.move(1,0)
    readData()
