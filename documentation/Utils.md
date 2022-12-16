## VQC Utils

All Utils are implemented using `util.py` blueprint. All must have three methods implemented:
* `__init__` - used only to initialize all parameters
* `set_params` - used only to update parameters and not initialize object once again
* `apply` - used to perform some task, returns either transformed image (`aligner`, `roi_cropped`) or boxes for template_matching (`box_generator`)

### Description of utils:
* `Aligner` - Perform image alignement so that the matching is much better, it detects keypoints of the image and try to put them in the same place on the warped image. It repairs some rotations, shift or perspective changes. **Image returned has the same size as template so that methods can be used afterwards it**. Sometimes when images differ a lot in all axes and perspective then aligner may create some black boundaries on warped image that may couse some errors, it may be solved using **roi_cropper util**. Two most important methods that build Aligner: [`ORB`](https://docs.opencv.org/4.5.1/d1/d89/tutorial_py_orb.html) and [`warpPerspective`](https://docs.opencv.org/3.4/da/d54/group__imgproc__transform.html#gaf73673a7e8e18ec6963e3774e6a94b87)
* `roi_cropper` - removes background from the image leaving only pcb. Works based on some color mask or edge detection. Currently method is not used but if it is not possible to make picture without a background and this background in some way influence the outcomes it may be cropped easily.
* `box_generator` - Util that generates bounding boxes in which components should be placed. Those boxes can be used by `template_matching` to boost its performance and efficiency. This method needs `anti-template` (template with all components taken off) and is based on difference method then it calculates [contours](https://docs.opencv.org/3.4/d4/d73/tutorial_py_contours_begin.html#:~:text=Contours%20can%20be%20explained%20simply,and%20object%20detection%20and%20recognition.&text=In%20OpenCV%2C%20finding%20contours%20is,white%20object%20from%20black%20background.) and then makes bounding boxes based on them.  **Why not to use only difference method then? When we have predefined boxes template matching is the fastest method and the most accurate** 