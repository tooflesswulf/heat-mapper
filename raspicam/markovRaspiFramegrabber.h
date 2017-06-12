#ifndef __MARKOV_RASPI_FRAMEGRABBER_H__
#define __MARKOV_RASPI_FRAMEGRABBER_H__

#include <vector>
#include <markovTimeTools.h>
#include <iostream>
#include <ctime>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <PicamFrameStore.h>
#include <memory>
#include "raspicam.h"

using std::string;
using std::vector;
using std::cerr;
using std::endl;
using std::cout;
using std::make_unique;
using std::unique_ptr;
using namespace raspicam;
using namespace MarkovTools;

class MarkovRaspiFramegrabber
{
private:
	unique_ptr<TimeTools> timetool;
	unique_ptr<PicamFrame> picamFrame;
	unique_ptr<raspicam::RaspiCam> picam;
	int w;
	int h;
public:
	MarkovRaspiFramegrabber();
	MarkovRaspiFramegrabber(string s, int w, int h);
	~MarkovRaspiFramegrabber();
	vector<uint8_t> GrabImage(int &w, int &h);
};


#endif/*__MARKOV_RASPI_FRAMEGRABBER_H__*/
