# Makefile for the code in this directory.
# Author: Arvind Pereira <arvind@markovcorp.com>

# For libthreadpool use this repo: https://github.com/arvindpereira/threadpool
# git clone git@github.com:arvindpereira/threadpool.git
# Install into /usr/local/lib
# Do not pull it into this project because it is released under the GNU GPLV2.
# Always build separately and link into it.

INCLUDES = -I ./ -I/usr/local/include -I/usr/include/python2.7
LIBS = -L/usr/local/lib -L./ -L/usr/lib/x86_64-linux-gnu/ -pthread -lpython2.7 -lstdc++#-lthrpool

CC = gcc
DEBUG = -g
LFLAGS = -Werror
CFLAGS = -g -Wall -c -fpermissive -fPIC # -Wall -Werror 
LD=$(CC)
AR = ar rc
RANLIB	= ranlib
RM= rm
LDFLAGS = -shared

# For cross-compilation on the Pi get toolchain for RaspberryPi from 
#include ../../external/pigpio/configArm.mk
UNAME_S= $(shell uname -s)
ifeq ($(UNAME_S),Linux)
        LDFLAGS += -Wl,-soname,$(GPIOSHRLIB)
endif
ifeq ($(UNAME_S),Darwin)
        CFLAGS += -dynamiclib
        LDFLAGS += -dynamiclib -fPIC
endif

OUTDIR=../markovlibs

SOURCES = \
c_gpio.cpp \
common.cpp \
cpuinfo.cpp \
event_gpio.cpp \
soft_pwm.cpp

HEADERS = \
c_gpio.h \
common.h \
cpuinfo.h \
event_gpio.h \
soft_pwm.h

SERVERTEST = markov_server_test
CLIENTTEST = markov_client_test

GPIOLIB = libgpio.a
GPIOSHRLIB = libgpio.so

OBJECTS = $(SOURCES:.cpp=.o)

all: $(GPIOLIB) $(GPIOSHRLIB)

$(GPIOLIB): $(OBJECTS)
	$(AR) $(OUTDIR)/$(GPIOLIB) $(OBJECTS)
	$(RANLIB) $(OUTDIR)/$(GPIOLIB)
	
$(GPIOSHRLIB): $(OBJECTS)
	$(CC) $(LDFLAGS) -o $(OUTDIR)/$(GPIOSHRLIB) $(OBJECTS) $(LIBS)

.cpp.o:
	$(CC) $(CFLAGS) $(INCLUDES) $< -o $@

tar:
	tar -czf Test_Tools.tar.gz $(SOURCES) $(HEADERS) Makefile

clean:
	$(RM) -f $(OBJECTS)
	$(RM) -f $(OUTDIR)/$(GPIOLIB)
	$(RM) -f $(OUTDIR)/$(GPIOSHRLIB)
