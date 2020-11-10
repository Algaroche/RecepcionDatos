# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 10:31:13 2020

@author: Alberto
"""


# from serial import Serial 

# with Serial('COM31', baudrate = 1500000, timeout = 1) as ser:
#     ser.set_buffer_size(rx_size = 100_000, tx_size = 100_000)
#     with open("datosUSB.txt" , "w") as dataFile:

#         while 1:
            
#             usbData = ser.read(10)
#             s=' '.join(f'0x{bytes:x}' for bytes in usbData)
#             dataFile.write(s+'\n')
            
#             print(s)

#https://realpython.com/intro-to-python-threading/


from serial import Serial
import concurrent.futures
import logging
import queue
import random
import threading
import time

def sincronizarInicio(ser, queue, tamañoTrama, bitInicioTrama):
    inicio = 0
    while not inicio:   #busco el inicio de la trama que siempre empieza con 0x3e
        usbData = ser.read(1)
        if (usbData == b'\x3e'): 
            inicio = 1; 
            logging.info("INICIO INICIO INICIO INICIO INICIO INICIO")
            usbData = ser.read(tamañoTrama - bitInicioTrama)
            message = "0x3e,"+','.join(f'0x{bytes:x}' for bytes in usbData)
            logging.info("Producer got message: %s", message)
            queue.put(message)
            return(1)
        # else:
        #     tamañoTrama = int.from_bytes(usbData, 'big') - 0x30

def procesadoTramaMotores(datos):
    logging.info("Procesando")
    separados = datos.split(",")
    datosBinarios = ""
    message = ""
    for bytes in separados:
        datosBinarios += bytes[2:4]
    datosBinarios = bin(int(datosBinarios,16))[2:]
    logging.info("Bytes separados")
    #Trama motores: 6 +12+12+12+ 4 +4+4+1+1+1+1+1+1+2+8
    message = datosBinarios[6 :18] #12
    message += "," + datosBinarios[18:30] #12 
    message += "," + datosBinarios[30:42] #12 
    message += "," + datosBinarios[46:50] #4+ 4 
    message += "," + datosBinarios[50:54] #4
    message += "," + datosBinarios[54:55] #1
    message += "," + datosBinarios[55:56] #1
    message += "," + datosBinarios[56:57] #1
    message += "," + datosBinarios[57:58] #1
    message += "," + datosBinarios[58:59] #1
    message += "," + datosBinarios[59:60] #1
    message += "," + datosBinarios[62:70] #2+ 8
    return(message)

def producer(queue, event, ser, tamañoTrama, bitInicioTrama):
    """Pretend we're getting a number from the network."""
    try:
        sincronizado = 0
        while not event.is_set():
            if (not sincronizado):
                sincronizado = sincronizarInicio(ser, queue, tamañoTrama, bitInicioTrama)
            usbData = ser.read(tamañoTrama)
            message = ','.join(f'0x{bytes:x}' for bytes in usbData)
            logging.info("Producer got message: %s", message)
            queue.put(message)
    
        logging.info("Producer received event. Exiting")
        
    except Exception as e:
        print(e)
        

def consumer(queue, event, txt_file):
    """Pretend we're saving a number in the database."""
    while not event.is_set() or not queue.empty():
        message = queue.get()
        txt_file.write(procesadoTramaMotores(message)+'\n')
        logging.info(
            "Consumer storing message: %s (size=%d)", message, queue.qsize()
        )

    logging.info("Consumer received event. Exiting")

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    tamañoTramaCOM31 = 9           #tamaño de la trama que envío yo por el USB de tamaño arbitrario
    bitInicioTramaCOM31 = 1
    colaCOM = queue.Queue(maxsize=10)
    event = threading.Event() 
    with Serial('COM31', baudrate = 1_500_000, timeout = 1) as puerto_serie31:
          puerto_serie31.set_buffer_size(rx_size = 100_000, tx_size = 100_000)
          with open("datosUSB.csv" , "w") as dataFile:
              with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                executor.submit(producer, colaCOM, event, puerto_serie31, tamañoTramaCOM31, bitInicioTramaCOM31)
                executor.submit(consumer, colaCOM, event, dataFile)
        
                time.sleep(10)
                logging.info("Main: about to set event")
                event.set()