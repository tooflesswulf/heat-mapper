#ifndef __LEPTON_FILE_STORE_H__
#define __LEPTON_FILE_STORE_H__

#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <stdint.h>

#define WRITE_SUCCESS (0)
#define ERRFILENOTOPEN (-1)

typedef struct _LeptonRawFrameHdr {
	int w;
	int h;
	int low;
	int high;
	int internal_temp;
	double time;
} LeptonRawFrameHdr_t;

typedef struct _LeptonRawImage {
	LeptonRawFrameHdr_t hdr;
	uint16_t *img;
} LeptonRawImage_t;


class LeptFrame
{
private:
	FILE *fp;
	bool isOpen;
	char *fname;
	char *fn;
	int count;
	LeptFrame();
public:
	LeptFrame( const char *fileName ); 
	int writeFrame( const LeptonRawImage_t *img );
	int reopen();
	int close();
	bool is_open();
	~LeptFrame();
};

#endif/*__LEPTON_FILE_STORE_H__*/
