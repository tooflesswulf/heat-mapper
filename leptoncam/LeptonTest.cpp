#include <iostream>
#include <unistd.h>
#include <LeptonFrameGrabber.h>

using std::cout;
using std::endl;

int main(int argc, char *argv[])
{
	cout<<"LeptonFrameGrabbingTest."<<endl;

	std::string fname;
	if(argc > 1) {
		fname = argv[1];
	}
	else {
		cout<<"Using default name 'Latest.dat'"<<endl;
		fname = "Latest";
	}

	LeptonFrameGrabber lfg(fname);
	// LeptonFrameGrabber lfg("Latest.dat");

	cout<<"Enabling radiometry mode."<<endl;
	lfg.enableRadMode();

	cout<<"Performing a FFC"<<endl;
	lfg.performFFC();

	sleep(1);
	cout<<"Now grabbing frames..."<<endl;

	// for(int i=0;i<100;i++) {
	while(true){
		vector<uint16_t> img=lfg.GrabImage();
	}

	cout<<"Done grabbing 100 images to "<< fname <<".dat"<<endl;
	cout<<"Frame rate was "<<lfg.getLeptonFrameRate()<<" fps."<<endl;


	return 0;
}
