all: 
	$(MAKE) -C markovtools
	$(MAKE) -C leptoncam
	$(MAKE) -C gpiolib

ifeq ($(MACHINE),armv7l)
	$(MAKE) -C raspicam
endif
	$(MAKE) -C jpeg_compression

clean:
	$(MAKE) -C markovtools clean
	$(MAKE) -C leptoncam clean
	$(MAKE) -C gpiolib clean
ifeq ($(MACHINE),armv7l)
	$(MAKE) -C raspicam clean
endif
	$(MAKE) -C jpeg_compression clean

ifndef MACHINE
MACHINE=$(shell uname -m)
endif