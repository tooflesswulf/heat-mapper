#include "PicamFrameStore.h"
#include <iostream>

PicamFrame::PicamFrame()
{}

PicamFrame::PicamFrame( string fileName )
{
	fp = fopen( fileName.c_str(), "w+");
	if (fp != NULL )
		isOpen = true;
	else
		isOpen = false;
}

int PicamFrame::writeFrame( const PicamRawImage_t *img ) {
	if( isOpen ) {
		// Write the header
		fwrite( (void*)&(img->hdr), sizeof(PicamRawFrameHdr_t), 1, fp );
		fwrite( (void*)(img->img), sizeof(uint8_t) * 3, img->hdr.w * img->hdr.h, fp );
		fflush( fp );
	}
	else {
		fprintf(stderr,"\nError: File not open.");
		return ERRFILENOTOPEN;
	}
	return WRITE_SUCCESS;
}

int PicamFrame::close()
{
	fclose(fp);
	fp  = NULL;
	isOpen = false;
}

bool PicamFrame::is_open()
{
	return isOpen;
}

PicamFrame::~PicamFrame()
{
	close();
}
