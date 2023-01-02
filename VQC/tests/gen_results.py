import os
import cv2
import sys
sys.path.append('..')
from TuningMethods.functions import aligner
from tqdm import tqdm


IMG_DIR = 'imgs'
RESULT_DIR = 'results'

for dir in tqdm(os.listdir(IMG_DIR)):
    img_path = os.path.join(IMG_DIR, dir)

    valid = cv2.imread(os.path.join(img_path, 'valid.png'), 0)
    defect = cv2.imread(os.path.join(img_path, 'defect.png'), 0)

    valid = cv2.equalizeHist(valid)
    defect = cv2.equalizeHist(defect)

    result, _ = aligner(valid, defect, matcher_name='flann_index_kdtree')

    cv2.imwrite(os.path.join(RESULT_DIR, '{}-result.png'.format(dir)), result)
