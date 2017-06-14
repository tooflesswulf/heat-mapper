#include "ImageProc.h"
#include <vector>

/* Found by binary searching on error codes. Sigh. */
#define LEP_FFC_CMD 0xc
#define LEP_RAD_UNIT 5
#define MAX_RETRIES 2

struct buffer {
	void *start;
	size_t length;
};
static char dev_name[16];
static int videofd = -1;
static std::vector<buffer> buffers;
static unsigned int n_buffers = 0;
static int waserror;
static int width;
static int height;

static bool initmmap(void);
static bool readframe(uint16_t *out);
static void reconnect();

/* Log errors, but be _Q_uiet after a while */
#define QLOGE(...) \
	do { \
		/* show the first 10 error logs around an error */ \
		if (waserror<10) { LOGE(__VA_ARGS__); } \
		waserror++; \
	} while (0)

static bool
xioctl(int fd, int req, void *arg)
{
	int r;

	if (fd == -1)
		return false;
	while (1) {
		r = ioctl(fd, req, arg);
		/* ok! */
		if (r != -1)
			break;
		/* retry! */
		if (errno == EINTR || errno == EAGAIN)
			continue;
		/* barf */
		QLOGE("Lepton: Gone fishing: %s", strerror(errno));
		return false;
	}
	return true;
}

static bool
probedevice(void)
{
	char fbuf[256], rbuf[512];

	/*
	 * I pulled 64 from my ass. In theory, by the time we've allocated the
	 * 64th device, Linux is probably going to go back to allocating
	 * smaller numbers again.
	 */
	for (int i = 0; i < 64; i++) {
		snprintf(fbuf, sizeof fbuf, "/sys/class/video4linux/video%d/name", i);
		int rfd = open(fbuf, O_RDONLY);
		if (rfd == -1)
			continue;
		int n = read(rfd, rbuf, sizeof rbuf - 1);
		close(rfd);
		if (n == -1)
			continue;
		rbuf[n] = 0;
		if (strstr(rbuf, "PureThermal")) {
			snprintf(dev_name, sizeof dev_name, "/dev/video%d", i);
			return true;
		}
	}
	return false;
}

static bool
reopendevice(void)
{
	struct stat st;

	if (!probedevice())
		return false;
	LOGI("Opening camera device %s", dev_name);
	if (stat(dev_name, &st) != 0) {
		LOGI("cannot stat '%s': %s", dev_name, strerror(errno));
		return false;
	}

	if (!S_ISCHR(st.st_mode)) {
		LOGI("%s is not character device", dev_name);
		return false;
	}

	videofd = open(dev_name, O_RDWR | O_NONBLOCK, 0);
	if (videofd == -1) {
		LOGI("unable to open %s: %s", dev_name, strerror(errno));
		return false;
	}
	return true;
}

static int
initdevice(int w, int h)
{
	struct v4l2_capability cap;
	struct v4l2_cropcap cropcap;
	struct v4l2_crop crop;
	struct v4l2_format fmt;
	unsigned int min;

	width  = w;
	height = h;

	LOGI("init device %s", dev_name);
	if (!xioctl(videofd, VIDIOC_QUERYCAP, &cap))
		return false;
	if (!(cap.capabilities & V4L2_CAP_VIDEO_CAPTURE)) {
		LOGE("%s: no video capture capability", dev_name);
		return false;
	}

	if (!(cap.capabilities & V4L2_CAP_STREAMING)) {
		LOGE("%s: no video streaming capability", dev_name);
		return false;
	}

	CLEAR(cropcap);
	cropcap.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;

	if (xioctl(videofd, VIDIOC_CROPCAP, &cropcap) == 0) {
		crop.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
		crop.c    = cropcap.defrect;
		if (!xioctl(videofd, VIDIOC_S_CROP, &crop))
			return false;
	}

	CLEAR(fmt);
	fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
	fmt.fmt.pix.width  = w;
	fmt.fmt.pix.height = h;
	fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_Y16;
	fmt.fmt.pix.field       = V4L2_FIELD_NONE;

	if (!xioctl(videofd, VIDIOC_S_FMT, &fmt))
		return false;

	LOGI("Everything appears to be ok in initdevice()");

	min = fmt.fmt.pix.width * 2;
	if (fmt.fmt.pix.bytesperline < min)
		fmt.fmt.pix.bytesperline = min;
	min				 = fmt.fmt.pix.bytesperline * fmt.fmt.pix.height;
	if (fmt.fmt.pix.sizeimage < min)
		fmt.fmt.pix.sizeimage = min;

	return initmmap();
}

static bool
initmmap(void)
{
	struct v4l2_requestbuffers req;

	CLEAR(req);
	req.count  = 4;
	req.type   = V4L2_BUF_TYPE_VIDEO_CAPTURE;
	req.memory = V4L2_MEMORY_MMAP;

	if (!xioctl(videofd, VIDIOC_REQBUFS, &req))
		return false;
	if (req.count < 2) {
		LOGE("Insufficient buffer memory on %s", dev_name);
		return false;
	}

	buffers.clear();
	for (n_buffers = 0; n_buffers < req.count; ++n_buffers) {
		struct v4l2_buffer buf;

		CLEAR(buf);

		buf.type   = V4L2_BUF_TYPE_VIDEO_CAPTURE;
		buf.memory = V4L2_MEMORY_MMAP;
		buf.index  = n_buffers;

		if (!xioctl(videofd, VIDIOC_QUERYBUF, &buf))
			return false;

		buffer b;
		b.length = buf.length;
		b.start  = mmap(NULL, buf.length, PROT_READ | PROT_WRITE,
				MAP_SHARED, videofd, buf.m.offset);

		if (b.start == MAP_FAILED) {
			LOGE("mmap failed: %s", strerror(errno));
			return false;
		}
		buffers.push_back(b);
		
	}

	return true;
}

static int
startcapturing(void)
{
	unsigned int i;
	enum v4l2_buf_type type;

	QLOGE("start capturing");
	for (i = 0; i < n_buffers; ++i) {
		struct v4l2_buffer buf;

		CLEAR(buf);

		buf.type   = V4L2_BUF_TYPE_VIDEO_CAPTURE;
		buf.memory = V4L2_MEMORY_MMAP;
		buf.index  = i;

		if (!xioctl(videofd, VIDIOC_QBUF, &buf))
			return false;
	}

	type = V4L2_BUF_TYPE_VIDEO_CAPTURE;

	if (!xioctl(videofd, VIDIOC_STREAMON, &type))
		return false;

	return true;
}

bool
readframeonce(uint16_t *buf)
{
	for (int retries = 0; retries < MAX_RETRIES; retries++) {
		if (videofd != -1) {
			fd_set fds;
			struct timeval tv;

			FD_ZERO(&fds);
			FD_SET(videofd, &fds);

			tv.tv_sec  = 1;
			tv.tv_usec = 0;
			int r = select(videofd + 1, &fds, NULL, NULL, &tv);
			if (r > 0 && readframe(buf))
				return true;
			else if (r == -1 && (errno == EINTR || errno == EAGAIN))
				continue;
		}
		QLOGE("Lepton on union mandated leave: %s", strerror(errno));
		reconnect();
	}

	return false;
}

static bool
readframe(uint16_t *out)
{
	struct v4l2_buffer buf;
	unsigned int i;

	CLEAR(buf);

	buf.type   = V4L2_BUF_TYPE_VIDEO_CAPTURE;
	buf.memory = V4L2_MEMORY_MMAP;

	if (!xioctl(videofd, VIDIOC_DQBUF, &buf))
		return false;
	assert(buf.index < n_buffers);
	uint8_t *src = static_cast<uint8_t *>(buffers[buf.index].start);
	for (i = 0; i < width * height * 2; i += 2)
		*out++ = ((uint16_t)src[i + 1] << 8) | src[i];

	if (!xioctl(videofd, VIDIOC_QBUF, &buf))
		return false;

	return true;
}

static int
stopcapturing(void)
{
	enum v4l2_buf_type type;

	type = V4L2_BUF_TYPE_VIDEO_CAPTURE;

	if (!xioctl(videofd, VIDIOC_STREAMOFF, &type))
		return false;

	return true;
}

static int
uninitdevice(void)
{
	unsigned int i;

	/* we can never fail here -- there's no recovery */
	for (i = 0; i < n_buffers; ++i) {
		munmap(buffers[i].start, buffers[i].length);
	}
	return true;
}

static int
closedevice(void)
{
	close(videofd);
	videofd = -1;
	return true;
}

static int
ffc(void)
{
	uvc_xu_control_query q;
	uint8_t c;

	q.unit     = LEP_RAD_UNIT;
	q.query    = UVC_SET_CUR;
	q.selector = LEP_FFC_CMD;
	q.size     = 1;
	q.data     = &c;

	for (int retries = 0; retries < MAX_RETRIES; retries++) {
		if (xioctl(videofd, UVCIOC_CTRL_QUERY, &q))
			break;
		QLOGE("USB failed: %s -- Reconnecting", strerror(errno));
		reconnect();
	}
	LOGI("FFC done");
	return 1;
}

void
reconnect()
{
	/* close down devices */
	LOGI("Reconnect: Shut down existing connections");
	stopcapturing();
	uninitdevice();
	closedevice();

	LOGI("Reconnect: reopen device");
	if (!reopendevice())
		return;
	if (!initdevice(width, height))
		return;
	if (!startcapturing())
		return;
	waserror = 0;
}

int
initLepton(int w, int h)
{
	width  = w;
	height = h;
	LOGI("reconnecting to camera at %dx%d", w, h);
	reconnect();
	return 1;
}

int
waitFrame( void )
{
	while (1) {
		if (videofd == -1)
			return 0;
		fd_set fds;
		struct timeval tv;
		FD_ZERO(&fds);
		FD_SET(videofd, &fds);
		tv.tv_sec  = 1;
		tv.tv_usec = 0;
		int r = select(videofd + 1, &fds, NULL, NULL, &tv);
		if (r != -1)
			return 1;
		if (r == -1 && errno != EAGAIN && errno != EINTR)
			return 0;
	}
}

int
leptonFfc(void)
{
	return ffc();
}

void
deinit()
{
	/* No error checking -- it may already be gone */
	stopcapturing();
	uninitdevice();
	closedevice();
	videofd = -1;
}
