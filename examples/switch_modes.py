#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from time import sleep
import mk312
from mk312.constants import MODE_WAVES, MODE_USER7


def main():
    # Create a basic logger
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    try:
        # Create the communication wrapper
        my312 = mk312.MK312CommunicationWrapper(device='/dev/cu.usbserial-ftE23GYE')

        # Do an handshake
        my312.handshake()

        # Switch the modes
        for mode in range(MODE_WAVES, MODE_USER7, 1):
            my312.loadMode(mode=mode)
            sleep(4.0)

    except Exception as e:
        logging.error('Exception: %s.' % e)
    finally:
        # Reset the key
        my312.resetkey()
        my312.closeserialport()


if __name__ == "__main__":
    main()
