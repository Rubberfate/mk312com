# -*- coding: utf-8 -*-

"""
     __  __ _  _______ _ ____   ____ ___  __  __
    |  \/  | |/ /___ // |___ \ / ___/ _ \|  \/  |
    | |\/| | ' /  |_ \| | __) | |  | | | | |\/| |
    | |  | | . \ ___) | |/ __/| |__| |_| | |  | |
    |_|  |_|_|\_\____/|_|_____|\____\___/|_|  |_|

    This is a simple implementation of controlling an MK312-BT via the RS232 interface.

    :copyright: © 2021 Rubberfate.
    :license: MIT, see LICENSE for more details.
"""

from .__version__ import __title__, __description__, __url__, __version__
from .__version__ import __author__, __author_email__, __license__, __copyright__

from .com import MK312CommunicationWrapper
from .exceptions import MK312ReceivingLengthException, MK312ChecksumException, MK312WriteDataValueException, \
    MK312HandshakeException

__all__ = ['MK312CommunicationWrapper', 'MK312ReceivingLengthException', 'MK312ChecksumException',
           'MK312WriteDataValueException', 'MK312HandshakeException']
