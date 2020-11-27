# -*- coding: utf-8 -*-

import serial
from time import sleep
import logging
from .exceptions import MK312COMInterfaceException, MK312COMChecksumException, MK312COMReceivingLengthException, \
    MK312COMWriteDataValueException, MK312COMHandshakeException
from .constants import ADDRESS_COMMAND_1, ADDRESS_CURRENT_MODE, ADDRESS_POWER_LEVEL, ADDRESS_R15, ADDRESS_LEVELA, \
    ADDRESS_LEVELB, ADDRESS_MA_MAX_VALUE, ADDRESS_MA_MIN_VALUE, ADDRESS_LEVELMA
from .constants import COMMAND_START_FAVORITE_MODULE, COMMAND_EXIT_MENU, COMMAND_NEW_MODE
from .constants import MODE_WAVES
from .constants import POWERLEVEL_NORMAL
from .constants import REGISTER_15_ADCDISABLE
from .utils import bytes_to_hex_str


# Logging for the module
log = logging.getLogger(__name__)


class MK312CommunicationWrapper(object):
    def __init__(self, device: str = '/dev/cu.usbserial', baudrate: int = 19200, timeout: float = 2.0,
                 key: int = None):
        '''
        Init the communication wrapper with some settings for the serial port which the MK312 is connected to.
        :param device: RS232-USB converter or directly accessible RS232 interface.
        :param baudrate: The baudrate is normally 19200 baud.
        :param timeout: The timeout for the serial communication.
        :param key: You can specify an encryption key for the communication.
        '''

        self.device = device
        log.debug('Use serial port: %s' % self.device)
        self.baudrate = baudrate
        log.debug('Baudrate: %i' % self.baudrate)
        self.timeout = timeout
        log.debug('Timeout: %f' % self.timeout)
        self.key = key
        if self.key is not None:
            log.debug('Key: 0x%0.2X' % self.key)
        self._openserialport()

    def _openserialport(self):
        '''
        We are trying to open the interface.
        :return: True if open.
        '''

        try:
            # Opening the serial port
            self.port = serial.Serial(self.device, baudrate=self.baudrate, bytesize=serial.EIGHTBITS,
                                      parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=self.timeout,
                                      xonxoff=serial.XOFF, rtscts=False)
            if self.port.is_open:
                # Closing the serial port if it is already open and use the properties above for reopen
                log.debug('Serial port is already open - closing it and reopen using the settings for MK-312.')
                self.port.close()
            self.port.open()

            # Be sure that we opened the interface
            if self.port.isOpen:
                log.debug('Serial port opened successful.')
                return True
            else:
                log.error('')
                raise MK312COMInterfaceException(message='Can\'t open interface: %s' % self.device)
        except Exception as e:
            raise e

    def readaddress(self, address: int = 0x00fd):
        '''
        Read data from the MK-312.
        :param address: The address (int) from which we like to read.
        :return: The content of the address as int value.
        '''

        log.debug('Reading address: 0x%0.2X' % address)

        # Create the address data for sending to the MK312
        send_data = [0x3c, address >> 8, address & 0xff]

        # Creating a checksum
        checksum = sum(send_data) % 256

        # Append the checksum to data
        send_data.append(checksum)
        log.debug('Sending data: %s' % bytes_to_hex_str(send_data))

        # Encrypt if the key is not None
        if self.key:
            send_data = [x ^ self.key for x in send_data]
            log.debug('Sending encrypted data: %s' % bytes_to_hex_str(send_data))

        # Send the data
        self.port.write(bytes(send_data))

        # Get the data from the reading command (3 bytes)
        read_data = self.port.read(3)
        log.debug('Reading data: %s' % bytes_to_hex_str(read_data))

        if len(read_data) is not 3:
            raise MK312COMReceivingLengthException(message='Not all data received.')

        # Get the checksum from the received data
        checksum = read_data[-1]
        log.debug('Checksum of read data: 0x%0.2X' % checksum)
        s = sum(read_data[:-1]) % 256
        if s != checksum:
            raise MK312COMChecksumException(message='Checksum of read data is incorrect: 0x%0.2X != 0x%0.2X' % (checksum, s))

        # Return the data
        log.debug('Address: 0x%0.2X content: 0x%0.2X' % (address, read_data[1]))
        return read_data[1]

    def closeserialport(self):
        '''
        Closing the serial port.
        :return: True if it was open.
        '''
        if self.port.is_open:
            log.debug('Closing the serial port.')
            self.port.close()
            return True
        else:
            log.debug('Serial port was not open.')

    def writedata(self, address: int = 0x4080, data: int = 0x00):
        '''
        Writing data to the given address.
        :param address: The address (int) from which we like to read.
        :param data: The data (int) for writing into the address.
        :return: True if the data was send and confirmed by the MK-312.
        '''

        log.debug('Writing data: 0x%0.2X to address: 0x%0.2X' % (data, address))

        # Check if the int value is between 0 and 255
        if data < 0x00 or data > 0xff:
            raise MK312COMWriteDataValueException(message='Wrong data value: It should be between 0x00 and 0xff.')

        # Build the data
        send_data = [((0x3 + 1) << 0x4) | 0xd, address >> 8, address & 0xff, data]

        # Create the checksum and append it
        checksum = sum(send_data) % 256
        send_data.append(checksum)
        log.debug('Sending data: %s' % bytes_to_hex_str(send_data))

        # Only encrypt if we have a key
        if self.key:
            send_data = [x ^ self.key for x in send_data]
            log.debug('Sending encrypted data: %s' % bytes_to_hex_str(send_data))

        # Send the data
        self.port.write(bytes(send_data))

        # Read the response
        read_data = self.port.read(1)
        log.debug('Reading data: %s' % bytes_to_hex_str(read_data))

        # If the write operation was successful, we can read back 0x06 from the device
        if read_data[0] is not 0x06:
            return False
            # TODO: Is this case worth of an exception?
        else:
            return True

    def resetkey(self):
        '''
        Reset the key to 0x00.
        '''

        log.debug('Resetting key to 0x00.')
        self.writedata(0x4213, 0x00)

    def handshake(self):
        '''
        Do a handshake with the MK-312.
        '''

        log.debug('Handshaking.')

        # Data for sending
        send_data = bytes([0])

        # If we have a key then use it
        if self.key is not None:
            send_data = [x ^ self.key for x in send_data]

        # Try to
        for i in range(4):
            log.debug('Sending data: %s' % bytes_to_hex_str(send_data))
            self.port.write(send_data)

            read_data = self.port.read(1)
            log.debug('Reading data: %s' % bytes_to_hex_str(read_data))

            if len(read_data) == 0:
                # Trying it again
                continue
            if read_data[0] != 0x7:
                # Reading no handshake
                raise MK312COMHandshakeException(message='Received handshake is not 0x07: 0x%0.2X' % read_data[0])
                #self.handshake()
            else:
                break
        if len(read_data) == 0:
            raise MK312COMHandshakeException(message='No data received.')

        # If we already have a key
        #if self.key is not None:
        #    return

        # Sending a key
        send_data = [0x2f, 0x00]
        checksum = sum(send_data) % 256
        send_data.append(checksum)

        # Only encrypt if we have a key
        if self.key:
            send_data = [x ^ self.key for x in send_data]
        self.port.write(bytes(send_data))
        log.debug('Sending data: %s' % bytes_to_hex_str(send_data))

        read_data = self.port.read(3)
        log.debug('Reading data: %s' % bytes_to_hex_str(read_data))

        if len(read_data) is 0:
            raise MK312COMHandshakeException(message='No data received after sending a key.')

        # Test checksum
        checksum = read_data[-1]
        s = sum(read_data[:-1]) % 256
        if s != checksum:
            raise MK312COMHandshakeException(message='Checksum is wrong: 0x%0.2X != 0x%0.2X' % (s, checksum))

        if read_data[0] != 0x21:
            raise MK312COMHandshakeException(message='Received hadnshake is not 0x21: 0x%0.2X' % read_data[0])

        # Key generation: 0x55 ^ their_key
        self.key = 0x55 ^ read_data[1]
        log.debug('Handshake successful key is now: 0x%0.2X' % self.key)

    def loadFavoriteMode(self):
        '''
        Load the favorite module.
        '''

        log.debug('Loading the favorite module.')
        # Check if we have a key
        if self.key is None:
            self.handshake()

        return self.writedata(address=ADDRESS_COMMAND_1, data=COMMAND_START_FAVORITE_MODULE)

    def loadMode(self, mode: int = MODE_WAVES):
        '''
        Switch the actual mode.
        '''

        log.debug('Loading mode: 0x%0.2X' % mode)

        # Check if we have a key
        if self.key is None:
            self.handshake()

        # Switch the mode
        if not self.writedata(address=ADDRESS_CURRENT_MODE, data=mode):
            log.debug('Mode switching is not working!')
            return False
        sleep(0.1)

        # Refresh LCD
        if not self.writedata(address=ADDRESS_COMMAND_1, data=COMMAND_EXIT_MENU):
            log.debug('Refreshing the LCD is not working!')
            return False
        sleep(0.1)

        # Select new mode
        if not self.writedata(address=ADDRESS_COMMAND_1, data=COMMAND_NEW_MODE):
            log.debug('New mode is not working!')
            return False
        sleep(0.1)

        # Read back the mode for proving it
        if mode is self.readaddress(address=ADDRESS_CURRENT_MODE):
            return True
        else:
            log.debug('New mode is not switched!')
            return False

    def setPowerLevel(self, powerlevel: int = POWERLEVEL_NORMAL):
        '''
        Change the power level.
        '''

        log.debug('Change power level: 0x%0.2X' % powerlevel)

        # Check if we have a key
        if self.key is None:
            self.handshake()

        # Switch the power level
        if not self.writedata(address=ADDRESS_POWER_LEVEL, data=powerlevel):
            log.debug('Power level changing is not working!')
            return False
        sleep(0.1)

        # Read back the mode for proving it
        if powerlevel is self.readaddress(address=ADDRESS_POWER_LEVEL):
            return True
        else:
            log.debug('New power level is not active!')
            return False

    def disableADC(self):
        '''
        Disable ADC --> The potentiometers at the front are disabled so you can not control the device anymore!
        '''

        log.debug('Disable the ADC!')

        # Read R15 from device
        register15 = self.readaddress(address=ADDRESS_R15)
        log.debug('Value of R15 is: 0x%0.2X' % register15)

        # Set bit 0 to True
        register15 = register15 | (1 << REGISTER_15_ADCDISABLE)
        log.debug('Switching ADC off: 0x%0.2X' % register15)

        if self.writedata(address=ADDRESS_R15, data=register15):
            return True
        else:
            return False

    def enableADC(self):
        '''
        Enable ADC --> You get control over the potentiometers.
        '''

        log.debug('Enable the ADC!')

        # Read R15 from device
        register15 = self.readaddress(address=ADDRESS_R15)
        log.debug('Value of R15 is: 0x%0.2X' % register15)

        # Set bit 0 to False
        register15 = register15 & ~(1 << REGISTER_15_ADCDISABLE)
        log.debug('Switching ADC on: 0x%0.2X' % register15)

        if self.writedata(address=ADDRESS_R15, data=register15):
            return True
        else:
            return False

    def setLevelA(self, level: int = 0x00):
        '''
        Set the Level A if the ADC is disabled.
        '''

        # TODO: Check if the ADC is disabled!
        log.debug('Set level A to: 0x%0.2X' % level)

        # Check if the int value is between 0 and 255
        if level < 0x00 or level > 0xff:
            log.debug('Level needs to be between 0x00 and 0xff! -> Can not set Level A to: 0x%0.2X' % level)
            return False

        # Write it
        if self.writedata(address=ADDRESS_LEVELA, data=level):
            read_levela = self.readaddress(address=ADDRESS_LEVELA)
            if read_levela is level:
                log.debug('Level A is set to: 0x%0.2X' % read_levela)
                return True
            else:
                return False
        else:
            return False

    def getLevelA(self):
        '''
        Get Level A.
        '''

        log.debug('Get Level A.')

        read_levela = self.readaddress(address=ADDRESS_LEVELA)
        log.debug('Level A is set to: 0x%0.2X' % read_levela)
        return read_levela

    def setLevelB(self, level: int = 0x00):
        '''
        Set the Level B if the ADC is disabled.
        '''

        # TODO: Check if the ADC is disabled!
        log.debug('Set level B to: 0x%0.2X' % level)

        # Check if the int value is between 0 and 255
        if level < 0x00 or level > 0xff:
            log.debug('Level needs to be between 0x00 and 0xff! -> Can not set Level B to: 0x%0.2X' % level)
            return False

        # Write it
        if self.writedata(address=ADDRESS_LEVELB, data=level):
            read_levelb = self.readaddress(address=ADDRESS_LEVELB)
            if read_levelb is level:
                log.debug('Level B is set to: 0x%0.2X' % read_levelb)
                return True
            else:
                return False
        else:
            return False

    def getLevelB(self):
        '''
        Get Level B.
        '''

        log.debug('Get Level B.')

        read_levelb = self.readaddress(address=ADDRESS_LEVELB)
        log.debug('Level B is set to: 0x%0.2X' % read_levelb)
        return read_levelb

    def setLevelMA(self, level: int = 0x00):
        '''
        Set the Level MA if the ADC is disabled.
        '''

        # TODO: Check if the ADC is disabled!
        log.debug('Set level MA to: 0x%0.2X' % level)

        # Check if the int value is between min MA and max ma
        read_min_ma, read_max_ma = self.getMinMaxValueMA()

        if level < read_min_ma or level > read_max_ma:
            log.debug('MA Level needs to be between 0x%0.2X and 0x%0.2X! -> Can not set MA Level to: 0x%0.2X' %
                      (read_min_ma, read_max_ma, level))
            return False

        # Write it
        if self.writedata(address=ADDRESS_LEVELMA, data=level):
            read_levelma = self.readaddress(address=ADDRESS_LEVELMA)
            if read_levelma is level:
                log.debug('MA Level is set to: 0x%0.2X' % read_levelma)
                return True
            else:
                return False
        else:
            return False

    def getMinMaxValueMA(self):
        '''
        Get the possible minimal and maximal value of the multi adjust.
        Please note that the minimal level is not necessarily the minimal value and vice versa.
        '''

        # TODO: Store the minimal and maximal levels in the object self.mamax and self.mamin
        #  fill the data if new mode is selected
        log.debug('Get the minimal and maximal multi adjust values.')

        read_min_ma = self.readaddress(address=ADDRESS_MA_MIN_VALUE)
        log.debug('MA minimal value is: 0x%0.2X' % read_min_ma)
        read_max_ma = self.readaddress(address=ADDRESS_MA_MAX_VALUE)
        log.debug('MA maximal value is: 0x%0.2X' % read_max_ma)

        return read_min_ma, read_max_ma

    def getLevelMA(self):
        '''
        Get the multi adjust level.
        '''

        log.debug('Get multi adjust level.')

        read_levelma = self.readaddress(address=ADDRESS_LEVELMA)
        log.debug('Level MA is set to: 0x%0.2X' % read_levelma)
        return read_levelma
