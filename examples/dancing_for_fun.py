#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from time import sleep
import mk312
from mk312.constants import MODE_INTENSE
from mk312.constants import POWERLEVEL_HIGH


def main():
    # Create a basic logger
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    try:
        # Create the communication wrapper
        et312 = mk312.MK312CommunicationWrapper(device='/dev/cu.usbserial-ftE23GYE')

        # Do an handshake
        et312.handshake()

        # Disable the ADC
        et312.disableADC()

        # Load intense module
        et312.loadMode(mode=MODE_INTENSE)

        # Set power level
        et312.setPowerLevel(powerlevel=POWERLEVEL_HIGH)

        ma_min, ma_max = et312.getMinMaxValueMA()
        logging.info('MA min: 0x%0.2X MA max: 0x%0.2X' % (ma_min, ma_max))

        ma_level = et312.getLevelMA()
        logging.info('MA level: 0x%0.2X' % ma_level)

        # Set Level of A
        et312.setLevelMA(level=128)
        et312.setLevelA(level=128)
        et312.getLevelA()
        et312.setLevelB(level=64)
        et312.getLevelB()
        sleep(5.0)
        et312.setLevelMA(level=255)
        et312.setLevelA(level=255)
        et312.setLevelB(level=128)
        sleep(5.0)
        et312.setLevelMA(level=9)
        et312.setLevelA(level=0)
        et312.setLevelB(level=0)

        # Enable the ADC
        et312.enableADC()

        # Reset key and close the interface
        et312.resetkey()
        et312.closeserialport()
    except Exception as e:
        logging.error('Exception: %s Error message: %s' % (e.__class__.__name__, e.message))


if __name__ == "__main__":
    main()
