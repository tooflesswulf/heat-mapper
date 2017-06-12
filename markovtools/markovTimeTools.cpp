#include <markovTimeTools.h>

namespace MarkovTools {
/** This class contains tools that are useful for obtaining the current time in
 * seconds, milliseconds and so on.
 */

TimeTools::TimeTools() {
	startTime = TimeTools::getEpochTime();
}


/** Provides current time in seconds. Useful when one needs to get a time-stamp.
 *  Resolution is in microseconds (accuracy might not be as high though).
 * @return seconds since epoch (Jan 1 1970, 00:00:00.000000)
 */
double TimeTools::getEpochTime() {
	struct timeval tv; double sec;
	gettimeofday( &tv, NULL );
	sec = (double)tv.tv_sec + (double) tv.tv_usec/1e6;
	return sec;
}

/** Provides the current time in milliseconds as a long. May be useful
 * for providing integer time-stamps if the actual date/time are not
 * that important. This might be useful for time-stamping packets.
 *
 */
unsigned long TimeTools::msTimer()
{
	unsigned long myTimeIn_ms = (unsigned long long)(TimeTools::getEpochTime() * 1000.0)
					& 0xffffffff;
	return myTimeIn_ms;
}

/** Get the current time in seconds since the epoch */
unsigned long long TimeTools::get_secs()
{
	return 	(unsigned long)TimeTools::getEpochTime();
}

/** Get the relative time since this class was first constructed
 *
 * @return seconds since construction of this TimeTools class instance.
 */
double TimeTools::timeSinceStart() {
	return (TimeTools::getEpochTime() - startTime);
}

}
