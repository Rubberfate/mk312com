#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('/home/andreas/Nextcloud/Andreas/Projects/mk312com')

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
        my312 = mk312.MK312CommunicationWrapper(device='/dev/cu.usbserial-ftE23GYE')

        # Do an handshake
        my312.handshake()

        # Disable the ADC
        my312.disableADC()

        # Load intense module
        my312.loadMode(mode=MODE_INTENSE)

        # Set power level
        my312.setPowerLevel(powerlevel=POWERLEVEL_HIGH)

        # Get the possible values of multi adjust
        ma_min, ma_max = my312.getMinMaxValueMA()
        logging.info('MA min: 0x%0.2X MA max: 0x%0.2X' % (ma_min, ma_max))
        # Get the actual multi adjus level
        ma_level = my312.getLevelMA()
        logging.info('MA level: 0x%0.2X' % ma_level)

        # Do some fun
        my312.setLevelMA(level=128)
        my312.setLevelA(level=128)
        my312.getLevelA()
        my312.setLevelB(level=64)
        my312.getLevelB()
        sleep(5.0)
        my312.setLevelMA(level=255)
        my312.setLevelA(level=255)
        my312.setLevelB(level=128)
        sleep(5.0)
        my312.setLevelMA(level=9)
        my312.setLevelA(level=0)
        my312.setLevelB(level=0)

        # Enable the ADC
        my312.enableADC()
    except Exception as e:
        logging.error('Exception: %s.' % e)
    finally:
        # Reset the key
        my312.resetkey()
        my312.closeserialport()


if __name__ == "__main__":
    main()
