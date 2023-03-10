""" CS4243 Lab 1: Template Matching
"""

import os
import cv2
import random
import numpy as np
import matplotlib.pyplot as plt
import math

##### Part 1: Image Preprossessing #####

def rgb2gray(img):
    """
    5 points
    Convert a colour image greyscale
    Use (R,G,B)=(0.299, 0.587, 0.114) as the weights for red, green and blue channels respectively
    :param img: numpy.ndarray (dtype: np.uint8)
    :return img_gray: numpy.ndarray (dtype:np.uint8)
    """
    if len(img.shape) != 3:
        print('RGB Image should have 3 channels')
        return
    
    """ Your code starts here """
    channel_weights = (0.299, 0.587, 0.114)
    img_gray = np.dot(img, channel_weights)
    """ Your code ends here """
    return img_gray


def gray2grad(img):
    """
    5 points
    Estimate the gradient map from the grayscale images by convolving with Sobel filters (horizontal and vertical gradients) and Sobel-like filters (gradients oriented at 45 and 135 degrees)
    The coefficients of Sobel filters are provided in the code below.
    :param img: numpy.ndarray
    :return img_grad_h: horizontal gradient map. numpy.ndarray
    :return img_grad_v: vertical gradient map. numpy.ndarray
    :return img_grad_d1: diagonal gradient map 1. numpy.ndarray
    :return img_grad_d2: diagonal gradient map 2. numpy.ndarray
    """
    sobelh = np.array([[-1, 0, 1], 
                       [-2, 0, 2], 
                       [-1, 0, 1]], dtype = float)
    sobelv = np.array([[-1, -2, -1], 
                       [0, 0, 0], 
                       [1, 2, 1]], dtype = float)
    sobeld1 = np.array([[-2, -1, 0],
                        [-1, 0, 1],
                        [0,  1, 2]], dtype = float)
    sobeld2 = np.array([[0, -1, -2],
                        [1, 0, -1],
                        [2, 1, 0]], dtype = float)
    

    """ Your code starts here """
    def convolve2d(kernel):
        #TODO: stop cheating with scipy lmao
        import scipy.signal as sig
        return sig.convolve2d(img, kernel, mode="same")

    img_grad_h, img_grad_v, img_grad_d1, img_grad_d2 = map(convolve2d, (sobelh, sobelv, sobeld1, sobeld2))

    """ Your code ends here """
    return img_grad_h, img_grad_v, img_grad_d1, img_grad_d2

def pad_zeros(img, pad_height_bef, pad_height_aft, pad_width_bef, pad_width_aft):
    """
    5 points
    Add a border of zeros around the input images so that the output size will match the input size after a convolution or cross-correlation operation.
    e.g., given matrix [[1]] with pad_height_bef=1, pad_height_aft=2, pad_width_bef=3 and pad_width_aft=4, obtains:
    [[0 0 0 0 0 0 0 0]
    [0 0 0 1 0 0 0 0]
    [0 0 0 0 0 0 0 0]
    [0 0 0 0 0 0 0 0]]
    :param img: numpy.ndarray
    :param pad_height_bef: int
    :param pad_height_aft: int
    :param pad_width_bef: int
    :param pad_width_aft: int
    :return img_pad: numpy.ndarray. dtype is the same as the input img. 
    """
    height, width = img.shape[:2]
    new_height, new_width = (height + pad_height_bef + pad_height_aft), (width + pad_width_bef + pad_width_aft)
    img_pad = np.zeros((new_height, new_width)) if len(img.shape) == 2 else np.zeros((new_height, new_width, img.shape[2]))

    """ Your code starts here """
    img_pad[pad_height_bef:pad_height_bef+height, pad_width_bef:pad_width_bef+width] = img
    """ Your code ends here """
    return img_pad




##### Part 2: Normalized Cross Correlation #####
def normalized_cross_correlation(img, template):
    """
    10 points.
    Implement the cross-correlation operation in a naive 4, 5 or 6 nested for-loops. 
    The loops should at least include the height and width of the output and height and width of the template.
    When it is 5 or 6 loops, the channel of the output and template may be included.
    :param img: numpy.ndarray.
    :param template: numpy.ndarray.
    :return response: numpy.ndarray. dtype: float
    """
    Hi, Wi = img.shape[:2]
    Hk, Wk = template.shape[:2]
    Ho = Hi - Hk + 1
    Wo = Wi - Wk + 1

    """ Your code starts here """
    n_colors = img.shape[2] if len(img.shape) == 3 else 1
    response = np.zeros(shape=(Ho, Wo))
    template_scaled = np.divide(template, np.sum(template))
    
    filter_magnitude = np.linalg.norm(template_scaled)
    
    for i in range(Ho):
        for j in range(Wo):
            input_window = img[i:i + Hk, j:j + Wk]
            input_window_magnitude = np.linalg.norm(input_window)
            for ti in range(Hk):
                for tj in range(Wk):
                    if n_colors == 1:
                        response[i][j] += input_window[ti][tj] * template_scaled[ti][tj] / (filter_magnitude * input_window_magnitude)
                    else:
                        for k in range(n_colors):
                            response[i][j] += input_window[ti][tj][k] * template_scaled[ti][tj][k] / (filter_magnitude * input_window_magnitude)
    """ Your code ends here """
    return response


def normalized_cross_correlation_fast(img, template):
    """
    10 points.
    Implement the cross correlation with 3 nested for-loops. 
    The for-loop over the template is replaced with the element-wise multiplication between the kernel and the image regions.
    :param img: numpy.ndarray
    :param template: numpy.ndarray
    :return response: numpy.ndarray. dtype: float
    """
    Hi, Wi = img.shape[:2]
    Hk, Wk = template.shape[:2]
    Ho = Hi - Hk + 1
    Wo = Wi - Wk + 1

    """ Your code starts here """
    n_colors = img.shape[2] if len(img.shape) == 3 else 1
    response = np.zeros(shape=(Ho, Wo))
    template_scaled = np.divide(template, np.sum(template))
    filter_magnitude = np.linalg.norm(template_scaled)
    
    for i in range(Ho):
        for j in range(Wo):
            input_window = img[i:i + Hk, j:j + Wk]
            input_window_magnitude = np.linalg.norm(input_window)
            if n_colors == 1:
                response[i,j] += np.sum(np.multiply(input_window[:,:], template_scaled[:,:])) / (filter_magnitude * input_window_magnitude)
            else:
                for k in range(n_colors):
                    response[i,j] += np.sum(np.multiply(input_window[:,:,k], template_scaled[:,:,k])) / (filter_magnitude * input_window_magnitude)
    """ Your code ends here """
    return response




def normalized_cross_correlation_matrix(img, template):
    """
    10 points.
    Converts cross-correlation into a matrix multiplication operation to leverage optimized matrix operations.
    Please check the detailed instructions in the pdf file.
    :param img: numpy.ndarray
    :param template: numpy.ndarray
    :return response: numpy.ndarray. dtype: float
    """
    Hi, Wi = img.shape[:2]
    Hk, Wk = template.shape[:2]
    Ho = Hi - Hk + 1
    Wo = Wi - Wk + 1
    """ Your code starts here """
    n_colors = img.shape[2] if len(img.shape) == 3 else 1
    template_scaled = np.divide(template, np.sum(template))
    reshape_multiple_color = lambda x, i, j: np.concatenate([x[i:i + Hk, j:j + Wk,k].flatten() for k in range(n_colors)])
    reshape_one_color = lambda x, i, j: x[i:i + Hk, j:j + Wk].flatten()
    reshape_matrix = reshape_one_color if n_colors == 1 else reshape_multiple_color
    normalize_matrix = lambda x: np.divide(x, np.linalg.norm(x))
    pr = np.stack([normalize_matrix(reshape_matrix(img, i, j)) for i in range(Ho) for j in range(Wo)])
    fr = normalize_matrix(reshape_matrix(template_scaled, 0, 0))
    frt = np.atleast_2d(fr).T
    response = np.matmul(pr, frt).reshape(Ho, Wo)
    """ Your code ends here """
    return response


##### Part 3: Non-maximum Suppression #####

def non_max_suppression(response, suppress_range, threshold=None):
    """
    10 points
    Implement the non-maximum suppression for translation symmetry detection
    The general approach for non-maximum suppression is as follows:
	1. Set a threshold ??; values in X<?? will not be considered.  Set X<?? to 0.  
    2. While there are non-zero values in X
        a. Find the global maximum in X and record the coordinates as a local maximum.
        b. Set a small window of size w??w points centered on the found maximum to 0.
	3. Return all recorded coordinates as the local maximum.
    :param response: numpy.ndarray, output from the normalized cross correlation
    :param suppress_range: a tuple of two ints (H_range, W_range). 
                           the points around the local maximum point within this range are set as 0. In this case, there are 2*H_range*2*W_range points including the local maxima are set to 0
    :param threshold: int, points with value less than the threshold are set to 0
    :return res: a sparse response map which has the same shape as response
    """
    
    """ Your code starts here """
    h, w = response.shape
    for i in range(h):
        for j in range(w):
            if response[i,j] < threshold:
                response[i,j] = 0
    non_zeros_present = True
    res = np.zeros(shape=(h,w))
    count = 0
    while non_zeros_present:
        count += 1
        maxI = -1
        maxJ = -1
        maxValue = 0
        for i in range(h):
            for j in range(w):
                if response[i,j] > maxValue:
                    maxI = i
                    maxJ = j
                    maxValue = response[i,j]
        if maxValue == 0:
            non_zeros_present = False
        else:
            res[maxI,maxJ] = response[maxI,maxJ]
            startI = max(maxI - suppress_range[0],0)
            endI = min(maxI + suppress_range[0], h - 1)
            startJ = max(maxJ - suppress_range[1], 0)
            endJ = min(maxJ + suppress_range[1], w - 1)
            for i in range(startI, endI + 1):
                for j in range(startJ, endJ + 1):
                    response[i,j] = 0
            
    """ Your code ends here """
    return res

##### Part 4: Question And Answer #####
    
def normalized_cross_correlation_ms(img, template):
    """
    10 points
    Please implement mean-subtracted cross correlation which corresponds to OpenCV TM_CCOEFF_NORMED.
    For simplicty, use the "fast" version.
    :param img: numpy.ndarray
    :param template: numpy.ndarray
    :return response: numpy.ndarray. dtype: float
    """
    Hi, Wi = img.shape[:2]
    Hk, Wk = template.shape[:2]
    Ho = Hi - Hk + 1
    Wo = Wi - Wk + 1

    """ Your code starts here """

    """ Your code ends here """
    return response




"""Helper functions: You should not have to touch the following functions.
"""
def read_img(filename):
    '''
    Read HxWxC image from the given filename
    :return img: numpy.ndarray, size (H, W, C) for RGB. The value is between [0, 255].
    '''
    img = cv2.imread(filename)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def show_imgs(imgs, titles=None):
    '''
    Display a list of images in the notebook cell.
    :param imgs: a list of images or a single image
    '''
    if isinstance(imgs, list) and len(imgs) != 1:
        n = len(imgs)
        fig, axs = plt.subplots(1, n, figsize=(15,15))
        for i in range(n):
            axs[i].imshow(imgs[i], cmap='gray' if len(imgs[i].shape) == 2 else None)
            if titles is not None:
                axs[i].set_title(titles[i])
    else:
        img = imgs[0] if (isinstance(imgs, list) and len(imgs) == 1) else imgs
        plt.figure()
        plt.imshow(img, cmap='gray' if len(img.shape) == 2 else None)

def show_img_with_points(response, img_ori=None):
    '''
    Draw small red rectangles of size defined by rec_shape around the non-zero points in the image.
    Display the rectangles and the image with rectangles in the notebook cell.
    :param response: numpy.ndarray. The input response should be a very sparse image with most of points as 0.
                     The response map is from the non-maximum suppression.
    :param img_ori: numpy.ndarray. The original image where response is computed from
    :param rec_shape: a tuple of 2 ints. The size of the red rectangles.
    '''
    response = response.copy()
    if img_ori is not None:
        img_ori = img_ori.copy()

    xs, ys = response.nonzero()
    for x, y in zip(xs, ys):
        response = cv2.circle(response, (y, x), radius=0, color=(255, 0, 0), thickness=5)
        if img_ori is not None:
            img_ori = cv2.circle(img_ori, (y, x), radius=0, color=(255, 0, 0), thickness=5)
        
    if img_ori is not None:
        show_imgs([response, img_ori])
    else:
        show_imgs(response)


