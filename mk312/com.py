# -*- coding: utf-8 -*-

import serial
from time import sleep
import logging
from .exceptions import MK312ReceivingLengthException, MK312ChecksumException, MK312WriteDataValueException, \
    MK312HandshakeException
from .constants import ADDRESS_COMMAND_1, ADDRESS_CURRENT_MODE, ADDRESS_POWER_LEVEL, ADDRESS_R15, ADDRESS_LEVELA, \
    ADDRESS_LEVELB, ADDRESS_MA_MAX_VALUE, ADDRESS_MA_MIN_VALUE, ADDRESS_LEVELMA, ADDRESS_KEY
from .constants import EEPROM_ADDRESS_POWER_LEVEL, EEPROM_ADDRESS_FAVORITE_MODE
from .constants import COMMAND_START_FAVORITE_MODULE, COMMAND_SHOW_STATUS_SCREEN, COMMAND_SELECT_MENU_ITEM, \
    COMMAND_EXIT_MENU, COMMAND_NEW_MODE
from .constants import MODE_WAVES
from .constants import POWERLEVEL_NORMAL
from .constants import REGISTER_15_ADCDISABLE
from .utils import bytes_to_hex_str


# Logging for the module
log = logging.getLogger(__name__)


class MK312CommunicationWrapper(object):
    """
    The Communication Wrapper for using a MK-312 box.
    """

    def __init__(self,
                 device: str = '/dev/cu.usbserial',
                 baudrate: int = 19200,
                 timeout: float = 0.5,
                 key: int = None,
                 handshake_repeat: int = 10):
        """
        Init the communication wrapper with some settings for the serial port which the MK312 is connected to.
        :param device: RS232-USB converter or directly accessible RS232 interface.
        :param baudrate: The baudrate is normally 19200 baud.
        :param timeout: The timeout for the serial communication.
        :param key: You can specify an encryption key for the communication.
        :param handshake_repeat: How often do we try to wait for the handshake of the device.
        """

        self.device = device
        log.debug('Use serial port: %s' % self.device)
        self.baudrate = baudrate
        log.debug('Baudrate: %i' % self.baudrate)
        self.timeout = timeout
        log.debug('Timeout: %f' % self.timeout)
        self.key = key
        if self.key is not None:
            log.debug('Key: 0x%0.2X' % self.key)
        self.handshake_repeat = handshake_repeat
        self.__openserialport()

    def __openserialport(self):
        """
        We are trying to open the interface.
        :return: True if open, else it throws an exception.
        """

        try:
            # Opening the serial port
            self.port = serial.Serial(self.device,
                                      baudrate=self.baudrate,
                                      bytesize=serial.EIGHTBITS,
                                      parity=serial.PARITY_NONE,
                                      stopbits=serial.STOPBITS_ONE,
                                      timeout=self.timeout,
                                      xonxoff=serial.XOFF,
                                      rtscts=False)
            if self.port.is_open:
                # Closing the serial port if it is already open and use the properties above for reopen
                log.debug('Serial port is already open - closing it and reopen using the settings for MK-312.')
                self.port.close()
            self.port.open()

            # Be sure that we opened the interface
            if self.port.isOpen:
                log.debug('Serial port opened successful.')
                return True
        except Exception as e:
            raise e

    def close(self):
        """
        Closing the serial port and reset the key.
        :return: True if it was open.
        """

        log.debug('Closing the communication.')

        # Reset the key
        self.__resetkey()

        if self.port.is_open:
            log.debug('Closing the serial port.')
            self.port.close()
            return True
        else:
            log.debug('Serial port was not open.')

    def handshake(self):
        """
        Do a handshake with the MK-312.
        :return: True if the handshake was successful.
        """

        log.debug('Handshaking.')

        # Data for sending
        send_data = bytes([0])

        # We are trying to disturb the device as long as self.handshake_repeat is
        handshake_repeat = 0

        while True:
            # If we have a key then use it
            if self.key is not None:
                send_data = [x ^ self.key for x in send_data]

            # Sending 0x00 or the encrypted variant to the device
            log.debug('Sending data: %s [Waiting for handshaking]' % bytes_to_hex_str(send_data))
            self.port.write(send_data)

            # Reading what is going on
            read_data = self.port.read(1)
            log.debug('Reading data: %s [Waiting for handshaking]' % bytes_to_hex_str(read_data))

            # If we can not read data back try to use the default key
            if len(read_data) == 0:
                self.key = 0x55

            # Send as long as we have data and 0x07 -> the device is ready for handshake
            if len(read_data) == 1 and read_data[0] == 0x07:
                # Exiting the while loop
                log.debug('Reading data: %s [Ready for handshaking]' % bytes_to_hex_str(read_data))
                break

            # We are trying as much as we like?
            handshake_repeat += 1
            if handshake_repeat >= self.handshake_repeat:
                raise MK312HandshakeException('Repeating to much times! Restart the device?')

        # We can setup a new key -> Sending a key, actually the key is fixed to 0x00
        send_data = [0x2f, 0x00]
        checksum = sum(send_data) % 256
        send_data.append(checksum)

        # Only encrypt if we have a key (if not, we do not know if the device has one)
        if self.key:
            send_data = [x ^ self.key for x in send_data]
        log.debug('Sending data: %s' % bytes_to_hex_str(send_data))
        self.port.write(bytes(send_data))

        read_data = self.port.read(3)
        log.debug('Reading data: %s' % bytes_to_hex_str(read_data))

        if len(read_data) == 0:
            # Maybe there was a key stored but we do not know it.
            # Normally you have to switch off the device and restart it after a long time.
            # If you do not have used a different key yet we can try to test our default key
            self.key = 0x55
            self.handshake()
        else:
            # Check the checksum from the device
            checksum = read_data[-1]
            s = sum(read_data[:-1]) % 256
            if s != checksum:
                # If the checksum is wrong, redo a handshake
                # raise MK312ChecksumException('Checksum is wrong: 0x%0.2X != 0x%0.2X' % (s, checksum))
                self.handshake()
                return

            # Key generation: 0x55 ^ their_key
            self.key = 0x55 ^ read_data[1]
            log.debug('Handshake successful key is now: 0x%0.2X' % self.key)

            return True

    def __resetkey(self):
        """
        Reset the key to 0x00.
        """

        log.debug('Resetting key to 0x00.')
        log.debug('Actual key in address 0x4213 is: 0x%0.2X' % self.readaddress(ADDRESS_KEY))
        self.writedata(ADDRESS_KEY, 0x00)
        self.key = None

    def readaddress(self, address: int = 0x00fd):
        """
        Read data from the MK-312 of the given address.
        :param address: The address (int) from which we like to read.
        :return: The content of the address as int value / flase if reading failed.
        """

        log.debug('Reading address: 0x%0.2X' % address)

        # Create the address data for sending to the MK312
        send_data = [0x3c, address >> 8, address & 0xff]

        # Creating a checksum
        checksum = sum(send_data) % 256

        # Append the checksum to data
        log.debug('Sending data: %s' % bytes_to_hex_str(send_data))
        send_data.append(checksum)

        # Encrypt if the key is not None
        if self.key:
            send_data = [x ^ self.key for x in send_data]
            log.debug('Sending encrypted data: %s' % bytes_to_hex_str(send_data))

        # Send the data
        self.port.write(bytes(send_data))

        # Get the data from the reading command (3 bytes)
        read_data = self.port.read(3)
        log.debug('Reading data: %s' % bytes_to_hex_str(read_data))

        # We have no data read -> maybe the key is wrong?
        if len(read_data) == 0:
            return False

        if len(read_data) != 3:
            raise MK312ReceivingLengthException('Reading failed getting %i bytes.' % len(read_data))

        # Get the checksum from the received data
        checksum = read_data[-1]
        log.debug('Checksum of read data: 0x%0.2X' % checksum)
        s = sum(read_data[:-1]) % 256
        if s != checksum:
            raise MK312ChecksumException('Checksum of read data is incorrect: 0x%0.2X != 0x%0.2X' % (checksum, s))

        # Return the data
        log.debug('Address: 0x%0.2X content: 0x%0.2X' % (address, read_data[1]))
        return read_data[1]

    def writedata(self, address: int = 0x4080, data: int = 0x00):
        """
        Writing data to the given address.
        :param address: The address (int) from which we like to read.
        :param data: The data (int) for writing into the address.
        :return: True if the data was send and confirmed by the MK-312 / False if not
        """

        log.debug('Writing data: 0x%0.2X to address: 0x%0.2X' % (data, address))

        # Check if the int value is between 0 and 255
        if data < 0x00 or data > 0xff:
            raise MK312WriteDataValueException('Wrong data value: It should be between 0x00 and 0xff.')

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
        if read_data[0] != 0x06:
            return False
            # TODO: Is this case worth of an exception?
        else:
            return True

    def favoriteModeLoad(self):
        """
        Load the favorite mode.
        :return: True if the mode was loaded.
        """

        log.debug('Loading the favorite mode.')

        # Check if we have a key
        if self.key is None:
            self.handshake()

        return self.writedata(address=ADDRESS_COMMAND_1, data=COMMAND_START_FAVORITE_MODULE)

    def favoriteModeRead(self):
        """
        Read the favorite mode from the EEPROM
        :return: The mode which is actually store in the EEPROM.
        """

        log.debug('Reading the favorite mode from the eeprom.')

        # Check if we have a key
        if self.key is None:
            self.handshake()

        return self.readaddress(address=EEPROM_ADDRESS_FAVORITE_MODE)

    def favoriteModeWrite(self, mode: int = MODE_WAVES):
        """
        Write the favorite mode into EEPROM. Please note you have to restart to use this mode as favorite.
        :param mode: The mode for writing.
        :return: True if the mode is written into the EEPROM.
        """

        log.debug('Writing the favorite mode into the eeprom -> 0x%0.2X' % mode)

        # Check if we have a key
        if self.key is None:
            self.handshake()

        # If the mode is actual the favorite one
        if mode == self.readaddress(address=EEPROM_ADDRESS_FAVORITE_MODE):
            return True

        return self.writedata(address=EEPROM_ADDRESS_FAVORITE_MODE, data=mode)

    def modeSwitch(self, mode: int = MODE_WAVES):
        """
        Switch the actual mode.
        :param mode: The mode for loading.
        :return: True or False if the mode is switched.
        """

        log.debug('Switching to mode: 0x%0.2X' % mode)

        # Check if we have a key
        if self.key is None:
            self.handshake()

        # Bail early on loadMode if mode is already selected
        if mode == self.readaddress(address=ADDRESS_CURRENT_MODE):
            return True
        
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
        if mode == self.readaddress(address=ADDRESS_CURRENT_MODE):
            return True
        else:
            log.debug('New mode is not switched!')
            return False

    def powerLevelSet(self, powerlevel: int = POWERLEVEL_NORMAL):
        """
        Change the power level.
        :param powerlevel: The power level to set.
        :return: True or False if the power level is set.
        """

        log.debug('Set the power level: 0x%0.2X' % powerlevel)

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

    def powerLevelRead(self):
        """
        Read the power level from the EEPROM
        :return: The power level which is actually store in the EEPROM.
        """

        log.debug('Reading the power level from the eeprom.')

        # Check if we have a key
        if self.key is None:
            self.handshake()

        return self.readaddress(address=EEPROM_ADDRESS_POWER_LEVEL)

    def powerLevelWrite(self, powerlevel: int = POWERLEVEL_NORMAL):
        """
        Write the power level into EEPROM. Please note you have to restart to use this power level as startup.
        :param powerlevel: The power level for writing.
        :return: True if the power level is written into the EEPROM.
        """

        log.debug('Writing the power level into the eeprom -> 0x%0.2X' % powerlevel)

        # Check if we have a key
        if self.key is None:
            self.handshake()

        # If the mode is actual the favorite one
        if powerlevel == self.readaddress(address=EEPROM_ADDRESS_POWER_LEVEL):
            return True

        return self.writedata(address=EEPROM_ADDRESS_POWER_LEVEL, data=powerlevel)

    def adcDisable(self):
        """
        Disable ADC --> The potentiometers at the front are disabled so you can not control the device anymore!
        """

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

    def adcEnable(self):
        """
        Enable ADC --> You get control over the potentiometers.
        """

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

    def levelASet(self, level: int = 0x00):
        """
        Set the Level A if the ADC is disabled.
        :param level: The Level of A 0-255
        :return: True if the level was set.
        """

        # TODO: Check if the ADC is disabled!
        log.debug('Set level A to: 0x%0.2X' % level)

        # Check if the int value is between 0 and 255
        if level < 0x00 or level > 0xff:
            log.debug('Level needs to be between 0x00 and 0xff! -> Can not set Level A to: 0x%0.2X' % level)
            return False

        # Check if we have a key
        if self.key is None:
            self.handshake()

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

    def levelAGet(self):
        """
        Get Level A.
        :return: The Level of A.
        """

        log.debug('Get Level A.')

        # Check if we have a key
        if self.key is None:
            self.handshake()

        read_levela = self.readaddress(address=ADDRESS_LEVELA)
        log.debug('Level A is set to: 0x%0.2X' % read_levela)
        return read_levela

    def levelBSet(self, level: int = 0x00):
        """
        Set the Level B if the ADC is disabled.
        :param level: The Level of B 0-255
        :return: True if the level was set.
        """

        # TODO: Check if the ADC is disabled!
        log.debug('Set level B to: 0x%0.2X' % level)

        # Check if the int value is between 0 and 255
        if level < 0x00 or level > 0xff:
            log.debug('Level needs to be between 0x00 and 0xff! -> Can not set Level B to: 0x%0.2X' % level)
            return False

        # Check if we have a key
        if self.key is None:
            self.handshake()

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

    def levelBGet(self):
        """
        Get Level B.
        :return: The Level of B.
        """

        log.debug('Get Level B.')

        # Check if we have a key
        if self.key is None:
            self.handshake()

        read_levelb = self.readaddress(address=ADDRESS_LEVELB)
        log.debug('Level B is set to: 0x%0.2X' % read_levelb)
        return read_levelb

    def levelMASet(self, level: int = 0x00):
        """
        Set the Level MA if the ADC is disabled.
        :param level: The Level of MA 0-255
        :return: True if the level was set.
        """

        # TODO: Check if the ADC is disabled!
        log.debug('Set level MA to: 0x%0.2X' % level)

        # Check if we have a key
        if self.key is None:
            self.handshake()

        # Check if the int value is between min MA and max ma
        read_min_ma, read_max_ma = self.levelMAGetMinMaxValue()

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

    def levelMAGetMinMaxValue(self):
        """
        Get the possible minimal and maximal value of the multi adjust.
        Please note that the minimal level is not necessarily the minimal value and vice versa.
        :return: Min Level, Max Level
        """

        # TODO: Store the minimal and maximal levels in the object self.mamax and self.mamin
        #  fill the data if new mode is selected
        log.debug('Get the minimal and maximal multi adjust values.')

        # Check if we have a key
        if self.key is None:
            self.handshake()

        read_min_ma = self.readaddress(address=ADDRESS_MA_MIN_VALUE)
        log.debug('MA minimal value is: 0x%0.2X' % read_min_ma)
        read_max_ma = self.readaddress(address=ADDRESS_MA_MAX_VALUE)
        log.debug('MA maximal value is: 0x%0.2X' % read_max_ma)

        return read_min_ma, read_max_ma

    def levelMAGet(self):
        """
        Get the multi adjust level.
        :return: The Level of MA.
        """

        log.debug('Get multi adjust level.')

        # Check if we have a key
        if self.key is None:
            self.handshake()

        read_levelma = self.readaddress(address=ADDRESS_LEVELMA)
        log.debug('Level MA is set to: 0x%0.2X' % read_levelma)
        return read_levelma
