# -*- coding: utf-8 -*-


class MK312COMInterfaceException(Exception):
    '''
    Exception at opening the interface.
    '''

    def __init__(self, message):
        self.message = message


class MK312COMReceivingLengthException(Exception):
    '''
    Length exception during answering (the bytes that we received are not the length that we expect).
    '''

    def __init__(self, message):
        self.message = message


class MK312COMChecksumException(Exception):
    '''
    The checksum of the received data is not correct.
    '''

    def __init__(self, message):
        self.message = message


class MK312COMWriteDataValueException(Exception):
    '''
    The value of the data which should be write is wrong.
    '''

    def __init__(self, message):
        self.message = message


class MK312COMHandshakeException(Exception):
    '''
    There is an exception during handshaking.
    '''

    def __init__(self, message):
        self.message = message
