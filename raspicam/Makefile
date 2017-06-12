RASPICAM_LIBS = ../markovlibs/libraspicam.so

CC = gcc

RASPICAM_SRCS = \
	markovRaspiFramegrabber.cpp \
	PicamFrameStore.cpp \
	src/raspicam.cpp \
	src/private/mutex.cpp \
	src/private/threadcondition.cpp \
	src/private/private_impl.cpp \
	src/private/yuv_conversion.cpp


RASPICAM_TEST = raspicamTest

RASPICAM_TEST_SRC = raspicam_test.cpp
RASPICAM_TEST_OBJ = $(RASPICAM_TEST_SRC:.cpp=.o)


INCLUDES = /usr/local/include -I./dependencies -I./src -I. -I./src/private -I../markovtools

LIBS = -L/usr/local/lib -L/usr/lib -lstdc++ -L/opt/vc/lib -lmmal_core -lmmal_util -lmmal

CFLAGS = -c -g -Wall -DNDEBUG -fPIC -std=c++14

.cpp.o:
	$(CC) $(CFLAGS) $(INCLUDES) $< -o $@

all: $(RASPICAM_LIBS) $(RASPICAM_TEST)

RASPICAM_OBJS = $(RASPICAM_SRCS:.cpp=.o)


$(RASPICAM_LIBS): $(RASPICAM_OBJS)
	$(CC) -o $(RASPICAM_LIBS) $(RASPICAM_OBJS) -shared $(LIBS)

$(RASPICAM_TEST): $(RASPICAM_LIBS) $(RASPICAM_TEST_OBJ) 
	$(CC) -o $(RASPICAM_TEST) $(RASPICAM_TEST_OBJ) $(LIBS) -L../markovlibs -lraspicam -lmarkovtools

clean:
	@rm -f $(RASPICAM_LIBS)
	@rm -f $(RASPICAM_OBJS)
	@rm -f $(RASPICAM_TEST)
	@rm -f $(RASPICAM_TEST_OBJ)
