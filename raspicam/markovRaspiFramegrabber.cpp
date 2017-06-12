#include <markovRaspiFramegrabber.h>

MarkovRaspiFramegrabber::MarkovRaspiFramegrabber() : timetool( make_unique<TimeTools>()), picamFrame( make_unique<PicamFrame>("markovRaspi.picamDat")),
		picam(nullptr)
{
	timetool = make_unique<TimeTools>();
	picam = nullptr;
	picamFrame = make_unique<PicamFrame>("markovRaspi.picamDat");
	w = 640;
	h = 480;
}

MarkovRaspiFramegrabber::MarkovRaspiFramegrabber(string fileName, int w, int h) : MarkovRaspiFramegrabber()
{
	timetool = make_unique<TimeTools>();
	picamFrame = make_unique<PicamFrame>(fileName);
	picam = make_unique<raspicam::RaspiCam>();
	this->w = w;
	this->h = h;
	picam->setHeight(h);
	picam->setWidth(w);
	picam->setFormat(raspicam::RASPICAM_FORMAT_RGB);
	if( !picam->open() ) {
		cerr<<"Error opening Picam."<<endl;
	}
}



MarkovRaspiFramegrabber::~MarkovRaspiFramegrabber()
{
	picam->release();
}

vector<uint8_t> MarkovRaspiFramegrabber::GrabImage(int &w, int &h)
{
	w = picam->getWidth();
	h = picam->getHeight();
	vector<uint8_t> data( picam->getImageBufferSize() );
	picam->grab();
	picam->retrieve( &data[0] );
	PicamRawFrameHdr_t prfh { w, h, timetool->getEpochTime() };
	PicamRawImage_t pri;
	pri.hdr = prfh;
	pri.img = &data[0];
	if( picamFrame->is_open()) {
		picamFrame->writeFrame( &pri );
	}

	return data;
}
