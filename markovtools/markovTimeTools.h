#ifndef __TIME_TOOLS_H__
#define __TIME_TOOLS_H__

#ifndef _WINDOWS_

#include <iostream>
#include <sys/time.h>


namespace MarkovTools {
/** This class contains tools that are useful for obtaining the current time in
 * seconds, milliseconds and so on.
 */
class TimeTools {
private:
	double startTime;
public:
	TimeTools();

	/** Provides current time in seconds. Useful when one needs to get a time-stamp.
 	 *  Resolution is in microseconds (accuracy might not be as high though).
	 * @return seconds since epoch (Jan 1 1970, 00:00:00.000000)
	 */
	static double getEpochTime();

	/** Provides the current time in milliseconds as a long. May be useful
	 * for providing integer time-stamps if the actual date/time are not
	 * that important. This might be useful for time-stamping packets.
	 *
	 */
	static unsigned long msTimer();

	/** Get the current time in seconds since the epoch */
	static unsigned long long get_secs();

	/** Get the relative time since this class was first constructed
	 *
	 * @return seconds since construction of this TimeTools class instance.
	 */
	double timeSinceStart();
};

};

#endif // #ifndef _WINDOWS_

#endif // #define __TIME_TOOLS_H__
