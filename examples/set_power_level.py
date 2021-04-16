#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from time import sleep
import mk312
from mk312.constants import POWERLEVEL_LOW, POWERLEVEL_NORMAL, POWERLEVEL_HIGH


def main():
    # Create a basic logger
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    try:
        # Create the communication wrapper
        my312 = mk312.MK312CommunicationWrapper(device='/dev/ttyUSB0')

        # Do an handshake
        my312.handshake()

        # Set the power level to low
        my312.powerLevelSet(powerlevel=POWERLEVEL_LOW)
        sleep(2.0)

        # Set the power level to normal
        my312.powerLevelSet(powerlevel=POWERLEVEL_NORMAL)
        sleep(2.0)

        # Set the power level to high
        my312.powerLevelSet(powerlevel=POWERLEVEL_HIGH)
        sleep(2.0)
    except Exception as e:
        logging.error('Exception: %s.' % e)
    finally:
        # Close the connection
        my312.close()


if __name__ == "__main__":
    main()
