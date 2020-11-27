# MK312 Communication Wrapper

## Introduction

This is an communication wrapper for the MK-312BT Estim Box. It uses `pyserial` for the RS232 communication. Primary I wrote it for my own purposes. It should be the base for a remote controlling tool and an abstraction layer for a Rest API too.
If you like to do a test, it would be great :) I love to hear from you if there are some problems.

## Firmware

I test the examples with the firmware from: [https://github.com/buttshock/mk312-bt/tree/master/firmware/Custom%20Boot%20Message%20f005-MK312-BT](https://github.com/buttshock/mk312-bt/tree/master/firmware/Custom%20Boot%20Message%20f005-MK312-BT).
Please note that I have some trouble with the fuse bits. Therefore I was using: `L: 0xFF / H: 0xD9` which worked perfectly for me.

## Connection

The communication with the MK-312 device is working via an RS232 interface. I'm not glad about the phone jack because you can shorten the connectors while plugging in the interface cable. So I suggest to do the connection if the device is switched off. Maybe someone will giving the board an sub-d connector in further hardware versions. Or even better a real ethernet connection with a socket communication :) 

| Phone Jack | RS232 | Sub-D |
|------------|-------|-------|
| Tip        | RxD   | Pin 2 |
| Ring       | TxD   | Pin 3 |
| Sleeve     | Gnd   | Pin 5 |

The soldering of the phone jack is a little tricky. Maybe that is the reason for the high price of the cable...

### Settings

The RS232 interface is working with 8 Bytes / None Parity / 1 Stop Bit and a baudrate of 19200.
Actually the communication wrapper is using 19200. You can switch the baudrate by yourself if you set the necessary UART registers. I did not a test with other baudrates than 19200.

## Examples

Please check the examples dir. I wrote some basic tests which should work.

## Handshaking

I got some troubles with the handshaking which are actually not solved. So please do the communication in the way:

```python
et312 = mk312.MK312CommunicationWrapper()
et312.handshake()

# Do the stuff you like to do with your box
# ...
# ...

# Reset key and close the interface
et312.resetkey()
et312.closeserialport()
```

If there is an interrupt of the script before you reset the key, you will getting problems with a reconnect. Maybe someone was fixing this issue or can help me with this matter.

When nothing helps you can switch off the box and switch it on again. Because of the high amount of capacitors the RAM of the AVR is bufferd very long - so it take some time to wait until a reconnection is possible. I have no battery on my MK-312 therefore I can only plug off the power supply. A better way will be unloading the capacitors if switching the box off...this remains in an hardware redesign too.

## Logging

For debugging reason I designed the wrapper in a way that he talks a very lot. If you don't like it when you are using an own logger than please change the logging level to info. The logger of the wrapper is talking at the debug level. 

## License

Please read the `LICENSE` file. Especially: *IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY* --> It is your turn to use the communication wrapper! 

## Thanks to...

My work is based on these two repos:

* [https://github.com/buttshock/buttshock-py](https://github.com/buttshock/buttshock-py)
* [https://github.com/buttplugio/stpihkal](https://github.com/buttplugio/stpihkal)

Without the preliminary work of the protocol description and the handshaking it would be much harder for me.
