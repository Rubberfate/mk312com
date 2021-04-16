#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import mk312
from mk312.constants import ADDRESS_CURRENT_MODE


def main():
    # Create a basic logger
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    try:
        # Create the communication wrapper
        my312 = mk312.MK312CommunicationWrapper(device='/dev/ttyUSB0')

        # Do an handshake
        my312.handshake()

        # Load the favorite mode
        my312.favoriteModeLoad()

        # Get the current selected mode
        current_mode = my312.readaddress(address=mk312.constants.ADDRESS_CURRENT_MODE)
        print('Current mode: 0x%0.2X' % current_mode)
    except Exception as e:
        logging.error('Exception: %s.' % e)
    finally:
        # Close the connection
        my312.close()


if __name__ == "__main__":
    main()
