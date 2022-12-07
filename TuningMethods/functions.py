import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

matchers = {
    'bruteforce': cv.DESCRIPTOR_MATCHER_BRUTEFORCE,
    'bruteforce_hamming': cv.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING,
    'bruteforce_hamminglut': cv.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMINGLUT,
    'bruteforce_l1': cv.DESCRIPTOR_MATCHER_BRUTEFORCE_L1,
    'bruteforce_sl2': cv.DESCRIPTOR_MATCHER_BRUTEFORCE_SL2,

    'flann_index_linear': 0,
    'flann_index_kdtree': 1,
    'flann_index_kmeans': 2,
    'flann_index_composite': 3,
    'flann_index_kdtree_single': 4,
    'flann_index_hierarchical': 5}


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
        template,
        img,
        max_features=250,
        good_match_percent=0.8,
        matcher_name='flann_index_kdtree',
        plot_keypoints=False
):
    im1Gray = cv.cvtColor(img,
                          cv.COLOR_BGR2GRAY) \
        if len(img.shape) == 3 else img

    templateGray = cv.cvtColor(template,
                               cv.COLOR_BGR2GRAY) \
        if len(template.shape) == 3 else template

    if matcher_name.startswith('bruteforce'):
        # Detect features and compute descriptors.
        orb = cv.ORB_create(max_features)

        keypoints1, descriptors1 = orb.detectAndCompute(im1Gray, None)
        keypoints2, descriptors2 = orb.detectAndCompute(templateGray, None)

        # Match features
        matcher = cv.DescriptorMatcher_create(matchers[matcher_name])
        matches = list(matcher.match(descriptors1, descriptors2, None))
    elif matcher_name.startswith('flann'):
        sift = cv.SIFT_create()

        keypoints1, descriptors1 = sift.detectAndCompute(im1Gray, None)
        keypoints2, descriptors2 = sift.detectAndCompute(templateGray, None)

        # Specify algorithm used and various parameters
        index_params = dict(algorithm=matchers[matcher_name], trees=5)

        matcher = cv.FlannBasedMatcher(index_params, {})

        matches = matcher.knnMatch(descriptors1, descriptors2, 2)
        matches = [m1 for (m1, m2) in matches
                   if m1.distance < 0.7 * m2.distance]
    else:
        print('Incorrect matcher name')
        return

    # Sort matches by score
    matches.sort(key=lambda x: x.distance, reverse=False)

    # Remove bad matches
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

    # Find homography
    h, _ = cv.findHomography(points1, points2, cv.RANSAC)

    # Use homography
    height, width = template.shape[0], template.shape[1]
    im1Reg = cv.warpPerspective(img, h, (width, height))

    # Plot keypoints
    if plot_keypoints:
        img_keypoints = cv.drawMatches(im1Gray,
                                       keypoints1,
                                       templateGray,
                                       keypoints2,
                                       matches,
                                       None, None)

        plt.figure(figsize=(10, 10))
        plt.imshow(img_keypoints, cmap='gray')
        plt.axis('off')
        plt.title(matcher_name)
        plt.show()

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
    For this to work a little bit better, after creating a mask we can try to
    do some Morphological operations
    """
    mask = cv.Canny(image=img,
                    threshold1=canny_thresh_low,
                    threshold2=canny_thresh_top)

    # cv.imwrite(f"outcome/mask1.png", mask)
    sumX = np.sum(
        mask, axis=0
    )  # collapsing rows, values of pixels from columns are summed
    indicesX = np.argwhere(sumX > thresh_border)
    x1 = indicesX[x1_i][
        0
    ]  # getting x1_i-th value from the left as a top left x coordinate
    x2 = indicesX[x2_i][0]

    sumY = np.sum(mask, axis=1)  # collapsing columns, rows are summed
    indicesY = np.argwhere(sumY > thresh_border)  # the same story as above
    y1 = indicesY[y1_i][0]
    y2 = indicesY[y2_i][0]

    cropped = img[y1: y2 + 1, x1: x2 + 1]  # cropping the image
    # cv.imwrite(f"outcome/cropped1.png", cropped)
    return cropped
