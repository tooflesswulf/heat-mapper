#include <string.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include <fcntl.h>              /* low-level i/o */
#include <unistd.h>
#include <errno.h>
#include <malloc.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/time.h>
#include <sys/mman.h>
#include <sys/ioctl.h>

#include <stdint.h>

#include <asm/types.h>          /* for videodev2.h */

#include <linux/videodev2.h>
#include <linux/usbdevice_fs.h>
#include <linux/uvcvideo.h>
#include <linux/usb/video.h>

#include "Palletes.h"

#define  LOG_TAG    "V4L2LeptonCam"
#define  LOGI(fmt, ...)  printf(fmt "\n", ##__VA_ARGS__)
#define  LOGE(fmt, ...)  printf(fmt "\n", ##__VA_ARGS__)

#define CLEAR(x) memset (&(x), 0, sizeof (x))

#ifdef LEPTON3
#define IMG_WIDTH 160
#define IMG_HEIGHT 120
#else
#define IMG_WIDTH 80
#define IMG_HEIGHT 60
#endif

#define ERROR_LOCAL -1
#define SUCCESS_LOCAL 0

int errnoexit(const char *s);

//int xioctl(int fd, int request, void *arg);

//int checkCamerabase(void);
//int opendevice(int videoid);
//int initdevice(void);
//int initmmap(void);
//int startcapturing(void);
bool readframeonce(uint16_t *out);
// bool readframe(uint16_t *out);
//void processimage (const void *p);

//int stopcapturing(void);
//int uninitdevice(void);
//int closedevice(void);
//int *getbuf();
int leptonFfc(void);
int prepareCamera(int videoid);

//void yuyv422toABGRY(unsigned char *src);
//void rescaleToARGBY(unsigned char *src);
int initLepton(int w, int h);
int waitFrame( void );
void deinit();
