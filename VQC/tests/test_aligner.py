import os
import cv2
from skimage.metrics import structural_similarity as ssim
from TuningMethods.functions import aligner
import pytest

IMG_PATH = os.path.join("tests", "imgs")
RESULTS_PATH = os.path.join("tests", "results")
THRESHOLD = 0.8


def load_data(dir_name):
    valid_path = os.path.join(IMG_PATH, dir_name, 'valid.png')
    defected_path = os.path.join(IMG_PATH, dir_name, 'defect.png')
    expected_path = os.path.join(RESULTS_PATH,
                                 '{}-result.png'.format(dir_name))

    print(f"\n\nvalid_path:\t{valid_path}"
          f"\ndefected_path:\t{defected_path}"
          f"\nexpected_path:\t{expected_path}\n\n")

    valid = cv2.imread(valid_path, 0)
    defected = cv2.imread(defected_path, 0)
    expected = cv2.imread(expected_path, 0)

    valid = cv2.equalizeHist(valid)
    defected = cv2.equalizeHist(defected)

    return valid, defected, expected


def _test(valid, defected, expected, matcher_name):
    result, _ = aligner(valid, defected, matcher_name=matcher_name)
    assert ssim(result, expected) > THRESHOLD


@pytest.mark.aligner
class Test1:
    valid, defected, expected = load_data('1')

    def test_flann_linear(self):
        _test(self.valid, self.defected, self.expected, 'flann_index_linear')

    def test_flann_kdtree(self):
        _test(self.valid, self.defected, self.expected, 'flann_index_kdtree')

    def test_flann_kmeans(self):
        _test(self.valid, self.defected, self.expected, 'flann_index_kmeans')


@pytest.mark.aligner
class Test2:
    valid, defected, expected = load_data('2')

    def test_flann_linear(self):
        _test(self.valid, self.defected, self.expected, 'flann_index_linear')

    def test_flann_kdtree(self):
        _test(self.valid, self.defected, self.expected, 'flann_index_kdtree')

    def test_flann_kmeans(self):
        _test(self.valid, self.defected, self.expected, 'flann_index_kmeans')


@pytest.mark.aligner
class Test3:
    valid, defected, expected = load_data('3')

    def test_flann_linear(self):
        _test(self.valid, self.defected, self.expected, 'flann_index_linear')

    def test_flann_kdtree(self):
        _test(self.valid, self.defected, self.expected, 'flann_index_kdtree')

    def test_flann_kmeans(self):
        _test(self.valid, self.defected, self.expected, 'flann_index_kmeans')
