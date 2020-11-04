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
            
#             usbData = ser.read(4)
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

def producer(queue, event):
    """Pretend we're getting a number from the network."""
    while not event.is_set():
        with Serial('COM31', baudrate = 1500000, timeout = 1) as ser:
            ser.set_buffer_size(rx_size = 100_000, tx_size = 100_000)
            
            usbData = ser.read(4)
            message = ' '.join(f'0x{bytes:x}' for bytes in usbData)
            logging.info("Producer got message: %s", message)
            queue.put(message)

    logging.info("Producer received event. Exiting")

def consumer(queue, event):
    """Pretend we're saving a number in the database."""
    while not event.is_set() or not queue.empty():
        message = queue.get()
        with open("datosUSB.txt" , "w") as dataFile:
            dataFile.write(message+'\n')
        logging.info(
            "Consumer storing message: %s (size=%d)", message, queue.qsize()
        )

    logging.info("Consumer received event. Exiting")

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    pipeline = queue.Queue(maxsize=10)
    event = threading.Event()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(producer, pipeline, event)
        executor.submit(consumer, pipeline, event)

        time.sleep(10)
        logging.info("Main: about to set event")
        event.set()