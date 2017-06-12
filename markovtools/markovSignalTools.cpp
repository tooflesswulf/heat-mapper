/*
 * SignalTools.cpp
 *      Author: Arvind A de Menezes Pereira <arvind@markovcorp.com>
 */
#ifndef _WINDOWS_ // Never use this in Windoze.

#include "markovSignalTools.h"

namespace MarkovTools {

SingletonSignalHandler* SingletonSignalHandler::mySelf=NULL; // The only pointer to this instance


SingletonSignalHandler * SingletonSignalHandler::getInstance() {
		if( !mySelf )
			SingletonSignalHandler::mySelf = new SingletonSignalHandler;
		return mySelf;
	}

void SingletonSignalHandler::captureSignal( int signalType, void (*pfunct)(int) ) {
		struct sigaction sa;
		memset( &sa, 0, sizeof( sa ) );
		sa.sa_handler = pfunct;
		switch( signalType ) {
			case InterruptSignal:
				if( sigaction(SIGINT, &sa, NULL)) { perror("sigaction");
				throw std::runtime_error("Could not capture Interrupt signal."); }
				break;
			case TerminateSignal:
				if( sigaction(SIGTERM, &sa, NULL) ) { perror("sigaction");
					throw std::runtime_error("Could not capture Terminate signal."); }
				break;
			case KillSignal:
				if( sigaction(SIGKILL, &sa, NULL) ) { perror("sigkill");
					throw std::runtime_error("Could not capture Kill signal."); }
				break;
			case SegmentationFaultSignal:
				if( sigaction(SIGSEGV, &sa, NULL) ) { perror("sigsegv");
					throw std::runtime_error("Could not capture SegFault signal.");
				}
				break;
			case FloatingPointExceptionSignal:
				if( sigaction(SIGFPE, &sa, NULL) ) { perror("sigfpe");
					throw std::runtime_error("Could not capture SIGFPE signal.");
				}
				break;
			case AbortSignal:
				if( sigaction(SIGABRT, &sa, NULL) ) {
					throw std::runtime_error("Could not capture SIGABRT signal.");
				}
				break;
			default:
				throw std::invalid_argument("Unknown/Unimplemented signal.");
				break;
		}
}

void SingletonSignalHandler::endSignalCapture() {
	delete SingletonSignalHandler::mySelf;
	SingletonSignalHandler::mySelf = NULL;
}

};

#endif
