# Makefile for the code in this directory.
# Author: Arvind Pereira <arvind@markovcorp.com>

# For libjpegcompress original code can be found here: https://code.google.com/archive/p/jpeg-compressor/
#

INCLUDES = -I ./ -I/usr/local/include

LIBS = -L/usr/lib -L/usr/local/lib -L./ -L../markovlibs/ -ljpegcompressor -lstdc++ -lm

CC = gcc
DEBUG = -g
LFLAGS = -Wall -Werror
CFLAGS = -g -Wall -c -std=c++14
LD=$(CC)
AR= ar rc
RANLIB = ranlib
RM = rm

SOURCES = \
jpgd.cpp \
jpge.cpp \
timer.cpp \
stb_image.cpp

HEADERS = \
jpgd.h \
jpge.h \
timer.h

TGA2JPG = tga2jpg

TGA2JPGSRCS = tga2jpg.cpp
TGA2JPGSOBJS = $(TGA2JPGSRCS:.cpp=.o)

JPGCOMPRESSLIB = ../markovlibs/libjpegcompressor.a
JPGCOMPRESSLIBSRCS = $(SOURCES)
JPGCOMPRESSLIBOBJS = $(JPGCOMPRESSLIBSRCS:.cpp=.o)

all: $(JPGCOMPRESSLIB) $(TGA2JPG)

$(JPGCOMPRESSLIB): $(JPGCOMPRESSLIBOBJS) $(OBJDIR)
	$(AR) $(JPGCOMPRESSLIB) $(JPGCOMPRESSLIBOBJS)
	$(RANLIB) $(JPGCOMPRESSLIB)

$(TGA2JPG): $(JPGCOMPRESSLIB) $(TGA2JPGSOBJS)
	$(CC) -o $(TGA2JPG) $(TGA2JPGSOBJS) $(LIBS) 
	
.cpp.o:
	$(CC) $(CFLAGS) $(INCLUDES) $< -o $@

clean:
	$(RM) -f $(JPGCOMPRESSLIB)
	$(RM) -f $(JPGCOMPRESSLIBOBJS)
	$(RM) -f $(TGA2JPG)
	$(RM) -f $(TGA2JPGSOBJS)