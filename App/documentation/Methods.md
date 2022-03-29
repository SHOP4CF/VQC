## VQC Methods

All methods are implemented using `method.py` blueprint. All must have three methods implemented:
* `__init__` - used only to initialize all parameters
* `set_params` - used only to update parameters and not initialize object once again
* `apply` - used to perform analysis, return decision and save inference for later inspection
`template matching` has one additionall function but this is used only inside that class for readability

### Descriptions of methods:
* `difference` - perform bitwiseXor on two grayscale images (template - inspected). Two methods available: first uses more complex binaryzation method that somehow may reduce influence of illumination [(`cv.adaptiveThreshold`)](https://docs.opencv.org/4.5.1/d7/d4d/tutorial_py_thresholding.html) second one just perform bitwiseXor and then do some easy thresholding with predefined values. After that some [morphological operators](https://docs.opencv.org/4.5.2/d9/d61/tutorial_py_morphological_ops.html) like `erosion`, `closing`, `opening` are performed to get rid of noise and leave only places where difference was biggest **Easiest to comprehend method and is quite fast**.
* `template_matching` - perform [`cv.matchTemplate`](https://docs.opencv.org/3.4/de/da9/tutorial_template_matching.html), again two ways of doing this. First is to slide using some constant window (we slide through whole image creating squares with predefined size) and we compare same square of template with same square of inspected image (**Drawback of that method is that sometimes we perform not needed checking as we check square containing no elements or some element may be in very small amounts in few squares which may worse the performance**). Alternatively better option is to have predefined boxes (places where comoponents are) for every template and compare only those. **For getting boxes we implemented `box_generator` util that need kind of `anti template` so this is a image of template but with all components that need to be checked taken out of the pcb. Alternatively boxes may be also prepared by human using some adnotation tool.** 
* k_means - alternative version of difference method, we perform segmentation of the difference (template - inspected) using [`k_means`](https://docs.opencv.org/4.5.2/d1/d5c/tutorial_py_kmeans_opencv.html) and pixels with big difference go to one cluster whereas pixels with good match goes to another cluster. **This method unfortunately is quite slow but may work good so this may be an alternative for previous methods if time of analysis is not so important**

**After inference is performed we save outcomes in earlier predefined folders**

 **Methods hardly depends on the good alignement of the image this problem is solved using `aligner` util and also on ilummination conditions which is solved using [`equalize_hist`](https://docs.opencv.org/4.5.1/d4/d1b/tutorial_histogram_equalization.html)**.