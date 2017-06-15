#include "LeptFrameStore.h"
#include <iostream>
#include <stdio.h>
#include <errno.h>
#include "markovTimeTools.h"

LeptFrame::LeptFrame()
{}

LeptFrame::LeptFrame( const char *fileName )
{
	fname = strdup(fileName);
	fn = strdup(fileName);
	sprintf(fn, "%s.dat", fname);
	fp = fopen( fn, "w+");
	if (fp != NULL )
		isOpen = true;
	else
		isOpen = false;
	count = 0;
}

int LeptFrame::writeFrame( const LeptonRawImage_t *img ) {
	if(count > 1000)
		reopen();
	if( isOpen ) {
		// Write the header
		fwrite( (void*)&(img->hdr), sizeof(LeptonRawFrameHdr_t), 1, fp );
		fwrite( (void*)(img->img), sizeof(uint16_t), img->hdr.w * img->hdr.h, fp );
		count++;
	}
	else {
		reopen();
		if(!isOpen) {
			fprintf(stderr,"\nError: File not open.");
			return ERRFILENOTOPEN;
		} else {
			writeFrame(img);
		}
	}	
	return WRITE_SUCCESS;
}

int LeptFrame::reopen()
{
	close();
	double cur_time = MarkovTools::TimeTools::getEpochTime();
	// int result;
	char newname[100];
	sprintf(newname,"%s_%f.dat", fname, cur_time);
	std::cout << "Renaming " << fn << " as " << newname << std::endl;
	int result = rename( fn, newname);
	if(result==0) {
		fp = fopen( fn, "w+");
		count = 0;
	} else {
	    std::cout << "Error: " << strerror(errno) << std::endl;
		fp = fopen(fn, "a+");
	}
	if (fp != NULL )
		isOpen = true;
	else
		isOpen = false;
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
