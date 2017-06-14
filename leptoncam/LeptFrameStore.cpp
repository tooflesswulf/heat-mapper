#include "LeptFrameStore.h"
#include <iostream>
LeptFrame::LeptFrame()
{}

LeptFrame::LeptFrame( const char *fileName )
{
	fp = fopen( fileName, "w+");
	if (fp != NULL )
		isOpen = true;
	else
		isOpen = false;
}

int LeptFrame::writeFrame( const LeptonRawImage_t *img ) {
	if( isOpen ) {
		// Write the header
		fwrite( (void*)&(img->hdr), sizeof(LeptonRawFrameHdr_t), 1, fp );
		fwrite( (void*)(img->img), sizeof(uint16_t), img->hdr.w * img->hdr.h, fp );
	}
	else {
		fprintf(stderr,"\nError: File not open.");
		return ERRFILENOTOPEN;
	}	
	return WRITE_SUCCESS;
}

int LeptFrame::close()
{
	fclose(fp);
	fp  = NULL;
	isOpen = false;
}

bool LeptFrame::is_open()
{
	return isOpen;
}

LeptFrame::~LeptFrame()
{
	close();
}
