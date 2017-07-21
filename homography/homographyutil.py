import numpy as np
import cv2
from sklearn.cluster import KMeans
from matplotlib.colors import rgb_to_hsv
import matplotlib.pyplot as plt


# Generates a rotation matrix for some angle theta.
# @arg: theta - the angle to rotate by
# @return: mat - the 2x2 rotation matrix.
def rot_mat(theta):
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array([[c,-s],[s,c]])


# Converts lines in a (rho, theta) format to a point-slope form.
# @arg: lines - an array of lines. Has shape (n, 2)
# @return: newlines - the same array of lines, just represented differently. Has shape (n, 2, 2)
def pts_rt2xy(lines):
    lines = np.array(lines)
    rho = lines[...,0]
    theta = lines[...,1]
    pt = rho * np.array([np.cos(theta), np.sin(theta)])
    n = np.array([-np.sin(theta), np.cos(theta)])

    newlines = np.dstack([pt, n]).transpose(1,2,0)
    return newlines


# Find the best intersecting point of many lines.
# @param lines - an array of lines in (rho, theta) format
# @return: pt - returns an (x, y) point that is the closest intersection between all the lines.
def get_intersection(lines):
    r = np.zeros((2,2))
    q = np.zeros((2,1))
    
    xylines = pts_rt2xy(lines)
    I = np.array([[1,0],[0,1]])
    for pt, n in xylines:
        n = n.reshape(2,1)
        r_i = I - np.matmul(n, n.T)
        q_i = np.matmul(r_i, pt.reshape(2,1))
        r += r_i
        q += q_i
    return np.matmul(np.linalg.pinv(r), q).reshape(2)


# Finds the edges of a mask.
# @param ms - the mask to find the edges of
# @param nlargest - only find edges of the n largest masks to reduce the effect of noise.
# @param dilate_size - returns lines of some width, to help the line-finder do its job better.
# @return: edges - An image similar to the mask, but with only the edges.
def get_mask_edges(ms, nlargest=2, dilate_size=(3,3)):
    ret, markers = cv2.connectedComponents(ms)
    _, counts = np.unique(markers, return_counts=True)
    counts[0] = 0

    ms = np.zeros_like(ms)
    for i in np.argsort(counts)[-nlargest:]:
        ms[markers == i] = 1

    edges = cv2.Canny(ms,0,1)
    edges = cv2.dilate(edges, np.ones(dilate_size))
    return edges


# Finds the intersection between a set of lines and an image. It selects only pixels close enough to any line
#  in <lines>; all other pixels are set to 0.  Also, it will label the pixels according to how the lines are labeled.
# @param edges - The image to match the lines to.
# @param avglines - The lines to match the image with.
# @param line_width - describes how close a pixel has to be to a line to be considered matching.
# @return: dummy_im - the image of matching lines. Each line will also be labeled according to 
def render_lines_on_image(edges, avglines, line_width = 1):
    rot = [[0,1],[-1,0]]

    xylines = pts_rt2xy(avglines)
    dummy_im = np.zeros_like(edges)
    for pix in np.argwhere(edges!=0):
        y, x = pix
        # px = pix[::-1]

        pts = xylines[:,0,:]
        ns = xylines[:,1,:]

        perps = np.matmul(ns, rot)
        dot = np.sum((pts - [x, y]) * perps, axis=1)
        dists = np.abs(dot)

        for i in np.argwhere(dists < line_width):
            dummy_im[y, x] = i+1
    return dummy_im


# Returns the ratio of the distance of the detected top and bottom of the cans to the vanishing point.
# @param dummy_im - the image with labeled lines.
# @param lines - the lines matched with the lines on the image.
# @param labels - the labels that match the lines with the image.
# @param vp - the vanishing point of the image.
# @returns: ratios - the ratios of each line (should be 4)
# @returns: endpt_list - the detected endpoints of each line (used for debugging.)
def get_endpt_ratios(dummy_im, avglines, vp):    
    u = np.unique(dummy_im)[1:]
    ratios = []
    endpt_list = []
    for lab, (rho ,theta) in zip(u, avglines):
        pts = np.argwhere(dummy_im == lab)
        # rho, theta = lines[ix]
        rot_pts = np.matmul(pts, rot_mat(-theta))
        minx = np.amin(rot_pts[:,0])
        maxx = np.amax(rot_pts[:,0])
        y = np.mean(rot_pts[:,1])
        pts2 = np.array([(minx, y), (maxx, y)])
        endpts = np.matmul(pts2, rot_mat(theta))
        endpts = endpts[:,[1,0]]

        dists = np.linalg.norm(endpts - vp.T, axis=1)

        d1, d2 = np.amin(dists), np.amax(dists)
        ratios.append(1/(1-d1/d2))

        endpt_list.append(endpts)
    return ratios, np.array(endpt_list)


# Wraps up many functions into one function call to get the ratio and vanishing point of a mask of the cans.
# @param ms - the mask to operate on
# @param imtype - either visual or lepton image, used for selecting some camera constants.
# @param debug - boolean for determining whether to return a bunch of extra info.
# @returns: ratios, vp - the information for 
def get_ratios_from_mask(ms, imtype, debug=False):
    assert imtype in ['vis', 'lept'], '`imtype` {} is invalid.'.format(imtype)
    if imtype == 'vis':
        mhc = 130
        lw = 3
    elif imtype == 'lept':
        mhc = 50
        lw = .5

    edges = get_mask_edges(ms)

    lines = cv2.HoughLines(edges,1,np.pi/180,mhc)
    lines = lines[:,0]

    kmeans = KMeans(n_clusters=4).fit(lines)

    labels = kmeans.labels_
    vp = get_intersection(lines)

    avglines = []
    for lab in np.unique(labels):
        avglines.append(np.mean(lines[labels==lab], axis=0))

    dummy_im = render_lines_on_image(edges, avglines, line_width=lw)
    ratios, endpts = get_endpt_ratios(dummy_im, avglines, vp)
    if debug:
        return ratios, vp, endpts, (edges, lines, labels)
    return ratios, vp, endpts


# Creates a mask for a visual image of the orange cans.
def vis_can_mask(visimg):
    hsv_im = rgb_to_hsv(visimg)
    m1 = .0 < hsv_im[...,0]  # Emperically determined `hue` values for orange.
    m2 = hsv_im[...,0] < .08
    m3 = hsv_im[...,1] > .3  # Minimum saturation.
    ms = m1 & m2 & m3

    ms = ms.astype(np.uint8)
    return ms


# Creates a mask for the lepton image of the cold cans.
def lept_can_mask(leptimg):
    ret, thresh = cv2.threshold(leptimg.astype(np.uint8), 0, 1, cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV)
    return thresh


# Creates a splice of a mask centered on a particular label such that the label fills the new image.
# Also returns the splice's location and details.
def zoom_on_label(labeled_mask, label):
    locs = np.argwhere(labeled_mask == label)
    minx, miny = np.amin(locs, axis=0)
    maxx, maxy = np.amax(locs, axis=0)
    return labeled_mask[minx-5:5+maxx, miny-5:5+maxy], (minx, maxx), (miny, maxy)


def get_tile_corners(labeled_mask):
    corners = []
    for label in np.unique(labeled_mask)[1:]:
        roi, (minx, maxx), (miny, maxy) = zoom_on_label(labeled_mask, label)
        
        im, contours, hierarchy = cv2.findContours(roi.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    
        epsilon = 0.1*cv2.arcLength(contours[0],True)
        corn_pts = cv2.approxPolyDP(contours[0],epsilon,True)
        corn_pts = corn_pts.reshape(4,2)

        corners.append(corn_pts + [miny-5, minx-5])
    return np.array(corners)


# Creats a mask for the visual image of the 6-tile calibration device.
def vis_tile_mask(visimg, return_labels=True):
    mask = np.sum(visimg > [230,235,230], axis=-1)==3
    mask = mask.astype(np.uint8)

    kernel = np.ones((5,5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    ret, markers = cv2.connectedComponents(mask)

    _, counts = np.unique(markers, return_counts=True)
    counts[0] = 0

    cleanmask = np.zeros_like(markers)
    for i in np.argsort(counts)[-6:]:
        cleanmask[markers==i] = 1

    if return_labels:
        return markers * cleanmask
    return cleanmask


# Creates a mask for the lepton image of the 6-tile calibration device.
def lept_tile_mask(leptimg, return_labels=True):
    img = cv2.resize(leptimg, (0,0), fx=2, fy=2)
    img2 = img.copy()

    img2[img2 < np.nanmean(img2)] = np.nan
    img2[img2 < np.nanmean(img2)] = np.nan
    mask = ~np.isnan(img2)

    ret, markers = cv2.connectedComponents(mask.astype(np.uint8))

    blob_temps = []
    for i in np.unique(markers):
        mean_temp = np.mean(img[markers == i])
        blob_temps.append(mean_temp)

    labeled_mask = np.zeros_like(markers)
    for i in np.argsort(blob_temps)[-6:]:
        if return_labels:
            labeled_mask[markers==i] = i
        else:
            labeled_mask[markers==i] = 1

    return labeled_mask


# Orders a bunch of points given some x-divisions and y-divisions.
# returns the order that would make the points follow a pattern like:
#    _____
#   | 0 1 |
#   | 2 3 |
#   |_4_5_|
# Also, if the points dont completely fall in the boundaries, they will be marked with a -1.
def classify_pts(pts, xdivs, ydivs):
    def gen_upper_lower_bounds(divs):
        divs = np.sort(divs)
        lb = np.concatenate([[-np.inf], divs], axis=0)
        ub = np.concatenate([divs, [np.inf]], axis=0)
        return zip(lb, ub)
    
    order = []
    for yl, yu in gen_upper_lower_bounds(ydivs):
        for xl, xu in gen_upper_lower_bounds(xdivs):
            order.append(-1)
            for k, pt in enumerate(pts):
                xpt = pt[...,0]
                ypt = pt[...,1]
                tot = (xl<xpt) & (xpt<xu) & (yl<ypt) & (ypt<yu)
                if np.all(tot):
                    order[-1] = k
                    break
    return np.array(order, dtype=int)


# Determines the order of the squares and also the order of the squares.
# @param init_pts - a (6,4,2) array that represents each square(6) and their corners(4,2).
# @returns: order(6) - the order that the squares should go in.
# @returns: sq_orders(6,4) - the order that the corners should go in. Each square has its own order of 4.
def align(init_pts, ref_pt, imshape):
    xrange = imshape[1]
    yrange = imshape[0]

    center = np.mean(init_pts.reshape(-1,2), axis=0)
    shift = init_pts - center
    targ_ang = np.pi/2
    tx, ty = ref_pt - center
    M = rot_mat(targ_ang - np.arctan2(ty, tx))
    shift = np.matmul(shift, M)
    
    ydiv = [yrange/8, -yrange/8]
    xdiv = [0]
    order = classify_pts(shift, xdiv, ydiv)
        
    sq_orders = []
    for pts in shift:
        zeroed = pts-np.mean(pts, axis=-2)
        sq_orders.append(classify_pts(zeroed, [0], [0]))
    sq_orders = np.array(sq_orders)

    return order, sq_orders


# Parses the orders and points to align the 
def match_orders(points, square_orders, order):
    sortord = order[order!=-1]

    new_points = []
    for pts, sqo in zip(points[sortord], square_orders[sortord]):
        new_points.append(pts[sqo])
    return np.array(new_points)


class HomographyGen:
    def __init__(self, vis_can_img, lept_can_img, vis_tile_img, lept_tile_img, debug=True):
        corns = get_tile_corners(vis_tile_mask(vis_tile_img))
        assert corns.shape == (6,4,2), 'Error in generating tile corners on visual image.'
        if debug:
            plt.subplot(221)
            plt.scatter(*corns.reshape(-1, 2).T, c='r')
            plt.imshow(vis_tile_img)
        vp = corns

        vis_mask = vis_can_mask(vis_can_img)
        vis_ratios, vis_vp, endpts = get_ratios_from_mask(vis_mask, imtype='vis')
        if debug:
            plt.subplot(222)
            plt.scatter(*vis_vp)
            plt.scatter(*endpts.T)
            plt.imshow(vis_can_img)

        vr, vv = np.mean(vis_ratios), vis_vp

        corns = get_tile_corners(lept_tile_mask(lept_tile_img)) / 2
        if debug:
            plt.subplot(223)
            plt.scatter(*corns.reshape(-1, 2).T, c='r')
            plt.imshow(lept_tile_img)
        lp = corns

        lep_ratios, lep_vp, endpts = get_ratios_from_mask(lept_can_mask(lept_can_img), imtype='lept')
        if debug:
            plt.subplot(224)
            plt.scatter(*lep_vp)
            plt.scatter(*endpts.T)
            plt.imshow(lept_can_img)
        lr, lv = np.mean(lep_ratios), lep_vp
        self.value_init(vis_vp, lep_vp, vr, lr, vp, lp)

    def value_init(self, vis_vanish, lept_vanish, vis_ratio, lept_ratio, vis_pts, lept_pts):
        can_height = 147.34# mm

        self.vv = vis_vanish.T
        self.lv = lept_vanish.T
        self.vf = vis_ratio * can_height
        self.lf = lept_ratio * can_height

        vis_shape = (480,640)
        lept_shape = (120,160)

        vis_order, vis_square_order = align(vis_pts, vis_vanish, vis_shape)
        lept_order, lept_square_order = align(lept_pts, lept_vanish, lept_shape)

        del_mask = (vis_order==-1) | (lept_order==-1)
        vis_order[del_mask] = -1
        lept_order[del_mask] = -1

        self.vpts = match_orders(vis_pts, vis_square_order, vis_order)
        self.lpts = match_orders(lept_pts, lept_square_order, lept_order)
    
    def send(self, h, return_success=False):
        lept_shifted = self.lf/(self.lf - h) * (self.lpts-self.lv) + self.lv
        vis_shifted = self.vf/(self.vf - h) * (self.vpts-self.vv) + self.vv

        H, success = cv2.findHomography(lept_shifted.reshape(-1,2), vis_shifted.reshape(-1,2))
        if return_success:
            return H, success
        return H
