#! /usr/bin/python
import usb.core
import usb.util

VENDOR_ID = 0x0922
PRODUCT_ID = 0x8003

DATA_MODE_GRAMS = 2
DATA_MODE_OUNCES = 11

GRAMS_PER_OUNCE = 28.3495

class scale:

    device = None
    endpoint = None

    def __init__(self):
        # find the USB device
        scale.device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
        if scale.device.is_kernel_driver_active(0):
            try:
                scale.device.detach_kernel_driver(0)
                print "kernel driver detached"
            except usb.core.USBError as e:             
                sys.exit("Could not detach kernel driver: %s" % str(e))

        # use the first/default configuration
        scale.device.set_configuration()
        # first endpoint
        scale.endpoint = scale.device[0][(0,0)][0]

    def getWeight(self):
        """Returns the weight on the scale in grams."""
        # read a data packet
        attempts = 10
        data = None
        while data is None and attempts > 0:
            try:
                data = scale.device.read(scale.endpoint.bEndpointAddress, scale.endpoint.wMaxPacketSize)
            except usb.core.USBError as e:
                data = None
                if e.args == ('Operation timed out',):
                     attempts -= 1
                continue

        if data[2] == DATA_MODE_GRAMS:
		weight = data[4] + data[5]/1000.
	elif data[2] == DATA_MODE_OUNCES:
		weight = data[4] + data[5]*256
		weight *= GRAMS_PER_OUNCE
	
	return weight
