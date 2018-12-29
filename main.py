#!/usr/bin/env python
import tempfile
import sys
import os
import cv2
import rect
import imutils
import numpy as np

class PageRecognizer(object):
    """This class recognizes a page from the give image"""
    WIDTH = 1000
    HEIGHT = 1414
    BLUR_RADIUS = 20

    def __init__(self, image_path=None):
        self.im_orig = cv2.imread(image_path)
        height = self.im_orig.shape[0]
        width = self.im_orig.shape[1]
        if height < width:
            self.rotate_anticlockwise_90()

    def rotate_anticlockwise_90(self):
        self.im_orig = imutils.rotate_bound(self.im_orig, 90)

    def generate_highcontrast(self):
        self.im_gray = cv2.cvtColor(self.im_orig, cv2.COLOR_BGR2GRAY)
        # alpha = 0
        # beta = -20
        # self.im_highcontrast = cv2.convertScaleAbs(self.im_gray, alpha=alpha, beta=beta)
        ret, th1 = cv2.threshold(self.im_gray, 100, 255, cv2.THRESH_BINARY)
        self.im_highcontrast = th1


    def generate_edged(self):
        self.generate_highcontrast()
        blurred = cv2.GaussianBlur(self.im_highcontrast, (5, 5), 0)
        self.im_edged = cv2.Canny(blurred, 0, 100)


    def find_contours(self):
        self.generate_edged()
        _a, contours, _b = cv2.findContours(self.im_edged.copy(), cv2.RETR_LIST,
                                            cv2.CHAIN_APPROX_NONE)
        return sorted(contours, key=cv2.contourArea, reverse=True)

    def extract_page(self):
        # We only need the largest contour
        contour = self.find_contours()[0]
        p = cv2.arcLength(contour, True)
        target = cv2.approxPolyDP(contour, 0.1 * p, True)
        approx = rect.rectify(target)

        pts2 = np.float32(
            [[0, 0], [self.WIDTH, 0], [self.WIDTH, self.HEIGHT], [0, self.HEIGHT]])
        M = cv2.getPerspectiveTransform(approx, pts2)
        self.im_page = cv2.warpPerspective(self.im_orig, M, (self.WIDTH, self.HEIGHT))

        # crop the page
        self.im_page = self.im_page[int(60/2):int(2735/2),
                                    int(65/2):int(1935/2)]

        # Black and white
        self.im_page_bw = cv2.cvtColor(self.im_page, cv2.COLOR_BGR2GRAY)

    def process_page(self):
        # blurred = cv2.GaussianBlur(
            # self.im_page, (self.BLUR_RADIUS, self.BLUR_RADIUS), 0)
        if not (hasattr(self, "im_page_bw") and self.im_page_bw):
            self.extract_page()
        ret,self.im_thresh1 = cv2.threshold(self.im_page_bw,127,255,cv2.THRESH_BINARY)
        ret,self.im_thresh2 = cv2.threshold(self.im_page_bw,127,255,cv2.THRESH_BINARY_INV)
        ret,self.im_thresh3 = cv2.threshold(self.im_page_bw,127,255,cv2.THRESH_TRUNC)
        ret,self.im_thresh4 = cv2.threshold(self.im_page_bw,127,255,cv2.THRESH_TOZERO)
        ret,self.im_thresh5 = cv2.threshold(self.im_page_bw,127,255,cv2.THRESH_TOZERO_INV)



    def _get_image_list(self):
        img_list = []
        for key, value in self.__dict__.items():
            if key.startswith("im_"):
                img_list.append((key, value))

        return img_list

    def show_images(self):
        for key, value in self._get_image_list():
            if value is not None:
                cv2.imshow('%s.jpg' % key, value)
        while True:
            cv2.waitKey(0)

    def write_images(self):
        os.system("mkdir out")
        for key, value in self._get_image_list():
            if value is not None:
                cv2.imwrite('out/%s.jpg' % key, value)

class ImageScanner(object):

    @classmethod
    def download_and_scan(cls, href, display=False):
        with tempfile.TemporaryDirectory() as dirpath:
            os.system("cd %s" % dirpath)
            os.system("wget %s -O infile.jpg" % href)
            page_recognizer = PageRecognizer("./infile.jpg")
            page_recognizer.process_page()
            if display:
                page_recognizer.show_images()


def main():
    url = sys.argv[1]
    display = False
    if len(sys.argv) > 2:
        display = sys.argv[2]
    ImageScanner.download_and_scan(url, display)

if __name__ == "__main__":
    main()
