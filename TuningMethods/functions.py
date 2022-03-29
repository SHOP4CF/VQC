import cv2 as cv
import numpy as np
import random
import matplotlib.pyplot as plt
import copy


def get_keypoints(template, max_features=250):
    templateGray = (
        cv.cvtColor(template, cv.COLOR_BGR2GRAY)
        if len(template.shape) == 3
        else template
    )
    orb = cv.ORB_create(max_features)
    keypoints, descriptors = orb.detectAndCompute(templateGray, None)
    return keypoints, descriptors


def aligner(
    template=None,
    img=None,
    max_features=250,
    good_match_percent=0.8,
    keypoints_dict={},
    template_id=1,
):
    if template is not None and img is not None:
        """Keypointsy dla tamplate zapisane wczesniej"""
        im1Gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        templateGray = (
            cv.cvtColor(template, cv.COLOR_BGR2GRAY)
            if len(template.shape) == 3
            else template
        )

        # Detect features and compute descriptors.
        orb = cv.ORB_create(max_features)
        keypoints1, descriptors1 = orb.detectAndCompute(im1Gray, None)
        """If we have done this template already then we will use it, we could also try to save those in a file but what 
        if they've changed templates, or maybe we save all templates in a file before every start. But this will be very hard
        as keypoints are some kind of Object that openCv creates so I think the only option is to remember them """
        if template_id in keypoints_dict:
            keypoints2, descriptors2 = keypoints_dict[template_id]
        else:
            keypoints2, descriptors2 = orb.detectAndCompute(templateGray, None)
            keypoints_dict[template_id] = (keypoints2, descriptors2)

        # Match features
        matcher = cv.DescriptorMatcher_create(cv.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
        matches = matcher.match(descriptors1, descriptors2, None)

        # Sort matches by score
        matches.sort(key=lambda x: x.distance, reverse=False)

        # remove bad matches
        numGoodMatches = int(len(matches) * good_match_percent)
        matches = matches[:numGoodMatches]

        # Extract location of good matches
        points1 = np.zeros((len(matches), 2), dtype=np.float32)
        points2 = np.zeros((len(matches), 2), dtype=np.float32)

        for i, match in enumerate(matches):
            # print(match.queryIdx, match.trainIdx)
            # print(keypoints1[match.queryIdx].pt)
            points1[i, :] = keypoints1[match.queryIdx].pt
            points2[i, :] = keypoints2[match.trainIdx].pt

        # find homography
        h, mask = cv.findHomography(points1, points2, cv.RANSAC)

        # use homography
        height, width = template.shape[0], template.shape[1]
        im1Reg = cv.warpPerspective(img, h, (width, height))

        return im1Reg, h


def cropper1(
    img,
    x1_i=0,
    x2_i=-1,
    y1_i=0,
    y2_i=-1,
    canny_thresh_low=100,
    canny_thresh_top=180,
    thresh_border=28000,
):
    """
    For this to work a little bit better, after creating a mask we can try to do some Morphological operations
    """
    mask = cv.Canny(image=img, threshold1=canny_thresh_low, threshold2=canny_thresh_top)

    # cv.imwrite(f"outcome/mask1.png", mask)
    sumX = np.sum(
        mask, axis=0
    )  # collapsing rows, values of pixels from columns are summed
    indicesX = np.argwhere(sumX > thresh_border)
    x1 = indicesX[x1_i][
        0
    ]  # getting x1_i-th value from the left as a top left x coordinate
    x2 = indicesX[x2_i][0]

    sumY = np.sum(mask, axis=1)  # collapsing columns, rowss are summed
    indicesY = np.argwhere(sumY > thresh_border)  # the same story as above
    y1 = indicesY[y1_i][0]
    y2 = indicesY[y2_i][0]

    cropped = img[y1 : y2 + 1, x1 : x2 + 1]  # cropping the image
    # cv.imwrite(f"outcome/cropped1.png", cropped)
    return cropped
