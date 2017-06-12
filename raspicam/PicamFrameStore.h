#ifndef __PICAM_FILE_STORE_H__
#define __PICAM_FILE_STORE_H__

#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <stdint.h>
#include <string>

using std::string;

#define WRITE_SUCCESS (0)
#define ERRFILENOTOPEN (-1)

typedef struct _PicamRawFrameHdr {
	int w;
	int h;
	double time;
} PicamRawFrameHdr_t;

typedef struct _PicamRawImage {
	PicamRawFrameHdr_t hdr;
	uint8_t *img;
} PicamRawImage_t;


class PicamFrame
{
private:
	FILE *fp;
	bool isOpen;
	char *fileName;
	int seqNum;
	PicamFrame();
public:
	PicamFrame( string fileName );
	int writeFrame( const PicamRawImage_t *img );
	int close();
	bool is_open();
	~PicamFrame();
};

#endif/*__PICAM_FILE_STORE_H__*/
