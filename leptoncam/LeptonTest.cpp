#include <iostream>
#include <unistd.h>
#include <LeptonFrameGrabber.h>

using std::cout;
using std::endl;

int main(int argc, char *argv[])
{
	cout<<"LeptonFrameGrabbingTest."<<endl;

	LeptonFrameGrabber lfg("Test.dat");
	cout<<"Enabling radiometry mode."<<endl;
	lfg.enableRadMode();

	cout<<"Performing a FFC"<<endl;
	lfg.performFFC();

	sleep(1);
	cout<<"Now grabbing frames..."<<endl;

	for(int i=0;i<100;i++) {
		vector<uint16_t> img=lfg.GrabImage();
	}

	cout<<"Done grabbing 100 images to Test.dat"<<endl;
	cout<<"Frame rate was "<<lfg.getLeptonFrameRate()<<endl;


	return 0;
}
