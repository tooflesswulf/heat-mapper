INCLUDES = \
	   -I./ \
	   -I/usr/local/include \
	   -I/usr/include/python2.7 \
	   -I.. \
	   -I/usr/include \
	   -I../muwcomm \
	   -I../markovtools

LIBS= -L/usr/lib -L/usr/local/lib -L/usr/local/lib64 -L/usr/lib64 \
	-lstdc++ -L. -L../markovlibs \
	-L/usr/lib/arm-linux-gnueabihf -lpython2.7 \
	-lboost_python -lboost_numpy -L../muwcomm -lmarkovtools -lpthread

CC=gcc
CFLAGS=	-g -c $(SHFLAGS) $(INCLUDES) -std=c++14 -DLEPTON3
SHFLAGS = -fpic
LDFLAGS= -shared $(LIBS)

SRCS=LeptonFrameGrabber.cpp \
	LeptFrameStore.cpp \
	SPI.cpp \
	ImageProc.cpp \
	Palletes.cpp 

OBJS=$(SRCS:.cpp=.o)

OUTDIR=../markovlibs

PYMODULE=liblepton.so
LEPTONTEST = leptonTest

all: $(LEPTONTEST) $(PYMODULE)

depend:
	makedepend -- $(CFLAGS) -- $(SRCS)

LEPTONTESTSRCS=LeptonTest.cpp
LEPTONTESTSRCS+=$(SRCS)
LEPTONTESTOBJS=$(LEPTONTESTSRCS:.cpp=.o)

$(LEPTONTEST): $(LEPTONTESTOBJS)
	$(CC) -o $(LEPTONTEST) $(LEPTONTESTOBJS) $(LIBS)

.cpp.o:
	$(CC) $(CFLAGS) $< -o $@

clean:
	echo "Removing all Boost Python objs"
	rm -f $(OBJS)
	rm -f $(PYMODULE)
	rm -f $(LEPTONTEST)

$(OUTDIR):
	mkdir -p $(OUTDIR)


$(PYMODULE): $(OBJS) $(OUTDIR)
	$(CC) $(LDFLAGS) $(SHFLAGS) -o $(OUTDIR)/$(PYMODULE) $(OBJS)

# DO NOT DELETE THIS LINE -- make depend depends on it.
