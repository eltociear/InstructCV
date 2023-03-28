import numpy as np
import numpy.ma as ma
from PIL import Image
import pdb
import cv2
from torchvision import transforms
from sklearn.metrics import mean_squared_error
from math import sqrt
from fnmatch import fnmatch
import math
import os

def absolute_mean_relative_error(pred, gt):
    """
    Calculate the absolute mean relative error (AMRE) between two arrays.
    
    Parameters:
    y_true (numpy.ndarray): Array of true values.
    y_pred (numpy.ndarray): Array of predicted values.
    
    Returns:
    float: AMRE between y_true and y_pred.
    """
    epsilon = 10e-6
    
    # Calculate the relative errors
    relative_errors = np.abs((gt - pred) / (gt + epsilon))
    
    # Calculate the AMRE
    amre = np.mean(relative_errors)
    
    return amre


def read_gt_img(img_name):
    
    img = Image.open(img_name)
    
    h, w = img.size

    np_img = np.array(img)
    np_img = np.asarray([np_img], dtype=float)
    
    return np_img, h, w

def read_pred_img(img_name, h, w):
    
    img = Image.open(img_name)
    
    resize = transforms.Resize([w,h])
    img = resize(img)
    
    np_img = np.array(img)
    np_img[np_img<10] = 0
    np_img = np.asarray([np_img], dtype=float)
    
    return np_img

def compute_errors(gt, pred):
    '''
    Modified by Yulu Gan. 13, March, 2023
    Ignore noise
    '''

    # remove noise areas (noise caused by the camera)
    gen                     = np.ones(gt.shape)
    flag                    = np.bitwise_and(gen.astype(np.uint8), gt.astype(np.uint8))
    flag                    = np.bitwise_and(flag.astype(np.uint8), pred.astype(np.uint8))
    gt_new                  = flag * gt
    pred_new                = flag * pred
    
    mask                    = (abs(gt_new)<=10e-4).astype(int).astype(np.float64)
    gt_new_nozero           = mask + gt_new # 0 -> 1
    pred_new_nozero         = mask + pred_new

    
    thresh                  = np.maximum((gt_new_nozero / pred_new_nozero), (pred_new_nozero / gt_new_nozero))
    a1                      = (thresh < 1.25   ).mean()
    a2                      = (thresh < 1.25 ** 2).mean()
    a3                      = (thresh < 1.25 ** 3).mean()
    abs_rel                 = np.mean(np.abs(gt_new_nozero - pred_new_nozero) / gt_new_nozero)
    
    rmse                    = (gt_new - pred_new) ** 2
    rmse                    = np.sqrt(rmse.mean())
    
    return dict(a1=a1, a2=a2, a3=a3, 
                abs_rel=abs_rel, rmse=rmse)
    
    
if __name__ == "__main__":
    
    test_path = "./data/image_pairs_evaluation_dep"
    file_name = os.listdir(test_path)
    rmse_l    = []
    a1_l        = []
    abs_rel_l   = []
    
    for file in file_name:
        
        img_list = []
        
        img_name_list = os.listdir(os.path.join(test_path,file))
        
        for img_name in img_name_list:
            
            img_list.append(img_name)
        
        for img_name_ in img_list:
            
            if fnmatch(img_name_, '*gt.jpg'):
                gt_path = os.path.join(test_path, file, img_name_)
                
            if fnmatch(img_name_, '*pred.jpg'):
                pred_path = os.path.join(test_path, file, img_name_)
    
        gt, h, w = read_gt_img(gt_path)
        gt = gt[:,:,:,0].squeeze()
        gt = gt * 10 / 255

        pred = read_pred_img(pred_path, h, w)
        pred = pred[:,:,:,0].squeeze()
        pred = pred * 10 / 255
        
        result                  = compute_errors(pred, gt)
        
        # if result["rmse"] <= 0.2:
        #     print(result["rmse"])
        #     print(pred_path)
        
        rmse_l.append(result["rmse"])
        abs_rel_l.append(result["abs_rel"])
        a1_l.append(result["a1"])
        
    
    sum_rmse, sum_a1, sum_abs_rel = 0, 0, 0 
    for item in rmse_l:
        sum_rmse += item
        rmse_mean = sum_rmse/len(rmse_l)

    for item in a1_l:
        sum_a1 += item
        a1_mean = sum_a1/len(a1_l)
        
    for item in abs_rel_l:
        sum_abs_rel += item
        abs_rel_mean = sum_abs_rel/len(abs_rel_l)
    
    print("RMSE_mean:", rmse_mean)
    print("a1_mean:", a1_mean)
    print("abs_rel_mean:", abs_rel_mean)