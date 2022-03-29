# Methodology

## Template matching method:
Template matching is mostly used as object detection method. We have a template image and we need to find where is this in the input image. For this, the sliding window approach is used. In the sliding window approach, we simply slide the template image over the input image (similar to convolution) and compare the overlapping patch. This outputs a grayscale image, where each pixel represents how much does the neighborhood of that pixel match with the template (i.e. the comparison score). From this, we can either select the maximum/minimum (depending on the comparison method used) or use thresholding to select the probable region of interest. **We could** use this approach in our problem and cut components like capacitors, transistor etc. from each template printed circuit board (PCB). Then with prior knowledge of how many of which comoponents should be located we could perform template matching for every cut component, and if it wouldn't be able to find enough matches then it means that there are some components missing. But there are some drawbacks of this approach:
* We always analyze whole image (if our template capacitor is **100x100** and size of our template is **1000x1000** then we obtain output greyscale matching image of the size **901x901** this is number of possible slides of the template through the image) so this introduce quite a big overhead as we need to perform a lot of calculations that are not always necessary.
* Components may be placed in different orientation (vertically, horizontally, with some rotation etc.) so generally we would need separate template for every such variation. 

As an **advantage** of this approach we could accepts robustness on shifts, if we shift whole image 30 pixels to the right, match still be found. However, this also may be drawback as shift of the component by 30 pixels may indicate that it was mounted incorrectly.

To overcome it we propose to compare only corresponding parts of template and inspected image. There are two ways of doing this, **sliding window approach** where we cut windows of some constant size and we compare only windows cut in the exactly same place in both images. And **second one**: We prepare bounding boxes around every area that we want to inspect. This can be done either by previously preparing some anti-template with all defects on it and using different method for preparing boxes or using some adnotation tool and those areas can be checked by some person. Then we compare only previously selected area on both images. With this we have:

* Less computations needed When we have windows 150x150 and our image is 1500x1500 we will perform 100 matching operations for the whole image as before we need to perform 810 000 for one component. When we use second approach with previously prepared boxes it is even more superior as when we have 30 components we only perform 30 matchings.
* We do not need to prepare a lot of templates since we think more area-wise insted of component-wise.

`Using template matching inspected PCB is condidered as defected when at least one checked rectangle returns similarity match that is below some predefined threshold.`

### Limitations of Template matching:
* Images should be aligned as good as possible, since template-matching perform pixel-wise comparison. Even small shift of the image may worsen the performance. Alignment util was created to overcome this.
* Ilumination conditions - as we change them, values of all pixels will either be greater or smaller. If they are different with comparison to the template then of course performance will be worse. To reduce the impact of it one can use [histogram equalization](https://docs.opencv.org/4.5.1/d4/d1b/tutorial_histogram_equalization.html) or [adaptive threshold binaryzation](https://docs.opencv.org/4.5.1/d7/d4d/tutorial_py_thresholding.html).
* Some random noise - during mounting PCB there may be some ash, some little scratches or something like that which also may influance the outcomes, one may use some kind of blurring to neglect it.
`Even though it is possible to somehow reduce impact of badly prepared photo it is very important to prepare some good conditions for making them.`

### Some details
1. **Comparison methods**:
    `At first its better to use methods that are are normalized!`
    * Normalized squared difference (cv2.TM_CCORR_NORMED): We generally subtract pixel-wise and then sum squares of that differences. So here score should be minimized score 0 means perfect match and the bigger score the worse match is.
    * Normalized Cross Correlation (cv2.TM_CCORR_NORMED): We just calculate cross correlation so namely pixel-wise product. Product have such property that when we have big match (either two big positive values or two big negative values) then product is very big positive, but when we have values from different ends then product is big and negative. After normalization we have correlation coefiiciant.
    * TM_CCOEFF_NORMED: It is very similar to previous one but in here we always subtract mean value of the pixels (Expected value) so somehow it is more strictly calculating variances and covariance and correlation coefiiciant. 
    
     `In Equation provided by openCV x,y denotes the center of currently compared part of the image and x',y' are all possible template pixels.`
2. **Additional Padding**: To somehow make this method more robust on bad alignement one can use some zero padding so that we heve more **centers** and a few pixel shift then may be not a problem.
3. **Using mask**: While the patch must be a rectangle it may be that not all of the rectangle is relevant. In such a case, a mask can be used to isolate the portion of the patch that should be used to find the match. Imagine that we need have a capacitor which has circle shape. We always need to cut it as a rectangle but with a mask we can only take into consideration that cirle shape.

For more datails:
* [Open CV documentation](https://docs.opencv.org/3.4/de/da9/tutorial_template_matching.html)
* [Open CV tutorial](https://docs.opencv.org/4.5.2/d4/dc6/tutorial_py_template_matching.html)
* [Open CV Function documentation](https://docs.opencv.org/3.4/df/dfb/group__imgproc__object.html#ga586ebfb0a7fb604b35a23d85391329be)
* [Paper comparing Difference and correlation method](https://www.researchgate.net/publication/301443589_Template_Matching_using_Sum_of_Squared_Difference_and_Normalized_Cross_Correlation)

`Template matching is more complex than differnce but also more robust so one can try at first difference method if it works not got enough try template matching method with either sliding windows`
## Difference method 
This method Directly subtracts(or perform bitwiseXor) the template image from the inspected image. However, subtracting images is not enough, since after it, we will be left with a lot of noise. To remove it one can use median filtering ([suppl1](https://docs.opencv.org/3.4/dc/dd3/tutorial_gausian_median_blur_bilateral_filter.html), [suppl2](https://docs.opencv.org/4.5.2/d4/d13/tutorial_py_filtering.html)) and mathematical morphological processing ([suppl1](https://docs.opencv.org/4.5.2/d9/d61/tutorial_py_morphological_ops.html)). The biggest advantage of this method is the ease of interpretation, when PCB is defected then on the inference image we will see white areas indicating that in this place there are some differences. **Big drawback** is that it has many more parameters to choose compared with template matching. Most of them are about morphologies, how many to perform, what type of kernels  to use, what size of kernels to use etc. 

### Limitations:
* This method is even more sensitive to some shifts. Alignement util was created to overcome it in some extent.
* Ilumination conditions: same problem as in template matching can be overcomed using binaryzation and hisogram equalization.
`Even though it is possible to somehow reduce impact of badly prepared photo it is very important to prepare some good conditions for making them.`

`Using difference method inspected PCB is condidered as defected when sum of all differences is greater than some predefined threshold.`

## Alignement Util
Generally all methods works better as we align template with inspacted image as good as possible. Preparing good station doing photos in constant conditions is the most straigthforward and probably effective step of doing this but it is quite expensive and very hard to prepare perfect station so that all photos are aligned perfectly. Alignemet tool was needed to make analyzis better.
### Detailed description
All we need to perform alignement is homopgraphy matrix, which we apply by performing matrix-vector multipilcation on all pixels in a photo to obtain as good matching as possible. Homography matrix can be found If we know 4 or more corresponding points in the two images by solving system of linear equations. To find those points automatically and describe them we need some keypoints detector. There are 3 most popular: SIFT, SURF, and ORB. We used ORB because SIFT and SURF are patented and if you want to use it in a real-world application, you need to pay a licensing fee. ORB is fast, accurate and license-free. 
If you want to learn more about how ORB work internally:
* [ORB](https://medium.com/data-breach/introduction-to-orb-oriented-fast-and-rotated-brief-4220e8ec40cf)
* [FAST description - Feature points detector used in ORB](https://medium.com/data-breach/introduction-to-fast-features-from-accelerated-segment-test-4ed33dde6d65)
* [BRIEF - feature points descriptior used in ORB](https://medium.com/data-breach/introduction-to-brief-binary-robust-independent-elementary-features-436f4a31a0e6)
* [OpenCV tutorial](https://docs.opencv.org/4.5.1/d1/d89/tutorial_py_orb.html)

After we have keypoints of two images we need to match them. It can be done using [Descriptor Matcher](https://docs.opencv.org/3.4/db/d39/classcv_1_1DescriptorMatcher.html). To measure distance between two keypoints we use [Hamming distance](https://en.wikipedia.org/wiki/Hamming_distance). Not all matches will be good enough so we can sort them and filter the worst ones that theoretically may worse performance.

Having keypoints matched we can calculate homography matrix. We have seen that there can be some possible errors while matching which may affect the result. To solve this problem, algorithm uses [RANSAC](https://en.wikipedia.org/wiki/Random_sample_consensus#:~:text=Random%20sample%20consensus%20(RANSAC)%20is,as%20an%20outlier%20detection%20method.) to reject outliers (points that are hardly matched). After than we can finally apply warpPerspective method.

Advantages:
* ORB is scale invariant
* Rotation invariant
* Resistant to noise
* Inspected image can be warped to have exactly the same shape as template, so this introduce robustness of sizes.
* Station that makes photos doesn't have to be perfect

Only disadvantage is that aligner is the most time consuming util.

`Aligner is quite powerfull but it won't repair photos that are taken very badly!`

## Box generator Util
This util is able to create bounding boxes for template matching using difference method. One might say why we need this as we're using other method here. It is done as time performance of template matching is much better using defined areas and also it improves performance of this method. Bad part is that we need some anti-template (template with all possible defects created) prapared so that difference method can identify all possible boxes in one shot. 
The idea is quite easy: at first we use difference method and then using result image we find its [contours](https://docs.opencv.org/3.4/d4/d73/tutorial_py_contours_begin.html) and then [bounding boxes](https://docs.opencv.org/3.4/dd/d49/tutorial_py_contour_features.html). We then save them in txt file (db also could be used) so that they are easily accessible later on.
Possibly we could use this util also with adnotation tool.

Advantages:
* Can boost template matching method a lot


## ROI Cropper Util
In some situations it may be hard to always take photos of PCBs without any background. Some boards may be smaller some may be bigger and than some zooming by camera should be performed to take photo only of the board. Presence of the background may harm performance of our methods, as it can introduce additionall noise. It is possible to get rid of the Background using this util.

Basically it can do it in two ways:
1. Using [Edge detection](https://docs.opencv.org/4.5.1/da/d22/tutorial_py_canny.html).
2. Using some color masking. 

All methods create some kind of binary mask where white lines defines our region of interest. What we do is to sum up image with respect to x and y axis and then select first points from left, right, top and bottom in which sum of white points is above defined threshold. Then we just crop the image based on these points.

So this util can be helpful in some situations. But unfortunately there are some parameters that need to be defined e.g. color that background has to know which should be filtered.

## Ways of improving performance
1. Do not load all: keypoints, templates, bounding boxes and all stuff that possibly can be reused during inspection and save them in dictonaries or arrays for fast access. This has one limitation available memory. If there would be very small amount of memory available and we were to read about 1000 templates with all keypoints and bounding boxes it may crash the system. So it is possible to create some kind of cache memory that will store some reference to a template counter and if template is not referenced for a long time (1000) inspection then it is cleaned from memory.
2. Ways of saving inference. The most costly operations are these connected with reading and saving images. If it is really needed outcomes of inspection may be represented in different ways (result of tamplate matching saved as txt file with boxes where we had low similarit instead of saving whole images with plotted boxes).
3. Not using aligner in the pipeline will boost the time performance greatly, but if the photo station does not make perfect photos the inference may be poorer.
4. Changing parameters in methods like, template_size in template matching, or erosion configuration or binary thresholding config will result in some small boost in time but may also lead to worse performance in inspection. If really some boost is needed one could think about it.

`Computing keypoints in aligner is the function with highest time complexity, so with limited memory, at least try to store only those as it will give big boost!`