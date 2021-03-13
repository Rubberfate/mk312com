# -*- coding: utf-8 -*-

class MK312ReceivingLengthException(Exception):
    """
    Length exception during answering (the bytes that we received are not the length that we expect).
    """
    pass


class MK312ChecksumException(Exception):
    """
    The checksum of the received data is not correct.
    """
    pass


class MK312WriteDataValueException(Exception):
    """
    The value of the data which should be write is wrong.
    """
    pass


class MK312HandshakeException(Exception):
    """
    There is an exception during handshaking.
    """

    pass
