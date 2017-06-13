#include <iostream>
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

	// FILE *file;
	// file = fopen( "Test.dat", "w+");
	for(int i=0;i<100;i++) {
		vector<uint16_t> img = lfg.GrabImage();
		// cout << "[\n";
		std::string sep = "";
		// fwrite(&img[0], sizeof(uint16_t), sizeof(img), file);
		// int j = 0;
		// for (auto pix : img) {
			// if (j++ % 30 == 0)
			// 	cout << "\n\t";
			// cout << sep << pix;
		// }
		// cout << "\n]";
	}
	// fclose(file);

	cout<<"Done grabbing 100 images to Test.dat"<<endl;
	cout<<"Frame rate was "<<lfg.getLeptonFrameRate()<<endl;


	return 0;
}
