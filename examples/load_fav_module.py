#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import mk312


def main():
    # Create a basic logger
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    try:
        # Create the communication wrapper
        et312 = mk312.MK312CommunicationWrapper(device='/dev/cu.usbserial-ftE23GYE')

        # Do an handshake
        et312.handshake()

        # Load the favorite mode
        et312.loadFavoriteMode()

        # Get the current selected mode
        current_mode = et312.readaddress(address=0x407b)
        print('Current mode: 0x%0.2X' % current_mode)

        # Reset key and close the interface
        et312.resetkey()
        et312.closeserialport()
    except Exception as e:
        logging.error('Exception: %s Error message: %s' % (e.__class__.__name__, e.message))


if __name__ == "__main__":
    main()
