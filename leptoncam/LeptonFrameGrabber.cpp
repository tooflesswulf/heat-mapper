#include "LeptonFrameGrabber.h"
#include "ImageProc.h"

//#include "Palettes.h"
#include "LeptFrameStore.h"
#include "markovTimeTools.h"

#include <iostream> 
#include <vector>
#include <string>

#define PACKET_SIZE 164
#define PACKET_SIZE_UINT16 (PACKET_SIZE/2)
#define PACKETS_PER_FRAME 60
#define FRAME_SIZE_UINT16 (PACKET_SIZE_UINT16*PACKETS_PER_FRAME)
#define FPS 27


using std::vector;
using std::endl;
using std::cout;
using std::make_unique;

#define IMG_HDR  ( 9 )
#define IMG_SIZE ( IMG_WIDTH * IMG_HEIGHT + IMG_HDR )

void LeptonFrameGrabber::OpenPorts() {
	initLepton(IMG_WIDTH,IMG_HEIGHT);
}

int LeptonFrameGrabber::ClosePorts() {
	deinit();
}

LeptonFrameGrabber::LeptonFrameGrabber(std::string fileName) : imageData( IMG_WIDTH*IMG_HEIGHT ),
		leptonMutex(PTHREAD_MUTEX_INITIALIZER),
		leptonCond(PTHREAD_COND_INITIALIZER),
		lptFrame(std::make_shared<LeptFrame>(fileName.c_str())),
		timetool(std::make_shared<MarkovTools::TimeTools>())
{
	resets = 0;
	packetNumber = 0;
	lwirImg.hdr.w = IMG_WIDTH;
	lwirImg.hdr.h = IMG_HEIGHT;
	// These will be filled in later at runtime.
	lwirImg.hdr.low = 65535;
	lwirImg.hdr.high = 0;
	lwirImg.hdr.time = 0;
	lwirImg.hdr.internal_temp = -100;

	lwirImg.img = new uint16_t[  IMG_WIDTH * IMG_HEIGHT ];

	leptonThreadCreated = false;
	singleLeptonPoll = false;
	stopRunningLeptonThread = false;
	performFFCflag = true;
	changeRadModeFlag = true;
	radModeEnabledState = true;

	framesSinceLastReset = 0;
	timeWhenLastReset = MarkovTools::TimeTools::getEpochTime();

	//open v4l port
	OpenPorts();
}

LeptonFrameGrabber::~LeptonFrameGrabber() {
    imageData.clear();
    //finally, close SPI port
    ClosePorts();
}

int LeptonFrameGrabber::enableRadMode(){
	// How to toggle rad mode with v4l?
	// return lepton_rad_enable();

}

int LeptonFrameGrabber::disableRadMode(){
	// How to toggle rad mode with v4l?
	// return lepton_rad_disable();
}

int LeptonFrameGrabber::getRadModeState(){
	// How to toggle rad mode with v4l?
	//return lepton_get_rad_state();
}

int LeptonFrameGrabber::getRBFO(){
	// WTF is RBFO?
	//return lepton_getRBFO();
}

int LeptonFrameGrabber::setRBFO(){
	// WTF is RBFO?
	// return lepton_setRBFO();
}

void LeptonFrameGrabber::performFFC() {
        //perform FFC
        //std::cout << "Performing FFC" << std::endl;
        //lepton_perform_ffc();
}

void LeptonFrameGrabber::initiateSinglePoll() 					{
	MarkovScopedMutexGuard msg(leptonMutex);
	singleLeptonPoll = true;
	pthread_cond_signal( &leptonCond );
}

void LeptonFrameGrabber::initiateEnableRadMode()
{
	MarkovScopedMutexGuard msg(leptonMutex);
	radModeEnabledState = true;
}

void LeptonFrameGrabber::initiateDisableRadMode()
{
	MarkovScopedMutexGuard msg(leptonMutex);
	radModeEnabledState = false;
}

void LeptonFrameGrabber::startLeptonThread() {

}

void LeptonFrameGrabber::stopLeptonThread() {
	MarkovScopedMutexGuard msg(leptonMutex);
	// Wait for condition variable to allow us to proceed.
	grabLeptonFrame=false;
}

void LeptonFrameGrabber::startContinuousGrabber() {
	MarkovScopedMutexGuard msg(leptonMutex);
	grabLeptonFrame = true;
	pthread_cond_signal(&leptonCond);
}

int LeptonFrameGrabber::createLeptonThread()
{
	int res=pthread_create(&leptonReadThread,NULL,setupLeptonReadThread, this );
	if(res!=0)
	{ perror("Lepton read thread creation failed."); exit(EXIT_FAILURE); }
	res = pthread_mutex_init( &leptonMutex, NULL );
	if (res!=0) { perror("Mutex init failed."); exit(EXIT_FAILURE); }
	leptonThreadCreated = true;
	cout<<"Lepton thread was created."<<endl;

	return res;
}

void* LeptonFrameGrabber::setupLeptonReadThread(void *arg)
{
	LeptonFrameGrabber *leptonFg = reinterpret_cast<LeptonFrameGrabber*>(arg);
	leptonFg->leptonFrameGrabberThread();
	return (void*)0;
}

void LeptonFrameGrabber::leptonFrameGrabberThread(void)
{
	uint16_t lastChksum = 0;
	grabLeptonFrame = false;
	vector<uint8_t> data(IMG_HEIGHT*IMG_WIDTH*2 + 8); // 4600 uint16 words and a double for frame-rate.
	framesSinceLastReset = 0;
	timeWhenLastReset = MarkovTools::TimeTools::getEpochTime();
	while (!stopRunningLeptonThread)
	{
		if( performFFCflag ) {
			performFFC();
			performFFCflag = false;
		}
		if( changeRadModeFlag ) {
			if( radModeEnabledState ) {
				enableRadMode();
			}
			else {
				disableRadMode();
			}
			changeRadModeFlag = false;
		}
		{
			cout<<"Waiting on mutex\n";
			MarkovScopedMutexGuard msg(leptonMutex);
			// Wait for condition variable to allow us to proceed.
			while( !grabLeptonFrame && !singleLeptonPoll) {
				pthread_cond_wait(&leptonCond, &leptonMutex);
			}
			cout<<"got mutex\n";
		}
		// If we made it here, it is fine for us to keep grabbing frames from the Lepton.
		// When we do so, we will also put these frames in the out-going queue.
		vector<uint16_t> frame = GrabImage();

		uint16_t chksum = 0;
		for (int i=0; i< frame.size(); i++ ) {
			chksum += frame[i];
		}

		timeOfLastLeptonFrame = MarkovTools::TimeTools::getEpochTime();
		memcpy(&data[0], (uint8_t*)&frame[0], 60*80*2);
		double frameRate = this->getLeptonFrameRate();

		// We just grabbed a frame. Put it in the outgoing Image Queue.
		if (chksum != lastChksum ) {
			//	TODO: Albert, you will need to put this into a queue, or write out to file with a timestamp here...
			// tcpTransport->sendDataThroughPacket( data, (uint16_t)MKV_LEPTON_FRAME_IMG );
		}
		if( singleLeptonPoll ) {
			singleLeptonPoll = false;
		}
		lastChksum = chksum;

	}
}

void LeptonFrameGrabber::executeAfterReset()
{
	framesSinceLastReset = 0;
	timeWhenLastReset = MarkovTools::TimeTools::getEpochTime();
}

void LeptonFrameGrabber::updateFrameRate()
{
	++framesSinceLastReset;
	double currentTime = MarkovTools::TimeTools::getEpochTime();
}

double LeptonFrameGrabber::getLeptonFrameRate()
{
	double currentTime = MarkovTools::TimeTools::getEpochTime();
	leptonFramerate = framesSinceLastReset/(currentTime-timeWhenLastReset);
	return leptonFramerate;
}

void LeptonFrameGrabber::updateImageStats(uint16_t *buf, int len)
{
	uint16_t min = 65535, max=0;
	for (int i=0; i<len; i++) {
		if (buf[i]<min) min = buf[i];
		if (buf[i]>max) max = buf[i];
	}
	lwirImg.hdr.low = min;
	lwirImg.hdr.high = max;
}

vector<uint16_t> LeptonFrameGrabber::GrabImage()
{
	std::vector<uint16_t> ret(IMG_WIDTH*IMG_HEIGHT);
	printf("reading frame\n");
	if (readframeonce( &ret[0] )) {
	    memcpy(lwirImg.img, &ret[0], IMG_WIDTH*IMG_HEIGHT*2);
	    lwirImg.hdr.time = MarkovTools::TimeTools::getEpochTime();
	    updateImageStats(&ret[0],ret.size());
	    lptFrame->writeFrame(&lwirImg);
	    printf("done\n");
	}
	
	return ret;
}

void LeptonFrameGrabber::ffc()
{
	leptonFfc();
}

