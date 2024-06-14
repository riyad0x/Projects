from pyimagesearch import transform
from pyimagesearch import imutils
from scipy.spatial import distance as dist
import itertools
import math
import cv2
import os
import numpy as np


class DocScanner(object):

    def __init__(self, MIN_QUAD_AREA_RATIO=0.25, MAX_QUAD_ANGLE_RANGE=40):
        # this determines the min area ratio for a contour to be suposed valid, the larger is the ratio, the more the app accepts only larger contours.
        self.MIN_QUAD_AREA_RATIO = MIN_QUAD_AREA_RATIO
        # this attribute is used to detemine the mas angles of a contour to be valid
        self.MAX_QUAD_ANGLE_RANGE = MAX_QUAD_ANGLE_RANGE

    # this function accpets only corners that are far enough from each other and removes all other one that are very close (very close angles), it uses a minimum distance to validate corners.
    def filter_corners(self, corners, min_dist=20):
        # this function is used to check if a corner is far from already filered corners
        def predicate(already_filtered_corners, corner):
            return all(dist.euclidean(representative, corner) >= min_dist for representative in already_filtered_corners)
        filtered_corners = []
        for c in corners:
            # this is the place where the corners are compared
            if predicate(filtered_corners, c):
                filtered_corners.append(c)
        return filtered_corners

    # Calculate the angle between two vectors
    def angle_between_vectors_degrees(self, u, v):
        return np.degrees(math.acos(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))))

    # here we used the angle_between_vectors_degrees function to calculale the angle between two vetors formed by tree points, this is going to help us know the orientation and alignment of corners.
    def get_angle(self, p1, p2, p3):
        a = np.radians(np.array(p1))
        b = np.radians(np.array(p2))
        c = np.radians(np.array(p3))
        avec = a - b
        cvec = c - b
        return self.angle_between_vectors_degrees(avec, cvec)

    # this function is used to calculate the angeles range, which means taking a four corners contour and finding the orientation and distance between angles to find a very good rectangular shape for the contour
    def angle_range(self, quad):
        tl, tr, br, bl = quad
        ura = self.get_angle(tl[0], tr[0], br[0])
        ula = self.get_angle(bl[0], tl[0], tr[0])
        lra = self.get_angle(tr[0], br[0], bl[0])
        lla = self.get_angle(br[0], bl[0], tl[0])
        angles = [ura, ula, lra, lla]
        return np.ptp(angles)

    # Determine all rectangular probable contours by relaying on corners alignment and vectors orientation
    def get_corners(self, img):
        # Check if image is BGR, to avoid any erros with colors
        if img.ndim == 3 and img.shape[2] == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        # apply the canny effect to trace all edges on the gray image with intervall for valid pixels [50, 150]
        edges = cv2.Canny(gray, 50, 150)

        # return all lines that can be drawn around detected edges whith a threshold of 100 and the gap between lines should not go beyond 10
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180,
                                threshold=100, minLineLength=50, maxLineGap=10)

        corners = []
        if lines is not None:
            # this squeez() function removes unnecessary noise or falsy lines detected by the houghlinesP algorithm which return a for items array for each line.
            lines = lines.squeeze()

            horizontal_lines_canvas = np.zeros(img.shape[:2], dtype=np.uint8)
            vertical_lines_canvas = np.zeros(img.shape[:2], dtype=np.uint8)

            # loop over the lines to separat horizontal from vertical ones
            for line in lines:
                x1, y1, x2, y2 = line

                if abs(x2 - x1) > abs(y2 - y1):  # find horizental lines : xf >> xi & yf ~~ yi
                    (x1, y1), (x2, y2) = sorted(
                        ((x1, y1), (x2, y2)), key=lambda pt: pt[0])
                    cv2.line(horizontal_lines_canvas, (max(x1 - 5, 0), y1),
                             (min(x2 + 5, img.shape[1] - 1), y2), 255, 2)
                else:
                    (x1, y1), (x2, y2) = sorted(  # for vertical lines, yf >> yi & xf ~~ xi
                        ((x1, y1), (x2, y2)), key=lambda pt: pt[1])
                    cv2.line(vertical_lines_canvas, (x1, max(y1 - 5, 0)),
                             (x2, min(y2 + 5, img.shape[0] - 1)), 255, 2)

            # finding contours around horizontal lines and sorting them based on their length in order to pic the largest contour from available contours.
            (contours, _) = cv2.findContours(horizontal_lines_canvas,
                                             cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            contours = sorted(contours, key=lambda c: cv2.arcLength(
                c, True), reverse=True)[:2]  # we just pic the top 2 contours from all available ones, because the document take the most of the image so it has the largest contour

            horizontal_lines_canvas = np.zeros(img.shape[:2], dtype=np.uint8)

            for contour in contours:
                # changes the shape of the contour from(a, b, c) t0 (a, c) in order to make it possible to calculate the amin, aax and average.
                contour = contour.reshape((contour.shape[0], contour.shape[2]))
                # find the top left coord of the contour
                min_x = np.amin(contour[:, 0], axis=0) + 2
                # find the top left coord of the contour
                max_x = np.amax(contour[:, 0], axis=0) - 2
                # find all points that have xmin as coord and take the y and calculate the average to use it for the left vect
                left_y = int(np.average(contour[contour[:, 0] == min_x][:, 1]))
                right_y = int(np.average(  # find the averyage y for the right vect
                    contour[contour[:, 0] == max_x][:, 1]))
                # add the found coords of corners to the corners list
                corners.append((min_x, left_y))
                corners.append((max_x, right_y))  # the same thing
                # draw lines between the two corners in order to make the contour
                cv2.line(horizontal_lines_canvas,
                         (min_x, left_y), (max_x, right_y), 1, 1)

            # we repeat the same process for vertical lines found by the houghlinesP algorithm
            (contours, _) = cv2.findContours(vertical_lines_canvas,
                                             cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            contours = sorted(contours, key=lambda c: cv2.arcLength(
                c, True), reverse=True)[:2]

            vertical_lines_canvas = np.zeros(img.shape[:2], dtype=np.uint8)

            for contour in contours:
                contour = contour.reshape((contour.shape[0], contour.shape[2]))
                min_y = np.amin(contour[:, 1], axis=0) + 2
                max_y = np.amax(contour[:, 1], axis=0) - 2
                top_x = int(np.average(contour[contour[:, 1] == min_y][:, 0]))
                bottom_x = int(np.average(
                    contour[contour[:, 1] == max_y][:, 0]))
                corners.append((top_x, min_y))
                corners.append((bottom_x, max_y))
                cv2.line(vertical_lines_canvas, (top_x, min_y),
                         (bottom_x, max_y), 1, 1)

            corners_y, corners_x = np.where(
                horizontal_lines_canvas + vertical_lines_canvas == 2)
            corners += zip(corners_x, corners_y)

        # filer all the found corners to remove small contours and near corners and reduce the probabilty of errors
        corners = self.filter_corners(corners)
        return corners

    # check if the contour is valid by checking that it is with 4 corners, its area is begger than the min and the angle range is valid
    def is_valid_contour(self, cnt, IM_WIDTH, IM_HEIGHT):
        return (
            len(cnt) == 4
            and cv2.contourArea(cnt) > IM_WIDTH * IM_HEIGHT * self.MIN_QUAD_AREA_RATIO
            and self.angle_range(cnt) < self.MAX_QUAD_ANGLE_RANGE
        )

    # this function return the largest contour in the image which is screencnt, by
    def get_contour(self, rescaled_image):
        MORPH = 9
        CANNY = 84
        IM_HEIGHT, IM_WIDTH, _ = rescaled_image.shape
        gray = cv2.cvtColor(rescaled_image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (MORPH, MORPH))
        dilated = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        # we have used the previous code to reduce noise and fill all gaps the image(if there is white areas on the text)
        edged = cv2.Canny(dilated, 0, CANNY)
        # using get_corners function to find the corners of the rescaled image
        test_corners = self.get_corners(edged)
        approx_contours = []
        if len(test_corners) >= 4:  # if we find more than 4 corners for element, we take every possible 4 combinations of those corners and work on them
            quads = []
            # making the combinations
            for quad in itertools.combinations(test_corners, 4):
                points = np.array(quad)
                # we order the points to take the image in the right orientation
                points = transform.order_points(points)
                # transform the combination to a numpy array
                points = np.array([[p] for p in points], dtype="int32")
                quads.append(points)
            # sort the combinations based on their area and take only the top 4
            quads = sorted(quads, key=cv2.contourArea, reverse=True)[:5]
            # take the farest corners from each other(angle range)
            quads = sorted(quads, key=self.angle_range)

            # the contour with largest areat and best angle range
            approx = quads[0]
            if self.is_valid_contour(approx, IM_WIDTH, IM_HEIGHT):
                approx_contours.append(approx)  # take it if valid

        # now we find the contours of edged image
        (cnts, hierarchy) = cv2.findContours(
            edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]
        for c in cnts:
            approx = cv2.approxPolyDP(c, 80, True)
            if self.is_valid_contour(approx, IM_WIDTH, IM_HEIGHT):
                approx_contours.append(approx)
                break  # when finding the first valid contour with all conditions stop loop over contours

        if not approx_contours:
            TOP_RIGHT = (IM_WIDTH, 0)
            BOTTOM_RIGHT = (IM_WIDTH, IM_HEIGHT)
            BOTTOM_LEFT = (0, IM_HEIGHT)
            TOP_LEFT = (0, 0)
            # if no approximation was found, take the originla image and order it this way
            screenCnt = np.array(
                [[TOP_RIGHT], [BOTTOM_RIGHT], [BOTTOM_LEFT], [TOP_LEFT]])
        else:
            # if found, take the largest contour based on its area.
            screenCnt = max(approx_contours, key=cv2.contourArea)
        return screenCnt.reshape(4, 2)

    def scan(self, image_path):
        RESCALED_HEIGHT = 500.0
        OUTPUT_DIR = './scans'

        image = cv2.imread(image_path)
        assert image is not None

        # the ration is used to maintain the aspect ration of the original image in order to prevent any loss
        ratio = image.shape[0] / RESCALED_HEIGHT
        original = image.copy()
        # we rescaled the image in order to make easy to be processed
        rescaled_image = imutils.resize(image, height=int(RESCALED_HEIGHT))

        screenCnt = self.get_contour(rescaled_image)
        # warp the image, means crop the image using the contour we found and respecting the ratio
        warped = transform.four_point_transform(original, screenCnt * ratio)
        # all the following functions are used to enhance the quality of the warped image
        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        sharpen = cv2.GaussianBlur(gray, (0, 0), 3)
        sharpen = cv2.addWeighted(gray, 1.5, sharpen, -0.5, 0)
        # convert the image to black and white version preparing for text extraction
        thresh = cv2.adaptiveThreshold(
            sharpen, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 15)
        basename = os.path.basename(image_path)
        result_path = OUTPUT_DIR + '/' + basename
        cv2.imwrite(result_path, thresh)
