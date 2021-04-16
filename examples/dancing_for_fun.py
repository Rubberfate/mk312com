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
        my312 = mk312.MK312CommunicationWrapper(device='/dev/ttyUSB0')

        # Do an handshake
        my312.handshake()

        # Disable the ADC
        my312.adcDisable()

        # Load intense module
        my312.modeSwitch(mode=MODE_INTENSE)

        # Set power level
        my312.powerLevelSet(powerlevel=POWERLEVEL_HIGH)

        # Get the possible values of multi adjust
        ma_min, ma_max = my312.levelMAGetMinMaxValue()
        logging.info('MA min: 0x%0.2X MA max: 0x%0.2X' % (ma_min, ma_max))
        # Get the actual multi adjus level
        ma_level = my312.levelMAGet()
        logging.info('MA level: 0x%0.2X' % ma_level)

        # Do some fun
        my312.levelMASet(level=128)
        my312.levelASet(level=128)
        my312.levelAGet()
        my312.levelBSet(level=64)
        my312.levelBGet()
        sleep(5.0)
        my312.levelMASet(level=255)
        my312.levelASet(level=255)
        my312.levelBSet(level=128)
        sleep(5.0)
        my312.levelMASet(level=9)
        my312.levelASet(level=0)
        my312.levelBSet(level=0)
        sleep(5.0)

        # Enable the ADC
        my312.adcEnable()
    except Exception as e:
        logging.error('Exception: %s.' % e)
    finally:
        # Close the connection
        my312.close()


if __name__ == "__main__":
    main()
