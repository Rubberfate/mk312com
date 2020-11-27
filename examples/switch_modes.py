#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from time import sleep
import mk312


def main():
    # Create a basic logger
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    try:
        # Create the communication wrapper
        et312 = mk312.MK312CommunicationWrapper(device='/dev/cu.usbserial-ftE23GYE')

        # Do an handshake
        et312.handshake()

        # Switch the modes
        for mode in range(mk312.MODE_WAVES, mk312.MODE_USER7, 1):
            et312.loadMode(mode=mode)
            sleep(4.0)

        # Reset key and close the interface
        et312.resetkey()
        et312.closeserialport()
    except Exception as e:
        logging.error('Exception: %s Error message: %s' % (e.__class__.__name__, e.message))


if __name__ == "__main__":
    main()
