# Makefile for the code in this directory.
# Author: Arvind Pereira <arvind@markovcorp.com>

# For libthreadpool use this repo: https://github.com/arvindpereira/threadpool
# git clone git@github.com:arvindpereira/threadpool.git
# Install into /usr/local/lib
# Do not pull it into this project because it is released under the GNU GPLV2.
# Always build separately and link into it.

INCLUDES = -I ./ -I/usr/local/include 
LIBS = -L/usr/local/lib -L./ -L/usr/lib/x86_64-linux-gnu/ -L../leptonSDKEmb32PUB/Debug/ -pthread -lstdc++

CC = gcc
DEBUG = -g
LFLAGS = -Wall -Werror
CFLAGS = -g -Wall -Werror -c # -DRASPBPI
LD=$(CC)
AR = ar rc
RANLIB	= ranlib
RM= rm

# For cross-compilation on the Pi get toolchain for RaspberryPi from 
#include ../../external/pigpio/configArm.mk

OUTDIR = ../markovlibs


SOURCES = \
markovTimeTools.cpp \
markovSignalTools.cpp 

HEADERS = \
markovTimeTools.h \
markovSignalTools.h \
markovScopedLock.h 

MARKOVTOOLSLIB = libmarkovtools.a

OBJECTS = $(SOURCES:.cpp=.o)

all: $(MARKOVTOOLSLIB) 

$(MARKOVTOOLSLIB): $(OBJECTS)
	mkdir -p $(OUTDIR)
	$(AR) $(OUTDIR)/$(MARKOVTOOLSLIB) $(OBJECTS)
	$(RANLIB) $(OUTDIR)/$(MARKOVTOOLSLIB)

.cpp.o:
	$(CC) $(CFLAGS) $(INCLUDES) $< -o $@

tar:
	tar -czf Test_Tools.tar.gz $(SOURCES) $(HEADERS) Makefile

clean:
	$(RM) -f $(OBJECTS)
	$(RM) -f $(MARKOVTOOLSLIB)
