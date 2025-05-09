#!/usr/bin/env python3
# StringExample.py
# Version 0.6

while True:
    print()
    print('Input test string from Dynon:', sep=' ', end=' ')
    text = input()
    if text.startswith('!1'):
        print()
        print('Dynon Skyview ADAHRS Serial Data', sep=' ', end='\n\n\n')
        print('ADAHRS Data version: ', text[2:3])
        print('Time:   ', text[3:5], ':', text[5:7], ":", text[7:9], sep='')
        print('Pitch: ', text[11:15], 'deg')
        print('Roll:  ', text[15:20], 'deg')
        print('Heading:', text[20:23], 'deg')
        IAS = float(text[23:27])
        IAS = IAS / 10
        print('IAS:   {0:5.1f}'.format(IAS), 'kts')
        pALT = int(text[27:33])
        print('pALT:    {0:,}'.format(pALT), 'ft')
        print('OAT     ', text[49:52], 'deg C')
        if text[52:56].isnumeric():
            TAS = float(text[52:56])
            TAS = TAS / 10
            print('TAS:    {0:5.1f},'.format(TAS), 'kts')
        elif text[52:56] == 'XXXX':
            print('No TAS')
        else: print('Trash for TAS:    ', text[52:56])
        BARO = float(text[56:59])
        BARO = BARO / 10
        print('BARO:    {0:5.2f}'.format(BARO), 'inHg')
        if text[59:65].isnumeric():
            dALT = int(text[59:65])
            print('dALT:    {0:,}'.format(dALT), 'ft')
        elif text[59:65].startswith('XXXXXX'):
            print('No Density Altitude')
        else: print('Trash for dAlt:   ', text[59:65])
        print()
    elif text.startswith('!2'):
        print()
        print('Dynon Skyview System Serial Data')
        print('System Data version: ', text[2:3], sep=' ', end='\n\n\n')
    elif text.startswith('!3'):
        print()
        print('Dynon Skkyview EMS Serial Data', sep=' ', end='\n\n\n')
        print('EMS Data version: ', text[2:3])
        if text[44:47].isnumeric():
            fuel_remain = float(text[44:47]) / 10
            print('Fuel Remaining:   ', '{0:4.1f}' .format(fuel_remain))
        if text[47:50].isnumeric():
            battery_1 = int(text[47:50])
            print('Battery-1:        ', '{0:4.1f}' .format(battery_1))
        if text[50:53].isnumeric():
            battery_2 = int(text[50:53])
            print('Battery-2:        ', '{0:4.1f}' .format(battery_2))
        if text[57:62].isnumeric():
            hobbs = float(text[57:62]) / 10
            print('Hobbs:            ' '{0:6.1f}' .format(hobbs))
        else: print('Trash for Hobbs:  ', text[57:62])
        if text[130:134].isnumeric():
            amps1 = float(text[129:134]) / 100
            print('Battery Amps:   ', '{0:6.1f}' .format(amps1), 'Amps')
        else: print('Trash for Battery Amps:', text[129:135])
        if text[136:140].isnumeric():
            amps2 = float(text[135:140]) / 100
            print('Alternator Amps:', '{0:6.1f}' .format(amps2), 'Amps')
        else: print('Trash for Alternator Amps:', text[135:141])
        if text[142:146].isnumeric():
            smoke = float(text[142:146])
            smoke = smoke / 10
            if text[146:147] != 'G': print('Expecting a "G" for "Gallons":', text[146:147])
            print('Smoke Level:        ' '{0:3.1f}'.format(smoke), 'Gallons')
        else: print('Trash for Smoke Level:', text[141:147])
        if text[153:158].isnumeric():
            flap_position = int(text[153:158])
            print('Flaps at: {0:,}' .format(flap_position), 'Percent Down')
        else: print('Trash for Flaps:   ', text[153:158])
        print('Expecting a "T" for "Percent":', text[158:159])
        print()
    else:
        print(text)


