# -*- coding: utf-8 -*-

"""
     __  __ _  _______ _ ____   ____ ___  __  __
    |  \/  | |/ /___ // |___ \ / ___/ _ \|  \/  |
    | |\/| | ' /  |_ \| | __) | |  | | | | |\/| |
    | |  | | . \ ___) | |/ __/| |__| |_| | |  | |
    |_|  |_|_|\_\____/|_|_____|\____\___/|_|  |_|

    This is a simple implementation of controlling an MK312-BT via the RS232 interface.

    :copyright: © 2020 Rubberfate.
    :license: MIT, see LICENSE for more details.
"""

from .__version__ import __title__, __description__, __url__, __version__
from .__version__ import __author__, __author_email__, __license__, __copyright__

from .com import MK312CommunicationWrapper
from .exceptions import MK312COMInterfaceException, MK312COMWriteDataValueException, MK312COMChecksumException, \
    MK312COMReceivingLengthException, MK312COMHandshakeException
from .constants import MODE_POWERON, MODE_UNKNOWN, MODE_WAVES, MODE_STROKE, MODE_CLIMB, MODE_COMBO, MODE_INTENSE, \
    MODE_RYTHM, MODE_AUDIO1, MODE_AUDIO2, MODE_AUDIO3, MODE_SPLIT, MODE_RANDOM1, MODE_RANDOM2, MODE_TOGGLE, \
    MODE_ORGASM, MODE_TORMENT, MODE_PHASE1, MODE_PHASE2, MODE_PHASE3, MODE_USER1, MODE_USER2, MODE_USER3, MODE_USER4, \
    MODE_USER5, MODE_USER6, MODE_USER7
from .constants import POWERLEVEL_LOW, POWERLEVEL_NORMAL, POWERLEVEL_HIGH

__all__ = ['MK312CommunicationWrapper', 'MK312COMInterfaceException', 'MK312COMWriteDataValueException',
           'MK312COMChecksumException', 'MK312COMReceivingLengthException', 'MK312COMHandshakeException']
