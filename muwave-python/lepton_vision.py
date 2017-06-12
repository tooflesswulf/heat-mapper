import os
import numpy as np
os.chdir(os.path.abspath('../mu-wave-control/'))
import struct
import matplotlib.pyplot as plt
import time
import lepton_util as lu
import cv2

image_array = lu.import_the_run("","MyLepton")
def create_list_of_run_ellipses(run_array, threshold_cut, area_cut):
    """This function takes a lepton array, a threshold and an area in pixels 
    it returns a list of lists, where the sublist is all the bounding ellipses
    of contours bigger than the input area and having a pixel value bigger than
    the threshold. The threshold is between 0 and 1 with the lepton images being
    0-255 pixel values."""
    m = len(run_array)
    run_ellipses = []
    for i in np.arange(m):
        if (run_array[i]['frame high value'] - run_array[i]['frame low value']) < 35:
            run_ellipses.append("Approximate flat image.")
            continue
        image = run_array[i]['img-pixels'].copy()
        image_mean = np.mean(image)
        image_std = np.std(image)
        image = (image - image_mean)/image_std
        ret, thresh = cv2.threshold((image).astype(np.float32), threshold_cut, 1, cv2.THRESH_BINARY)
        contours, heirarchy = cv2.findContours((thresh*255).astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) == 0:
            run_ellipses.append( "No contours found")
            #print "No contours found at frame", i + 1
            continue
        ellipses = []
        l = len(contours)
        for j in np.arange(l):
            if len(contours[j]) < 5:
                #print "Contour not big enough for ellipse fit in frame ", i + 1 
                continue
            else:
                ellipses.append(cv2.fitEllipse(contours[j]))
                #print "filling ellipse list."
            
        ellipses = [x for x in ellipses if x[1][0]*x[1][1]*np.pi/4. > area_cut ]
        ellipses = [x for x in ellipses if (0. < x[1][0] and x[1][0] < 80.)]
        ellipses = [x for x in ellipses if (0. < x[1][1] and x[1][1] < 60.)]
        if len(ellipses) == 0: 
            run_ellipses.append( "No ellipses big enough to pass cut.")
            #print "No ellipses big enough to pass cut."
            continue
        else:    
            run_ellipses.append( ellipses)
    
    return run_ellipses

def get_ellipse_temperature(array, frame_number, ellipse):
    """Takes a lepton array, frame number and ellipse as arguments and returns
    the average temperature, in celsius of the pixels in the ellipse. """
    img = np.zeros_like(array[frame_number]['img-pixels']).astype(np.uint8)
    cv2.ellipse(img, ellipse, 255, -1)
    inside_contour = np.where(img == 255)
    num_points_inside_contour = len(inside_contour[0])
    if num_points_inside_contour == 0: 
        print "zero div at " , frame_number
    pixel_inside_contour_sum = 0
    for i in np.arange(num_points_inside_contour):
        pixel_inside_contour_sum += lu.get_temp_in_rad_mode(array[inside_contour[0][i] , inside_contour[1][i]])
        
    return pixel_inside_contour_sum/num_points_inside_contour

def get_list_of_ellipse_temperatures(array, threshold_cut, area_cut):
    """Takes a lepton array a threshold and an area and returns a list of
    lists, where the sublist is a list of all ellipses in a frame an their 
    average temperatures. """
    ellipse_list = create_list_of_run_ellipses(array, threshold_cut, area_cut)
    ellipse_temp_list = []
    for idx, ellipses in enumerate(ellipse_list):
        elip = []
        for ellipse in ellipses:
            if type(ellipse) == tuple:
                elip.append(ellipse + (get_ellipse_temperature(array, idx , ellipse),))
            elif type(ellipse) == str:
                continue
            else:
                print "Unsupported data type in ellipse list."
        if len(elip) == 0:
            ellipse_temp_list.append("No ellipses found.")
        else:
            ellipse_temp_list.append(elip)
            
    return ellipse_temp_list

def plot_image_and_ellipse(array, ellipse_temp_list, frame_number):
    """Takes a lepton array, a list create by get_list_of_ellipse_temperatures
     and a frame number. It plots the original image alongside a black image
     with only the ellipses found. It also prints the temperature af the ellipses."""
    #fig = plt.figure(figsize=(8,12),edgecolor=None)
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8,12))
    #plt.subplot()
    axes[0].imshow(array[frame_number - 1]['img-pixels'])
    axes[0].set_title('Lepton Image')
    ellipse_image = np.zeros((60,80))
    for ellipse in ellipse_temp_list[frame_number-1]:
        cv2.ellipse(ellipse_image, ellipse[:-1], 255, 1)
    
    axes[1].imshow(ellipse_image, cmap= 'gray')
    axes[1].set_title('Centered ellipses.')
    
    print len(ellipse_temp_list[frame_number-1]) , " ellipses found."
    for idx, ellipse in enumerate(ellipse_temp_list[frame_number-1]):
        print "Ellipse", idx + 1, ": centered at ", '%.1f'%ellipse[0][1], '%.1f'%ellipse[0][0], "with temperature " , '%.3f'%ellipse[-1] 

def get_array_of_temperatures_vs_time(path, file_name, circle_tuple=((30,40), 9)):
    """Takes the path and file name of a muwave run and returns an array of the temperatures
    of a circle, defaults @ 30, 40 with radius 9, as well as arrays of times of the temps, 
    frame numbers and if the muwave was on/off
    of the original run file.
    Return ->  array_of_temp, array_of_time, array_of_frames, array_of_muwaveOnOff"""
    array = lu.import_the_run(path, file_name)

    auto_circle_int = circle_tuple

    blank_image = np.zeros((60,80))
    cv2.circle(blank_image, auto_circle_int[0], auto_circle_int[1]/2, 255 , -1)
    auto_circle_points = np.append(np.where(blank_image == 255)[1], np.where(blank_image == 255)[0]).reshape(2, -1).transpose()

    array_of_auto_temps_blur = []
    array_of_times = []
    array_of_frames= []
    array_of_muwave_OnOff = []
    for j in np.arange(len(array)):
        auto_temps_blur = []
        if j % 10 == 0:
            for i in np.arange(len(auto_circle_points)):
                auto_temps_blur.append(get_temperature_from_raw_lepton(array[j]['temp'], cv2.GaussianBlur(array[j]['img-pixels'],(5,5),5)[tuple(auto_circle_points[i][::-1])]))

            #array_of_temps3.append(temps3)
            array_of_auto_temps_blur.append(auto_temps_blur)
            array_of_times.append(array['time'][j])
            array_of_frames.append(j)
            array_of_muwave_OnOff.append(array['muwaveOn'][j])
        else:
            continue

    array_of_times = np.array(array_of_times)
    array_of_temps = np.array([np.mean(array_of) for array_of in array_of_auto_temps_blur])
    array_of_frames = np.array(array_of_frames)
    array_of_muwave_OnOff = np.array(array_of_muwave_OnOff)

    return array_of_temps, array_of_times, array_of_frames, array_of_muwave_OnOff




