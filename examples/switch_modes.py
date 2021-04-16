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
        my312 = mk312.MK312CommunicationWrapper(device='/dev/ttyUSB0')

        # Do an handshake
        my312.handshake()

        # Switch the modes
        for mode in range(MODE_WAVES, MODE_USER7, 1):
            my312.modeSwitch(mode=mode)
            sleep(4.0)

    except Exception as e:
        logging.error('Exception: %s.' % e)
    finally:
        # Close the connection
        my312.close()


if __name__ == "__main__":
    main()
