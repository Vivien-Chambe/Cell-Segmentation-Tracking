import cv2 as cv
import numpy as np
from sklearn.metrics import f1_score
import sys

def evaluate(pred_images, true_images):
    # à écrire - une fonction qui permet d'evaluer la performance d'un algorithme de threshold
    # sur un ensemble d'images "déjà validés"
    
    # INPUT :
    # pred_images : a list of predicted binary images
    # true_images : a list of true binary images
    # OUTPUT :
    # f1 : the F1-score of the thresholding algorithm
    
    pred_labels = []
    true_labels = []
    
    # convert the predicted and true images to binary labels
    for pred_image, true_image in zip(pred_images, true_images):
        pred_label = np.where(pred_image.flatten() > 0, 1, 0)
        true_label = np.where(true_image.flatten() > 0, 1, 0)
        pred_labels.append(pred_label)
        true_labels.append(true_label)
    
    assert np.shape(true_labels) == np.shape(pred_labels) # error : True and predicted labels do not have the same shape
    assert len(np.unique(true_labels)) == 2 # error : labels are not binary
    
    # compute the F1-score of the thresholding algorithm
    f1 = f1_score(np.concatenate(true_labels), np.concatenate(pred_labels), average='macro')
    return f1


# load the input image
initial = cv.imread('images/puit03/t000.tif')

if initial is None:
    sys.exit("Could not read the image.")
#print(initial)

# grayscale
img = cv.cvtColor(initial, cv.COLOR_BGR2GRAY)

# create a validation set of images
val_initial = cv.imread('images/puit03/t029.tif')
val_images = cv.cvtColor(val_initial, cv.COLOR_BGR2GRAY)
#val_images = [cv.imread(r'images/puit03/t029.tif'), cv.imread(r'images/puit03/t028.tif'), cv.imread(r'images/puit03/t027.tif')]

if val_images is None:
    sys.exit("Could not read the images.")
#print(val_images)

# define a range of kernel sizes and sigma values to test
kernel_sizes = range(3,11,2)
sigmas = np.linspace(0,3,11)

# loop over all combinations of kernel sizes and sigma values
best_kernel_size = None
best_sigma = None
best_accuracy = 0

for kernel_size in kernel_sizes:
    for sigma in sigmas:
        # apply Gaussian blur to the input image
        blurred_img = cv.GaussianBlur(img, (kernel_size, kernel_size), sigma)
        # perform thresholding on the blurred image
        thresh_img, binary_img = cv.threshold(blurred_img, 0, 255, cv.THRESH_BINARY)
        # evaluate the performance of the thresholding algorithm on the validation set
        accuracy = evaluate(thresh_img, val_images)
        # keep track of the best kernel size and sigma values
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_kernel_size = kernel_size
            best_sigma = sigma

# apply the best Gaussian blur to the input image
blurred_img = cv.GaussianBlur(img, (best_kernel_size, best_kernel_size), best_sigma)
# perform thresholding on the blurred image using the optimal kernel size
thresh_img, binary_img = cv.threshold(blurred_img, 0, 255, cv.THRESH_BINARY)

cv.imshow('Input', img)
cv.imshow('Output', thresh_img)
cv.waitKey(0)
cv.destroyAllWindows()