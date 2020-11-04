# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 10:31:13 2020

@author: Alberto
"""


from serial import Serial 

with Serial('COM29', baudrate = 1500000, timeout = 1) as ser:
    ser.set_buffer_size(rx_size = 100_000, tx_size = 100_000)
    with open("datosUSB.txt" , "w") as dataFile:

        while 1:
            
            usbData = ser.read(4)
            s=' '.join(f'0x{bytes:x}' for bytes in usbData)
            dataFile.write(s+'\n')
            
            print(s)