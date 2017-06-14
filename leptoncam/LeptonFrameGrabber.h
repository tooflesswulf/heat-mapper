#ifndef __LEPTON_FRAME_GRABBER_H___
#define __LEPTON_FRAME_GRABBER_H___

#include <ctime>
#include <stdint.h>
#include "LeptFrameStore.h"
#include "markovTimeTools.h"
#include "markovScopedLock.h"
#define PACKET_SIZE 164
#define PACKET_SIZE_UINT16 (PACKET_SIZE/2)
#define PACKETS_PER_FRAME 60
#define FRAME_SIZE_UINT16 (PACKET_SIZE_UINT16*PACKETS_PER_FRAME)
#include <vector>
#include <string>
#include <memory>

#include <pthread.h>

using namespace MarkovTools;

using std::vector;
using std::shared_ptr;

class LeptonFrameGrabber
{
public:
  LeptonFrameGrabber(std::string);
  ~LeptonFrameGrabber();
  void performFFC();
  vector<uint16_t> GrabImage();
  int enableRadMode();
  int disableRadMode();
  int getRadModeState();
  int getRBFO();
  int setRBFO();
  void OpenPorts();
  int ClosePorts();
  int createLeptonThread();
  void leptonFrameGrabberThread();
  static void *setupLeptonReadThread(void *arg);

  void stopLeptonThread();
  void startLeptonThread();
  void initiateSinglePoll();
  void initiateEnableRadMode();
  void initiateDisableRadMode();
  void startContinuousGrabber();
  bool isThreadCreated() {	return leptonThreadCreated;  }
  double getLastLeptonFrameTime() { return timeOfLastLeptonFrame; }
  void executeAfterReset();
  void updateImageStats(uint16_t *buf, int len);
  void updateFrameRate();
  void ffc();
  double getLeptonFrameRate();

private:
	uint8_t result[PACKET_SIZE*PACKETS_PER_FRAME];
	uint16_t *frameBuffer;
	LeptonRawImage_t lwirImg;
	shared_ptr<LeptFrame> lptFrame;
	shared_ptr<TimeTools> timetool;
	int resets;
	int packetNumber;
	int framesSinceLastReset;
	double timeWhenLastReset;
	vector<uint16_t> imageData;

	// Lepton Frame grabbing related variables
	bool leptonThreadCreated;
	pthread_t leptonReadThread;
	pthread_mutex_t leptonMutex;
	pthread_cond_t leptonCond;
	bool stopRunningLeptonThread;
	bool grabLeptonFrame;
	bool singleLeptonPoll;
	bool performFFCflag;
	bool changeRadModeFlag;
	bool radModeEnabledState;
	double leptonFramerate;
	double timeOfLastLeptonFrame;
};


#endif/*__LEPTON_FRAME_GRABBER_H___*/
